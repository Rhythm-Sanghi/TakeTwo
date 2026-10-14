export type ReportType = "summary" | "evidence";
export type WorkspacePrintMode = "paired" | "reference" | "dataset";

function rememberPrintState() {
  const previousTitle = document.title;
  const previousScope = document.body.dataset.printScope;
  const previousType = document.body.dataset.reportType;
  const previousMode = document.body.dataset.reportMode;
  return () => {
    document.title = previousTitle;
    if (previousScope == null) delete document.body.dataset.printScope;
    else document.body.dataset.printScope = previousScope;
    if (previousType == null) delete document.body.dataset.reportType;
    else document.body.dataset.reportType = previousType;
    if (previousMode == null) delete document.body.dataset.reportMode;
    else document.body.dataset.reportMode = previousMode;
  };
}

function selectPrintView(
  type: ReportType | "workspace" | "dataset",
  mode: WorkspacePrintMode,
) {
  const name =
    mode === "paired"
      ? "speech-comparison"
      : mode === "reference"
        ? "reference-inspection"
        : "dataset-readiness";
  const suffix =
    type === "summary"
      ? "analysis-summary"
      : type === "evidence"
        ? "full-evidence-report"
        : type === "workspace"
          ? "workspace-view"
          : "report";
  document.title = `TakeTwo-${name}-${suffix}`;
  document.body.dataset.printScope =
    type === "summary" || type === "evidence" ? "exploratory" : "workspace";
  document.body.dataset.reportType = type;
  document.body.dataset.reportMode = mode;
}

function print(
  type: ReportType | "workspace" | "dataset",
  mode: WorkspacePrintMode,
) {
  const restore = rememberPrintState();
  selectPrintView(type, mode);
  window.addEventListener("afterprint", restore, { once: true });
  try {
    window.print();
  } catch (error) {
    window.removeEventListener("afterprint", restore);
    restore();
    throw error;
  }
}

// Browser Save as PDF keeps searchable text. Restore scope/title on cancel too.
export function printAnalysisReport(type: ReportType, paired: boolean) {
  print(type, paired ? "paired" : "reference");
}

export function printWorkspaceReport(mode: WorkspacePrintMode) {
  print(mode === "dataset" ? "dataset" : "workspace", mode);
}

// Ordinary Ctrl+P needs the same identity as the supported workspace action.
// Dedicated exports already select their view and must never be overridden.
export function installWorkspacePrint(mode: WorkspacePrintMode) {
  let restore: (() => void) | null = null;
  const prepare = () => {
    if (document.body.dataset.reportType) return;
    restore = rememberPrintState();
    selectPrintView(mode === "dataset" ? "dataset" : "workspace", mode);
  };
  const finish = () => {
    restore?.();
    restore = null;
  };
  window.addEventListener("beforeprint", prepare);
  window.addEventListener("afterprint", finish);
  return () => {
    window.removeEventListener("beforeprint", prepare);
    window.removeEventListener("afterprint", finish);
    finish();
  };
}
