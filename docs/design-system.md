# TakeTwo design system

Product name: **TakeTwo**. Description: **Speech analysis workspace**. Implemented by the React workspace. See [interaction guide](frontend-workspace.md) and [actual verification](verification.md); human-pair/manual accessibility acceptance remains open.

## Workshop + Gridline + Studio Utility

Workshop means visible tools, evidence and deliberate operating states. Gridline means aligned columns, consistent scales and quiet borders. Studio Utility means audio transport, precise time readings and comfortable inspection density. The product should feel like maintained engineering software. Avoid chatbot layouts, decorative statistic cards, glass effects, purple gradients, glow and oversized empty hero areas.

## Tokens

| Category | Specification |
| --- | --- |
| Typography | Local system sans (`Segoe UI`, system-ui); monospace (`Cascadia Mono`, `Consolas`, monospace) for time, units and hashes. No mandatory web font downloads |
| Type scale | 12 px metadata, 14 px interface/body, 16 px section labels, 20 px page title; line height 1.45-1.6; tabular numerals for comparisons |
| Spacing | 4 px base; 4/8/12/16/24/32 px steps. Panel padding 16 px, dense tool groups 8-12 px |
| Surfaces | Workspace `#F4F3EF`, panel `#FFFFFF`, subtle secondary `#EAE9E3` |
| Text | Primary `#202824`, secondary `#4D5B54`; never use disabled text for needed evidence |
| Structure | Quiet border `#D1D5CF`; meaningful control outlines `#76857C`; 1 px rules; 2-4 px corner radii |
| Action / focus | Deep teal `#235A50`; white action text; focus outline `#005FCC`, 2 px with offset |
| Signals | Reference `#235A50` solid, participant `#8B4D22` dashed; warning `#805100`, error `#A12C2C`, success `#286140` with text/icon labels |
| Motion | Minimal 100-150 ms state transitions; respect reduced-motion preference; no animated decoration |

Tokens are starting choices. Verify actual foreground/background combinations to WCAG AA in implementation: at least 4.5:1 normal text, 3:1 large text and meaningful non-text controls. Quiet borders separate panels; they are insufficient as sole control boundaries. Color never carries meaning alone.

## Workspace structure

Use a compact top bar with name, description, active pair and actual processing state. Keep the full collection/history only in Recording Library, with a 260 px collection column on desktop and a vertical list below 800 px. Other pages begin with their task and concise comparison context. The inspector is a secondary disclosure below the evidence tools. Timelines pair where space permits; at 800 px and below, explicit track buttons switch between mounted native timelines, pausing playback while retaining each cursor and selection. Below 600 px a labeled native workspace selector replaces the desktop navigation row. Maintain readable minimum content widths and local chart scrolling rather than shrinking text.

Connected views: recording library/import, pair comparison, selected-region inspector, rubric, evaluation runs and export. Start the user with import/select-reference actions and supported formats. Empty lists contain no sample users, fabricated analyses or decorative metrics. Evaluation charts exist only after actual evaluation runs.

## Reusable controls and states

Use standard buttons, labeled file inputs, text areas, selects, disclosure panels, data tables, transport controls, range inputs, status messages and evidence rows. Every visible control must perform a real action; omit unfinished controls from the operating UI. Disabled actions explain missing prerequisites through nearby text, not hover-only tooltips. Destructive operations identify affected recordings and respect report dependencies.

| State | Required behavior |
| --- | --- |
| Empty | Explain which file/transcript is needed and offer import |
| Validating / queued | Show actual named stage and queue state, with cancel when possible |
| Processing | Stage text and busy announcement; no invented percentage or ETA |
| Needs review | Identify transcript/channel/alignment issue and direct correction/retry |
| Failed / interrupted | Preserve input and error context; show retry and recovery guidance |
| Partial evidence | Display available contours with missing spans and explicit unavailable scores |
| Complete | Offer evidence inspection, rubric details and real export |

Product language is concise and measurable: "Alignment needs review", "Pitch evidence unavailable", "Pause exceeds tolerance". Avoid claims about confidence, emotion or rhetorical quality unsupported by the engine.

## Waveforms and charts

Show reference and participant in distinct lanes with labeled native timestamps, units and a shared token/phrase correspondence row. An optional aligned overlay uses a clearly labeled transcript-position axis; it must not pretend both recordings have identical wall time. Seeking an overlay position maps through the selected recording's word interval. Duration/pause evidence always remains visible on native time axes.

Render min/max waveform envelopes at display resolution; zoom changes resolution without inventing sample detail. Provide play/pause, reference/participant selection, seek, zoom and region navigation with accessible names. Playback uses one recording at a time; preserve separate cursors. Display selection start/end/duration numerically and distinguish listening selection from detected regions.

Feature plots label F0 Hz or normalized semitones, energy dBFS or relative dB, rate words/min and time seconds. Never mix raw and normalized values without explicit labels. Use consistent units/ranges across compared lanes, thin gridlines, zero/baseline where meaningful and gaps for invalid frames. Downsampling preserves extrema for waveform/energy inspection and declares aggregation; full-resolution values remain in exports. No decorative 3D plots or arbitrary smoothed trends.

Region shading uses a hatch/outline plus category text. Selecting a region updates the inspector with matched transcript, both intervals, measured values, signed delta, tolerance, calculation and reliability. Chart tooltips duplicate information available by keyboard in an evidence table. Scores show rubric version and coverage next to the value; missing scores display "Unavailable" and the reason.

## Accessibility and verification

Use semantic landmarks, logical heading order, visible labels, table headers and focus indicators. Tab order follows reading/workflow order. Native controls retain expected keys; Space plays only when the transport has focus, arrows seek only within the focused timeline, and Escape closes overlays and restores focus. Region previous/next buttons provide a non-pointer alternative to dragging. Announce stage changes with a polite live region; errors use an appropriate alert without repeatedly interrupting playback.

At 200% zoom, controls reflow without loss; touch/click targets aim for at least 32 px in dense desktop controls and 44 px for primary transport. Ensure accessible names, text error associations and keyboard access to every chart action. Phase 4 verification includes browser keyboard flows, focus restoration, automated accessibility checks and manual screen-reader/contrast/zoom review; automated checks alone are insufficient.


## Information hierarchy

Outcome and next action come first; supporting measurements, findings and listening
come next; implementation details and diagnostics follow in disclosures. Use the
shared ruled measurement row for real evidence rather than decorative statistics.
Pair labels, role names and solid/dashed track signals remain legible without color.
Review steps show the assigned scope and acknowledged save/validation state, never
an inferred percentage or completion based on navigation.

Outcome panels have a 1120 px maximum reading width; comparison charts retain working width. Reference inspection describes measurements and processing, with participant selection as the next action. It does not present comparison abstention as a failed reference analysis. Print layouts distinguish single-input evidence from paired reference agreement.
