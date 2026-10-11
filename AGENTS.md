
Create and maintain a root-level `AGENTS.md` that defines the permanent engineering and product standards for TakeTwo.

**Product identity**

Use "TakeTwo" as the product name and "Speech analysis workspace" as its description across documentation, metadata and visible application branding.

TakeTwo is a professional speech-analysis workstation, not an AI chatbot, generic SaaS dashboard, or marketing prototype.

Use the Workshop + Gridline + Studio Utility design language across every interface. The product should feel like specialized, carefully maintained engineering software.

**Design rules**

- Use a consistent typography, spacing, colour and component system.
- Prefer restrained colours, precise grids, subtle borders and functional visualizations.
- Avoid purple gradients, glassmorphism, glowing cards, excessive rounding and decorative statistics.
- Do not invent metrics, activity feeds, users or analysis results.
- Prioritize comfortable information density over empty decorative space.
- Every control must perform a real action.
- Provide deliberate loading, empty, error and recovery states.
- Make keyboard navigation and accessibility part of normal implementation.
- Use clear, concise, specific product language rather than generic AI-generated copy.

**Code quality**

- Write straightforward, idiomatic, maintainable code.
- Use descriptive names based on the speech-analysis domain.
- Prefer small cohesive modules and clear interfaces.
- Avoid overengineering, speculative abstractions, unnecessary dependencies and generated boilerplate.
- Keep the repository organized and free of temporary artifacts.
- Never remove working functionality merely to simplify an implementation.
- Use focused commits and explain meaningful design decisions.
- Keep public APIs and data contracts documented.

**Scientific integrity**

- Use real acoustic measurements and real processing pipelines.
- Never substitute hardcoded demonstration outputs for analysis.
- Distinguish source recordings, synthetic alterations and annotated ground truth.
- Preserve dataset provenance and applicable licenses.
- Make scoring formulas, thresholds and feature definitions explicit.
- Preserve temporal grounding and explain each flagged region with measurable evidence.
- Report actual evaluation results, limitations and failure cases.
- Never claim causal certainty where only acoustic association is established.
- Keep analysis reproducible under fixed inputs and configuration.

**Development workflow**

1. Inspect the existing repository before modifying it.
2. Identify the smallest complete implementation step.
3. Implement the feature and its required tests.
4. Run available checks and verify the result.
5. Fix discovered regressions.
6. Update relevant documentation.
7. Commit related changes with a meaningful message.
8. Report completed work, verified evidence and outstanding blockers.

Do not claim that tests passed unless they were actually executed. Do not mark unfinished functionality complete. Do not claim that the application is production-ready solely because automated tests pass.

**Hackathon compliance**

Follow the official Track C problem statement, including the contrastive dataset, forced alignment, acoustic feature extraction, temporal grounding, explainable rubric-based scoring, reproducibility, dashboard and deliverables.

Document Codex and other AI assistance honestly. Aim for professional, human-directed quality rather than concealing AI tool use.

Apply these standards to all existing and future TakeTwo code, interfaces, documentation and development decisions.
