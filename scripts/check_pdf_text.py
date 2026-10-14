"""Read-only PDF text/font inspection using two optional QA extractors."""

import argparse
import json
from pathlib import Path

import pymupdf
from pypdf import PdfReader


def inspect(path, expected):
    document = pymupdf.open(path)
    independent = PdfReader(path)
    texts = [page.get_text() for page in document]
    independent_texts = [page.extract_text() or "" for page in independent.pages]
    for name, pages in [("PyMuPDF", texts), ("pypdf", independent_texts)]:
        if not pages or any(len(text.strip()) < 100 for text in pages):
            raise ValueError(f"{name}: missing text or nearly empty page")
        if any("\ufffd" in text for text in pages):
            raise ValueError(f"{name}: Unicode replacement characters in extracted text")
        compact = "".join("\n".join(pages).split())
        for value in expected:
            if "".join(value.split()) not in compact:
                raise ValueError(f"{name}: expected report content is absent: {value}")
    font_refs = {font[0] for page in document for font in page.get_fonts()}
    if not font_refs:
        raise ValueError("PDF has no font resources; text may have been outlined")
    embedded = sum(bool(document.extract_font(reference)[3]) for reference in font_refs)
    for page in document:
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
                            raise ValueError("Extractable text falls outside a PDF page")
    return {
        "pages": len(document),
        "pymupdf_characters": [len(text) for text in texts],
        "pypdf_characters": [len(text) for text in independent_texts],
        "font_resources": len(font_refs),
        "embedded_fonts": embedded,
        "structure_tree": bool(independent.trailer["/Root"].get("/StructTreeRoot")),
        "expected_content": "pass in both extractors",
        "text_bounds": "pass",
        "accessibility_limit": (
            "Text/fonts/tags do not establish PDF/UA or spoken usability; "
            "inspect reading order and actual assistive technology separately."
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--expect", action="append", default=[])
    args = parser.parse_args()
    print(json.dumps(inspect(args.pdf, args.expect), indent=2))


if __name__ == "__main__":
    main()
