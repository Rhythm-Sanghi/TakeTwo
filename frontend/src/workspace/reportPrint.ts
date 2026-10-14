export type ReportType = "summary" | "evidence";

// Browser Save as PDF keeps searchable text. Restore scope/title on cancel too.
export function printAnalysisReport(type: ReportType, paired: boolean) {
  const previousTitle = document.title;
  const previousScope = document.body.dataset.printScope;
  const previousType = document.body.dataset.reportType;
  const restore = () => {
    document.title = previousTitle;
    if (previousScope == null) delete document.body.dataset.printScope;
    else document.body.dataset.printScope = previousScope;
    if (previousType == null) delete document.body.dataset.reportType;
    else document.body.dataset.reportType = previousType;
  };
  document.title = `TakeTwo-${paired ? "speech-comparison" : "reference-inspection"}-${type === "summary" ? "analysis-summary" : "full-evidence-report"}`;
  document.body.dataset.printScope = "exploratory";
  document.body.dataset.reportType = type;
  window.addEventListener("afterprint", restore, { once: true });
  try {
    window.print();
  } catch (error) {
    window.removeEventListener("afterprint", restore);
    restore();
    throw error;
  }
}
