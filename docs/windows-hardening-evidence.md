# Windows restoration and reset evidence

TakeTwo — Speech analysis workspace. Measured locally on 14 October 2026:
Windows 11 Pro Insider Preview 10.0.26220, Python 3.11.9, Uvicorn 0.42.0,
Intel Core i7-1365U (12 logical processors), 16,815,702,016 bytes installed RAM.
This is same-host evidence, not a clean-machine compatibility certification.

## Reproduced transport defect

An isolated copy of the genuine workspace was made using SQLite backup connections
and copies of managed audio/artifacts. Originals, historical reviews and the live
owner workspace were not changed. Six owned local server processes were started:
three with Uvicorn's default Windows Proactor and three with
`loop="asyncio:SelectorEventLoop"`. Each loaded the existing report, exploratory
and comparative JSON, then exercised up to 30 abrupt TCP resets. Winsock
`SO_LINGER` was set to unsigned shorts `(1, 0)` after a local HTTP request;
the connection was closed after 20 ms. Health and comparative content were checked
again afterward. Every process was stopped by its experiment owner.

All three Proactor trials raised **WinError 64 / Accept failed on a socket** and
lost their HTTP listener (14, 30 and 19 resets sent). Python 3.11's installed
`proactor_events._start_serving` closes the accept socket on this OSError.
All three Selector trials survived 30 resets, without accept/callback exceptions,
and returned the identical comparative bytes. Every corresponding report,
exploratory and insights payload hash matched across all six trials.

The launcher now selects Selector only on Windows. This addresses the reproduced
accept failure; it does not suppress diagnostics or upgrade dependencies. Existing
workers use synchronous Popen in supervised threads, not asyncio subprocess pipes.
Windows Selector is suitable for this bounded local service, with its 512-socket
limit and lack of asyncio subprocess-pipe support. It is not an Internet-scale
server design. The earlier intermittent **WinError 10054** was observed during the
baseline, but was not reproduced by this experiment; its broader cause remains
unestablished. Do not claim every connection-reset diagnostic is fixed.

## Restoration measurements

Each process made one initial request and three repeated requests per endpoint,
in report → exploratory → insights order. “Cold” means a fresh process/cache;
OS disk caches were not cleared. Later endpoints can benefit from earlier
validation. The warm column describes nine calls, not a fresh extraction.

| Loop / request | Initial seconds, three trials | Warm median (range), seconds |
| --- | --- | --- |
| Proactor startup to healthy | 8.231, 4.985, 12.719 | Not applicable |
| Selector startup to healthy | 6.831, 6.665, 8.823 | Not applicable |
| Proactor report | 15.233, 11.302, 20.850 | 0.661 (0.331–3.118) |
| Selector report | 10.244, 42.479, 19.934 | 0.701 (0.451–0.886) |
| Proactor exploratory | 7.912, 14.235, 9.260 | 0.709 (0.521–0.854) |
| Selector exploratory | 5.030, 11.248, 25.149 | 1.257 (0.268–2.216) |
| Proactor insights | 3.138, 9.978, 6.403 | 0.622 (0.310–1.064) |
| Selector insights | 4.241, 12.572, 14.294 | 1.364 (0.294–4.798) |

These timings varied under host contention and concurrent development checks;
a snapshot showed only 1.66 GiB free physical memory. They do not demonstrate an
event-loop speedup. Source/environment/artifact validation stays active, including
on cached restoration. Cold latency remains a practical limitation. No acoustic
threshold or score was changed to make restoration faster.

The fresh genuine baseline job completed in **211.906 s**, no cache hits:
reference MFA 87.390 s, participant MFA 98.422 s, reference extraction 12.985 s,
participant extraction 10.343 s, comparison 1.204 s and validation 0.250 s.
Peak supervised worker-tree commit was **2,077,245,440 bytes**. This is kernel
commit accounting, not RSS, and separate from backend startup/restoration timings.
Native processing is CPU-only; independent scientific accuracy is unestablished.

The final fresh genuine run also passed all three browser tests (4.9 min).
Its selected pair job completed in **237.640 s**, no cache hits: reference MFA
116.671 s, participant MFA 91.219 s, reference extraction 15.297 s, participant
extraction 11.375 s, comparison 1.328 s and validation 0.266 s. Peak supervised
tree commit was **2,081,546,240 bytes**. These are a second actual run, not a
comparison establishing universal throughput; host variation remains visible.

## Concurrent cold-load repair and browser measurements

A fresh browser then reproduced the existing assessment/exploratory request-budget
expiry on this copy. The cause was confirmed separately: six simultaneous requests
to the existing artifact cache validated the same **25,592,607-byte** real feature
artifact six times (29.187 s). `lru_cache` permits concurrent misses to execute
the reader repeatedly. A lock now covers cache lookup and validation/digest work.
The same six-request experiment performed one validation in **4.412 s**, returning
identical models. The cache remains bounded at eight entries with the existing
mtime/size key; every endpoint still performs current source/code/review identity
checks. Failures remain uncached. No scientific implementation hash or formula changed.
This specific experiment is not a universal application speedup claim.

After repair, a fresh Chromium browser/server run against the isolated genuine copy
passed cold restoration, actual backend interruption while the frontend stayed open,
restart/reconnect and warm reload. Measured separately:

| Operation | Seconds |
| --- | --- |
| Backend startup to healthy | 4.370 |
| Cold frontend load to usable inventory/current health | 2.401 |
| Cold selection to comparative findings and both native charts | 29.431 |
| Backend restart to healthy | 4.254 |
| Open frontend reconnect to current inventory/health | 3.937 |
| Warm frontend reload plus stored comparison restoration | 5.991 |

The restored JSON equaled its pre-restart JSON. Before cold selection, the owned API
process had 146,518,016 bytes working set and 862,019,584 bytes private memory;
afterward, 244,994,048 / 962,580,480 bytes. Peak working set at that point was
335,384,576 bytes. Process CPU accumulated from 3.9375 to 21.90625 CPU-seconds during
the 29.431 s selection (17.96875 CPU-seconds, distinct from wall time). These are
API-process measurements, not worker-tree memory or whole-machine CPU. The final
restarted process's peak working set was 375,246,848 bytes.
The measured 29.431 s spans sequential evidence requests; each retains its existing
15 s budget. A subsequent fresh genuine-layout bootstrap timed out after the repair,
so cold timeout remains reproducible on this host. Retry after validation completes
can restore evidence; no universal cold-load success is claimed. No timeout or
scientific safeguard was relaxed. Actual human perception and screen-reader speech
are not established by these browser checks.

## Failure and recovery

An actual owner browser remained open while its owned backend was stopped. Refresh
showed failed local requests and a reconnect action. The cached header still said
“Local workspace ready”: this was a reproduced presentation defect. Service status
now follows the current health request, announces connection failure, and retains
the explicit reconnect path. An automated controlled health failure/recovery test
passed, including axe with zero violations. Narrator/NVDA speech remains untested.

The reset regression initially used an uninitialized test directory and failed
startup correctly; it now uses the initialized recording fixture. An existing
crash/retry test first exceeded its unchanged 60 s budget under concurrent load;
a subsequent run completed processing but exceeded its 3 s cold-report request
budget. These failures are retained, not counted as passes or hidden by relaxing
timeouts. Final regression results will be recorded in the
[completion record](verification.md).
The unchanged crash/retry test subsequently passed alone (104.04 s); the focused
reset/concurrent-cache regressions passed together (two tests, 9.13 s).

Initial API failure was checked separately from failure after a successful mode check.
The safe startup guard correctly withheld operator views but had no in-app recovery;
it now times out at the existing 15 s request budget, announces an alert and rechecks
mode through a retry button. A unit retry into an active reviewer handoff still never
mounts operator views. Once the guard legitimately permits the operator shell, failed
inventory requests show unavailable rather than false zero/empty history. Six focused
browser failure/recovery/print cases passed in 50.9 s. This is software evidence,
not actual spoken Narrator/NVDA acceptance.

Private reproducibility records: `local-data/hardening-reliability.py`, six logs,
`hardening-reliability-results.json`, the isolated workspace, test traces and
fresh pilot SQLite telemetry. Keep these and audio outside public release files.
