import { useState } from "react";

export function ReviewJourney({
  scope,
  dirty,
  busy,
  submitted,
  validated,
  issues,
}: {
  scope: "transcript" | "timing" | "flaws";
  dirty: boolean;
  busy: boolean;
  submitted: boolean;
  validated: boolean;
  issues: string[];
}) {
  const [current, setCurrent] = useState("review-listen");
  const steps = [
    ["review-listen", "Listen"],
    [
      "review-evidence",
      scope === "transcript"
        ? "Check transcript"
        : scope === "timing"
          ? "Inspect timing"
          : "Annotate flaws",
    ],
    ["review-notes", "Notes and uncertainty"],
    ["review-submit", "Validate and submit"],
  ];
  return (
    <section
      className="panel review-journey"
      aria-label="Assigned review steps"
    >
      <h2>{submitted ? "Review submitted" : "Your assigned review"}</h2>
      <p>
        {submitted
          ? "Saved as an immutable submitted assertion."
          : busy
            ? "Saving or checking with the local service…"
            : dirty
              ? "Unsaved changes — save your draft before validation."
              : "Draft saved. Submission requires backend validation."}
      </p>
      <ol>
        {steps.map(([id, text], i) => (
          <li key={id}>
            <button
              type="button"
              aria-current={current === id ? "step" : undefined}
              onClick={() => {
                setCurrent(id);
                requestAnimationFrame(() => {
                  const target = document.getElementById(id);
                  target?.scrollIntoView({ block: "start" });
                  target?.focus();
                });
              }}
            >
              {i + 1}. {text}
            </button>
            {(submitted || (validated && !dirty)) && (
              <span className="meta">
                {submitted ? "Submitted" : "Validated"}
              </span>
            )}
          </li>
        ))}
      </ol>
      <p className="meta">
        {submitted
          ? "All submission requirements passed when submitted."
          : validated && !dirty
            ? "Backend completion check passed. Submit when ready."
            : "Completion is not yet validated. Moving between steps does not approve evidence."}
      </p>
      {issues.length > 0 && (
        <details open>
          <summary>Remaining requirements from the completion check</summary>
          <ul>
            {issues.map((issue, i) => (
              <li key={i}>{issue}</li>
            ))}
          </ul>
        </details>
      )}
    </section>
  );
}
