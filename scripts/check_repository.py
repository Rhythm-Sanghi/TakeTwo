"""Check local documentation, scientific schemas and unchanged official specification."""

import json
import re
import runpy
from pathlib import Path
from urllib.parse import unquote

from taketwo.analysis.contracts import AlignmentResult, FeatureResult
from taketwo.comparison.cli import schema
from taketwo.dataset.audio import sha256
from taketwo.dataset.schema import Dataset
from taketwo.exploratory.contracts import ExploratoryReport
from taketwo.insights.contracts import ComparativeReport

ROOT = Path(__file__).resolve().parents[1]


def main():
    documents = [ROOT / "README.md", ROOT / "AGENTS.md", *sorted((ROOT / "docs").glob("*.md"))]
    links = 0
    for path in documents:
        text = path.read_text(encoding="utf-8")
        if len(re.findall(r"^```", text, flags=re.MULTILINE)) % 2:
            raise ValueError(f"Unclosed code fence: {path}")
        if "Cadence" in text:
            raise ValueError(f"Obsolete product name: {path}")
        for target in re.findall(r"\]\(([^)]+)\)", text):
            if target.startswith(("https://", "http://", "#", "mailto:")):
                continue
            target = unquote(target.split("#", 1)[0])
            if not (path.parent / target).is_file():
                raise ValueError(f"Broken local link in {path}: {target}")
            links += 1
    matrix = (ROOT / "docs/requirements-matrix.md").read_text(encoding="utf-8")
    for weight in ("30%", "25%", "20%", "15%", "10%"):
        if weight not in matrix:
            raise ValueError(f"Official judging weight missing: {weight}")
    expected = {
        "dataset-schema-v2.json": Dataset.model_json_schema(),
        "analysis-schema-v1.json": {
            "alignment": AlignmentResult.model_json_schema(),
            "features": FeatureResult.model_json_schema(),
        },
        "comparison-schema-v1.json": schema(),
        "exploratory-schema-v1.json": ExploratoryReport.model_json_schema(),
        "comparative-insights-schema-v1.json": ComparativeReport.model_json_schema(),
        "api-v1.json": runpy.run_path(str(ROOT / "scripts/export_api.py"))["contract"](),
    }
    for name, contract in expected.items():
        saved = json.loads((ROOT / "docs" / name).read_text(encoding="utf-8"))
        if saved != contract:
            raise ValueError(f"Schema differs from runtime: {name}")
    pdf_hash = sha256((ROOT / "requirments/Track C.pdf").read_bytes())
    if pdf_hash != "0e621d35e6bfdbb9d9e169b259ebf9d3d923d1efcbab38ba2a4331f6958fb280":
        raise ValueError("Official specification PDF changed.")
    print(
        json.dumps(
            {
                "markdown_files": len(documents),
                "local_links": links,
                "schemas": list(expected),
                "official_pdf_sha256": pdf_hash,
            }
        )
    )


if __name__ == "__main__":
    main()
