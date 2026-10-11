"""Export the implemented OpenAPI contract without leaving a local dataset behind."""

import json
import tempfile
from pathlib import Path

from taketwo.web.app import create_app
from taketwo.web.contracts import ImportRequest


def contract():
    with tempfile.TemporaryDirectory(prefix="taketwo-schema-") as directory:
        schema = create_app(Path(directory) / "workspace").openapi()
    metadata = ImportRequest.model_json_schema(ref_template="#/components/schemas/{model}")
    schema["components"]["schemas"].update(metadata.pop("$defs"))
    schema["components"]["schemas"]["ImportRequest"] = metadata
    return schema


if __name__ == "__main__":
    target = Path(__file__).resolve().parents[1] / "docs/api-v1.json"
    target.write_text(json.dumps(contract(), indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
