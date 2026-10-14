# Searchable reports and workspace printing

TakeTwo — Speech analysis workspace.

1. Restore the intended completed analysis. Check reference/participant filenames,
   job ID, dataset version and native intervals before exporting.
2. Start with **Export Analysis Summary / save PDF**. It selects three existing
   observations and verification status; it is not a delivery-flaw diagnosis.
3. Use **Export Full Evidence Report / save PDF** for every group, provisional word,
   raw acoustic window, method and provenance. JSON retains the authoritative model;
   interval CSV retains raw windows. A summary is a separate document, not an appendix.
4. In Chromium's print destination, select **Save as PDF**. The two owner-supplied
   Microsoft Print to PDF files contain outlined glyphs and no extractable text.
   That printer path is unsuitable for those outputs. Changing a filename cannot
   restore absent text; re-export from the actual application rather than using OCR.
5. **Print workspace evidence** (or ordinary browser printing) produces a deliberate
   workspace view: selected observations, current native chart windows and an explicit
   verification state. It excludes technical inventories and interactive controls;
   those remain available through the dedicated full report and data exports.
6. Reopen the saved file. Select/copy a recording name and numeric measurement, search
   for a highlighted phrase, and check the correct comparison/reference footer and
   page counters. Inspect every page for clipping, blank sections and readable charts.
7. Recheck text with an independent extractor. The optional QA tools require no
   application dependency changes:

   ```powershell
   uv run --with pymupdf==1.28.2 --with pypdf==6.20.1 python scripts/check_pdf_text.py $pdfPath --expect TakeTwo
   ```

   Add repeated `--expect` arguments for actual recording names, headings, Unicode
   observations, numbers and limits. Use `scripts/check_analysis_pdf.py` with the
   matching JSON/CSV for complete comparative inventory, native intervals and hashes.
8. Searchable/selectable text, embedded fonts and an available structure tree are
   checked separately. They do not certify PDF/UA, reliable reading order in every
   viewer, keyboard audio usability or actual Narrator/NVDA speech. Review tagged
   headings/tables and reading order with the intended viewer/assistive technology;
   spoken acceptance remains a real-person task.

Reports containing private recordings, source identities or review evidence remain
local. Do not attach them to a public release without genuine rights and authorization.
