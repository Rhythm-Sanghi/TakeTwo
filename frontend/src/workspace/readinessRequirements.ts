import type { Recording, Report } from "../api";
import type { DatasetSummary, Readiness } from "./DatasetReadiness";

type Requirement = {
  name: string;
  status: string;
  missing: string;
  why: string;
  action: string;
  location: string;
};

export function readinessRequirements(
  recording: Recording | undefined,
  readiness: Readiness | undefined,
  summary: DatasetSummary | null,
  report: Report | null,
  current: boolean,
): Requirement[] {
  const known =
    current &&
    Boolean(
      recording?.provenance?.rights &&
      recording?.transcript &&
      readiness &&
      summary,
    );
  const reviewStatus = (scope: string) =>
    !known || readiness?.review_agreement?.[scope] == null
      ? "Unknown"
      : readiness.review_agreement[scope]
        ? "Agreement recorded"
        : readiness.review_status?.[scope] === "No submitted reviews"
          ? "Pending"
          : "Blocked";
  const rights = recording?.provenance?.rights;
  const consent =
    recording?.origin !== "self_recorded" ||
    Boolean(recording?.provenance?.consent_evidence);
  const transcriptVerified = recording?.transcript?.status === "verified";
  const hasPair = Boolean(readiness?.pair_id);
  return [
    {
      name: "Recording rights",
      status: !known
        ? "Unknown"
        : rights?.status === "cleared" && consent
          ? "Declaration recorded"
          : "Blocked",
      missing: !known
        ? "Current rights evidence unavailable."
        : rights?.status !== "cleared"
          ? "Rights clearance is pending; local import permission does not grant redistribution."
          : !consent
            ? "Genuine consent evidence is missing."
            : "The manifest records permission; the software does not grant or authenticate legal rights.",
      why: "Permitted uses must match actual permission and consent evidence.",
      action:
        "Preserve actual holder, license, permitted scope and evidence references in ImportSpec metadata; create a new version for corrections.",
      location: "Recording provenance / reviewed-version CLI workflow",
    },
    {
      name: "Spoken transcript",
      status: !known
        ? "Unknown"
        : transcriptVerified
          ? "Verified in manifest"
          : reviewStatus("transcript"),
      missing: !known
        ? "Current transcript review status unavailable."
        : transcriptVerified
          ? "Verification metadata is recorded; reviewer identities are not authenticated by TakeTwo."
          : (readiness?.review_status?.transcript ??
            "Transcript evidence unavailable."),
      why: "MFA aligns supplied text; it does not establish the words actually spoken.",
      action:
        "Two real independent reviewers listen and check text. Resolve discrepancies with same-author revisions, then import their agreed text into a reviewed version.",
      location: "Review Workspace · transcript / new-version import",
    },
    {
      name: "Word and phrase timing",
      status: reviewStatus("timing"),
      missing: known
        ? (readiness?.review_status?.timing ?? "Timing status unavailable.")
        : "Current timing evidence unavailable.",
      why: "Native temporal comparisons require reviewed boundaries and a common phrase partition.",
      action:
        "Process the reviewed version, then have two independent reviewers inspect every word and phrase against its current alignment hash.",
      location: "Review Workspace · timing",
    },
    {
      name: "Human flaw inventory",
      status: !known
        ? "Unknown"
        : !hasPair
          ? "Not applicable to reference alone"
          : reviewStatus("flaws"),
      missing: !known
        ? "Current annotation evidence unavailable."
        : !hasPair
          ? "A participant pair is required for flaw review and evaluation."
          : (readiness?.review_status?.flaws ??
            "Flaw review status unavailable."),
      why: "Automatic observations and usability notes are not ground-truth flaws.",
      action:
        "Two independent blinded reviewers cover the full participant recording and record genuine labels or a genuinely reviewed empty inventory. Resolve exact-inventory disagreement.",
      location: "Review Workspace · blinded flaws / adjudication",
    },
    {
      name: "Reviewed dataset version",
      status: !known
        ? "Unknown"
        : !transcriptVerified
          ? "Pending"
          : readiness?.job_id
            ? "Version and processing recorded"
            : "Blocked",
      missing: !known
        ? "Current dataset/version evidence unavailable."
        : !transcriptVerified
          ? "Agreed reviewer assertions do not automatically update the manifest."
          : !readiness?.job_id
            ? "Successful processing for the reviewed version is missing."
            : `Dataset ${summary?.dataset_version}; dependent review and eligibility checks still apply.`,
      why: "Corrections change provenance and invalidate dependent artifacts.",
      action:
        "Create a new workspace/version, import originals with legitimate reviewed metadata, then regenerate alignment/features. Preserve earlier versions and reviews.",
      location: "taketwo-dataset / taketwo-analysis CLI",
    },
    {
      name: "Scientific evaluation",
      status: !known
        ? "Unknown"
        : !report
          ? "Unavailable"
          : report.eligibility.state === "ELIGIBLE"
            ? "Pending evaluation"
            : "Blocked",
      missing: !known
        ? "Current eligibility and split information unavailable."
        : !report
          ? "No selected comparison report is available."
          : report.eligibility.state !== "ELIGIBLE"
            ? "The selected comparison is not eligible; reviewed labels and valid held-out splits are also required."
            : "Eligibility alone does not establish valid ground truth, held-out splits or computed metrics.",
      why: "Closely related takes cannot establish speaker-independent generalization.",
      action:
        "Validate labels, dataset identity and connected-group splits; run evaluation only when prerequisites pass. Preserve withheld metrics and actual error diagnostics.",
      location:
        "Dataset and Evaluation · review import / taketwo-comparison evaluate",
    },
  ];
}
