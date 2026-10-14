import { number } from "../api";
import type { ComparativeReport } from "../api";

type Item = ComparativeReport["inspection_order"][number];

// Readable presentation of existing evidence; no new selection or scoring rule.
export function inspectionReason(
  report: ComparativeReport,
  item: Item,
): string {
  const anomaly = report.anomalies.find((a) => a.id === item.evidence_id);
  const segment = report.segments.find((s) => s.id === item.evidence_id);
  const group = report.groups.find((g) => g.id === item.evidence_id);
  if (anomaly) {
    return anomaly.measurement.complete &&
      anomaly.measurement.low_energy_s === 0
      ? `The ${number(anomaly.gap.end_s - anomaly.gap.start_s, 3)} s automatic word gap does not match a low-energy interval in the acoustic measurement. Check the supplied text and assigned timing against the recording.`
      : `The ${number(anomaly.gap.end_s - anomaly.gap.start_s, 3)} s automatic word gap merits checking against the supplied text and measured activity. It establishes neither silence nor an alignment error.`;
  }
  if (segment) {
    return item.category === "gap_difference"
      ? `The provisional gap before this word is ${number(segment.participant_gap_before_s, 3)} s in the participant and ${number(segment.reference_gap_before_s, 3)} s in the reference. Inspect the assigned boundaries around this supplied-text word.`
      : `The assigned participant word duration differs by ${number(segment.duration_delta_s, 3)} s from the reference. Check the automatic boundaries before interpreting this difference.`;
  }
  if (group) {
    const count = group.candidate_ids.length;
    return `${count} supporting ${count === 1 ? "window describes" : "windows describe"} a ${number(group.duration_s, 3)} s ${group.direction === "low_energy" ? "low-energy" : "digital-level change"} interval. Inspect the connected passage alongside its contributing measurements.`;
  }
  return "Supporting evidence is unavailable; restore the complete result before interpreting this item.";
}

export function readableEvidenceReason(reason: string): string {
  return reason.replace(
    /(\d+) source window\(s\)/g,
    (_, count: string) =>
      `${count} source ${count === "1" ? "window" : "windows"}`,
  );
}

export function selectionLabel(count: number, paired: boolean): string {
  const noun = paired ? "passage" : "interval";
  if (!count) return `No supported ${noun}s selected for inspection.`;
  const amount = ["", "One", "Two", "Three"][count] ?? String(count);
  return `${amount} ${noun}${count === 1 ? "" : "s"} selected for inspection.`;
}
