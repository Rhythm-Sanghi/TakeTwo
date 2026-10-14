export const workspacePages = [
  "Recording Library",
  "Analysis Workspace",
  "Rubric and Evidence",
  "Review Workspace",
  "Dataset and Evaluation",
] as const;
export type Page = (typeof workspacePages)[number];

export function WorkspaceNavigation({
  current,
  onNavigate,
}: {
  current: Page;
  onNavigate: (page: Page) => void;
}) {
  return (
    <nav aria-label="Workspace areas">
      <div className="desktop-navigation">
        {workspacePages.map((page) => (
          <button
            key={page}
            aria-current={current === page ? "page" : undefined}
            onClick={() => onNavigate(page)}
          >
            {page}
          </button>
        ))}
      </div>
      <label className="mobile-navigation">
        Workspace
        <select
          aria-label="Workspace"
          value={current}
          onChange={(event) => onNavigate(event.target.value as Page)}
        >
          {workspacePages.map((page) => (
            <option key={page}>{page}</option>
          ))}
        </select>
      </label>
    </nav>
  );
}
