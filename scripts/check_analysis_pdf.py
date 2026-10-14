"""Read-only PDF/JSON/CSV acceptance checks; requires optional pymupdf QA tooling."""

import argparse
import csv
import json
import re
from pathlib import Path

import pymupdf

from taketwo.dataset.schema import content_hash
from taketwo.insights.contracts import ComparativeReport


def compact(text):
    return "".join(text.split())


def native_intervals(report, item):
    """Independently recover the existing replay bounds; never synchronize clocks."""
    group = next((g for g in report.groups if g.id == item.evidence_id), None)
    if group:
        return [(group.start_s, group.end_s)]
    anomaly = next((a for a in report.anomalies if a.id == item.evidence_id), None)
    segment = next((s for s in report.segments if s.id == item.evidence_id), None)
    if anomaly:
        segment = next(
            (
                s
                for s in report.segments
                if s.kind == "word" and s.token_start == anomaly.before_token_index + 1
            ),
            None,
        )
        if not segment:
            return [
                (anomaly.before_word.start_s, anomaly.before_word.end_s),
                (anomaly.after_word.start_s, anomaly.after_word.end_s),
            ]
    if not segment:
        return []
    intervals = []
    for recording in report.exploratory.recordings:
        reference = recording.recording_id == report.exploratory.reference_id
        interval = segment.reference if reference else segment.participant
        gap = segment.reference_gap_before_s if reference else segment.participant_gap_before_s
        start = interval.start_s - (
            (gap or 0) if anomaly or item.category == "gap_difference" else 0
        )
        if anomaly and recording.automatic_alignment:
            previous = next(
                (
                    w
                    for w in recording.automatic_alignment.words
                    if w.token_index == anomaly.before_token_index
                ),
                None,
            )
            if previous:
                start = previous.start_s
        intervals.append((start, interval.end_s))
    return intervals


def check(insights, csv_path, summary, evidence, expect_first=False):
    data = json.loads(insights.read_text(encoding="utf-8"))
    if "result" in data:
        if content_hash(data["result"]) != data["sha256"]:
            raise ValueError("JSON envelope checksum differs")
        data = data["result"]
    report = ComparativeReport.model_validate(data)
    candidates = {c.id: c.model_dump(mode="json") for c in report.exploratory.candidates}
    with csv_path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != len(candidates) or {r["candidate_id"] for r in rows} != set(candidates):
        raise ValueError("CSV candidate inventory differs")
    for row in rows:
        candidate = candidates[row["candidate_id"]]
        for field, value in row.items():
            expected = candidate["id" if field == "candidate_id" else field]
            if expected is None:
                valid = value == ""
            elif isinstance(expected, float | int):
                valid = float(value) == expected
            else:
                valid = value == expected
            if not valid:
                raise ValueError(f"CSV {field} differs for {candidate['id']}")
    result = {}
    paired = bool(report.exploratory.pair_id)
    footer = "TakeTwo / speech comparison" if paired else "TakeTwo / reference inspection"
    selected = report.inspection_order[:3]
    for mode, path in [("summary", summary), ("evidence", evidence)]:
        doc = pymupdf.open(path)
        pages = [p.get_text() for p in doc]
        text = "\n".join(pages)
        normalized = compact(text)
        for index, page in enumerate(doc):
            if len(pages[index].strip()) < 150 or compact(footer) not in compact(pages[index]):
                raise ValueError(f"Blank page or incorrect footer: {mode} page {index + 1}")
            if f"{index + 1}/{len(doc)}" not in compact(pages[index]):
                raise ValueError("Page counter differs")
            for block in page.get_text("rawdict")["blocks"]:
                for line in block.get("lines", []):
                    for span in line["spans"]:
                        for char in span["chars"]:
                            x0, y0, x1, y1 = char["bbox"]
                            if (
                                min(x0, y0) < 0
                                or x1 > page.rect.width + 0.1
                                or y1 > page.rect.height + 0.1
                            ):
                                raise ValueError(f"Text outside page: {mode} page {index + 1}")
        if (
            compact("Analysis Summary" if mode == "summary" else "Full Evidence Report")
            not in normalized
        ):
            raise ValueError("Report title differs")
        expected_ids = (
            [i.evidence_id for i in selected]
            if mode == "summary"
            else [
                x.id
                for collection in [report.groups, report.segments, report.anomalies]
                for x in collection
            ]
            + list(candidates)
        )
        if any(i not in normalized for i in expected_ids):
            raise ValueError("PDF evidence inventory differs")
        for recording in report.exploratory.recordings:
            if (
                compact(recording.filename) not in normalized
                or f"{recording.duration_s:.3f}" not in text
            ):
                raise ValueError("Recording identity/duration differs")
        for item in selected:
            for start, end in native_intervals(report, item):
                if f"{start:.2f}" not in text or f"{end:.2f}" not in text:
                    raise ValueError("Selected native bounds differ")
        if report.config.method not in text or report.exploratory.dataset_version not in text:
            raise ValueError("Method/dataset version differs")
        comparison = report.exploratory.comparison
        if comparison:
            for value in [abs(comparison.duration_delta_s), comparison.rms_level_delta_db]:
                if value is not None and f"{value:.3f}" not in text:
                    raise ValueError("Whole-recording measurement differs")
        if mode == "summary":
            printed = re.findall(r"Evidence reference:\s*([a-z]-[0-9a-f]+)", text)
            if printed != [i.evidence_id for i in selected]:
                raise ValueError("Summary contains unsupported or reordered findings")
            if "appendix" in text.lower() or "ordered items" in text or "window(s)" in text:
                raise ValueError("Technical/inaccurate summary wording")
            if selected and expect_first and selected[0].evidence_id not in compact(pages[0]):
                raise ValueError("Leading selected finding is not on page one")
        else:
            segment_ids = {s.id for s in report.segments}
            for page_text in pages:
                if segment_ids.intersection(line.strip() for line in page_text.splitlines()):
                    if "Supplied text" not in page_text:
                        raise ValueError("Missing repeated word-inventory column header")
            for digest in [
                report.exploratory_sha256,
                report.implementation_sha256,
                report.exploratory.dataset_sha256,
            ]:
                if digest not in normalized:
                    raise ValueError("Full provenance digest differs")
        result[mode] = {
            "pages": len(doc),
            "evidence_ids": len(expected_ids),
            "first_selected_page": next(
                (
                    i + 1
                    for i, p in enumerate(pages)
                    if selected and selected[0].evidence_id in compact(p)
                ),
                None,
            ),
            "footer": footer,
            "text_bounds": "pass",
        }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ["insights", "csv", "summary", "evidence"]:
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument(
        "--expect-first-highlight",
        action="store_true",
        help="Require page-one placement for a case whose leading finding fits",
    )
    args = parser.parse_args()
    print(
        json.dumps(
            check(
                args.insights, args.csv, args.summary, args.evidence, args.expect_first_highlight
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
