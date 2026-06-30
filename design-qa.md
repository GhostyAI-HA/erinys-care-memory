# Design QA: Answer Diff Bench

final result: passed

source visual truth path: `/Users/fujiyoshi/work/hackathons/qwen-cloud-2026/qwen-cloud-hackathon-2026/submissions/track1-erinys-memoryagent/docs/design/gui-concept-04-answer-diff-bench.png`

implementation screenshot path: `/Users/fujiyoshi/work/hackathons/qwen-cloud-2026/qwen-cloud-hackathon-2026/submissions/track1-erinys-memoryagent/docs/design/implementation-answer-diff-bench.png`

full-view comparison evidence: `/Users/fujiyoshi/work/hackathons/qwen-cloud-2026/qwen-cloud-hackathon-2026/submissions/track1-erinys-memoryagent/docs/design/design-qa-comparison-answer-diff.png`

viewport: 1440 x 1024

state: default demo state after the app auto-runs the care visit benchmark.

focused region comparison evidence: not needed. The screen is a single dense dashboard view, and the important fidelity surfaces are all visible in the full-view comparison.

## Findings

No P0, P1, or P2 issues remain.

The implementation preserves the intended product structure: caregiver prompt first, then the same-prompt answer comparison, then a side Memory Decisions panel and token efficiency strip. The three answer columns are now the visual center, and the Raw Memory / ERINYS + Qwen difference is visible without reading explanatory prose.

## Required Fidelity Surfaces

Fonts and typography: passed. The implementation uses a system sans stack with a similar product UI feel, readable 13-16px body sizing, clear headings, and no visible wrapping failures.

Spacing and layout rhythm: passed. The prompt area was tightened after QA so the first viewport prioritizes the comparison. The implementation has a slightly cleaner and less icon-heavy top section than the source mock, which is acceptable for reducing explanatory density.

Colors and visual tokens: passed. Neutral base surfaces, teal/green success states, red risk highlights, and muted blue comparison banner match the source intent.

Image quality and asset fidelity: passed with intentional simplification. The source mock uses small icon marks; the implementation uses text badges and simple product marks to avoid adding an icon dependency. No raster assets are required for the app screen.

Copy and content: passed. The app-specific text now foregrounds the answer diff. Raw Memory uses synthetic unsafe details only; ERINYS + Qwen keeps the response in clinic visit preparation and avoids diagnosis or treatment advice.

## Patches Made Since QA

- Reduced prompt panel height and page spacing so the comparison appears earlier in the first viewport.
- Updated Raw Memory mock output to include synthetic private identifier/address and stale train/ramen routine.
- Added editable chat prompt, three answer cards, transformation column, persistent Memory Decisions panel, and token efficiency strip.
- Updated `gui-user-stories.csv` with post-fix status and retest notes.

## Follow-Up Polish

- P3: The source mock shows 73% fewer context tokens, while the current live seed shows 29%. This does not block the UI handoff, but the demo can be made stronger by adding more irrelevant/stale/sensitive memory records to the seed or by tuning selected-memory thresholds.
