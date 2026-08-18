# VibePulse Round 1.75C — screen-shape contract

Status: implementation target for the `codex/round-1.75c-port` branch. This is a simulator-first contract; no behavior is physically verified on the round board yet.

## Surface and intent

- Surface: 466×466 circular AMOLED (Waveshare ESP32-S3-Touch-AMOLED-1.75C).
- Mode: Operate. The device is a glanceable agent-status display first and a small action surface second.
- Primary intent: answer “what needs my attention?” and “how much capacity remains?” without opening the Mac.
- Data shape: eight peer pages, each centered on one dominant state or metric with at most three supporting facts.

## Chosen form

- Keep the existing full-screen paged carousel: one task or metric page at a time.
- Preserve horizontal swipe navigation and the compact bottom pager.
- Keep the launcher as a deliberate full-screen takeover reached from the provider/app identity control.
- Keep `Needs You` as the only blocking full-screen takeover. Its action choices remain explicit buttons, never hidden gestures.
- Preserve the established true-black, IBM Plex, Claude orange, and Codex indigo visual language.

The round adaptation is a reflow, not a scale-down. The display center holds the hero state. Identity moves into the narrower upper arc, supporting facts occupy the broad lower-middle band, and the pager sits in the narrow lower arc.

## Geometry rules

- Framebuffer: 466×466; circle center `(233, 233)`; physical radius `233`.
- No meaningful content may depend on corner pixels. The simulator must visibly clip the UI to the circular panel.
- Primary safe content band: `x=36..430`, `y=52..414`.
- Upper identity/control content must fit inside `x=92..374` by `y=48`.
- Hero metrics should remain centered within `y=116..278`.
- Supporting labels, progress, and reset information should remain within `y=286..402`.
- Pager/control affordances should remain centered and compact at `y=420..448`.
- Minimum touch target remains 44×44 logical pixels; edge targets must not cross the visible circular boundary.

## State and disclosure

- Live, cached/stale, partial, no-data, loading, and error remain distinct states.
- Missing values render as dashes or an explicit unavailable label; the UI must never invent zero.
- One level of nesting is allowed: launcher → selected app/page. A blocking takeover may temporarily replace that level.
- The current page is session state only unless the existing firmware already persists it.

## Rejected forms

- A multi-card home dashboard: too much information collides with the circular edge and weakens glanceability.
- Uniformly scaling the 480×480 square layout: makes labels and touch targets smaller while still losing content at the corners.
- A vertically scrolling status list: requires more attention and touch precision than a desk display should.

## Acceptance evidence

- Square simulator behavior and captures remain unchanged under the default profile.
- A selectable round simulator profile renders at exactly 466×466 with black/absent corners.
- Static captures cover live, partial, stale, no-data, error, launcher, GitHub, value, tracker, and `Needs You` states.
- Automated tests prove profile dimensions and circular clipping; exact raster inspection confirms no meaningful content is cut by the panel edge.
- Hardware, touch mapping, buttons, brightness, sleep/wake, and power behavior remain labeled unverified until tested on the delivered board.
