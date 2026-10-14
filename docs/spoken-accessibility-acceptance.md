# Spoken accessibility acceptance

TakeTwo — Speech analysis workspace. **Narrator/NVDA spoken acceptance: pending.**
No completed actual-listener record is available. Axe, keyboard-routing, native zoom
and PDF tagging checks do not establish spoken comprehension. This coding environment
does not provide a genuine audible screen-reader acceptance session.

## Prepare an actual Windows session

Record Windows, browser and screen-reader versions, listener/date (with permission),
dataset/job identity and viewport/zoom. Restart the local TakeTwo backend with the
current code before testing. Use authorized private recording copies; preserve originals.
Start Narrator with **Windows + Ctrl + Enter**, following the
[official Microsoft commands](https://support.microsoft.com/en-us/accessibility/windows/narrator/appendix-b-narrator-keyboard-commands-and-touch-gestures).
Prefer a separate NVDA run when available; use its
[official user guide](https://download.nvaccess.org/documentation/userGuide.html).
In NVDA browse mode, `H` navigates headings and `B` buttons; `NVDA + Space` switches
browse/focus modes. Use Tab/Shift+Tab to test actual control focus as well as reading.
Keep speech output audible to the reviewer; reading a DOM snapshot is not this test.

## Test steps and expected understanding

| Step | What the listener must verify | Actual result / problem |
| --- | --- | --- |
| Workspace navigation | Names, current area and keyboard focus are understandable | |
| Recording selectors | Reference/participant identities and selected values are spoken | |
| Run/restore analysis | Loading, processing completion and failures are announced without repeated noise | |
| Opening result | Listener can identify recordings, measured differences and unverified status without a graph | |
| Selected heading | Finding category and supplied-text context are understandable | |
| Native timestamps | Each recording's independent start/end and units are understandable | |
| Why inspect / Listen for | Listener can explain the selection reason and uncertainty | |
| Replay reference / participant | Button names, audio switching and stopping bounds are understandable | |
| Inspect waveform | Focus moves to the intended recording's native audio control | |
| Expand evidence | Disclosure state and complete source measurements are reachable | |
| Export both reports | Summary/full purposes and controls are distinct; cancelling restores the workspace | |
| Safe failure/retry | Error and recovery are spoken; stale source results do not remain active | |
| Reference-only repeat | No nonexistent participant or paired differences are presented | |
| Native 200% repeat | Focus, reading and controls work without a visual-only workaround | |
| Dataset readiness | Selected recording/version and all six prerequisite statuses, missing evidence and next actions are spoken | |
| Evaluation unavailable/retry | A failed request is announced as unavailable; recovery distinguishes a successful zero inventory | |
| Dataset PDF export | Export name, print guidance, failure recovery and restored focus are understandable | |

Record inaccessible controls, missing/duplicate announcements, unexpected focus moves,
ambiguous wording and graph-dependent conclusions. Repeat failed steps after fixes.
Classify each step **Passed**, **Failed**, **Inconclusive**, **Not performed** or
**Blocked**, with exact
spoken observations; leave all fields blank until an actual reviewer performs them.
No automatic review, scientific approval, rights clearance or publication decision
results from completing this worksheet.
