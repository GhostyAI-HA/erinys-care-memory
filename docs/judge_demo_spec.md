# Judge Demo Spec

## One-Line Demo

ERINYS Care Memory shows how Qwen answers improve when memory is governed
instead of blindly appended.

## User Request

```text
Draft the exact door-to-door plan for tomorrow's clinic visit using only what
you remember. Include timing, transport, what to bring, questions to ask, and
what not to expose. If you lack the memory, say what cannot be known instead
of giving a generic checklist.
```

## What Judges See

1. No Memory: competent but honest; it cannot know exact timing or transport.
2. Raw Memory: plausible RAG failure; stale routes, conflicts, and synthetic
   IDs enter the plan.
3. ERINYS + Qwen: critical care context is selected, old routines are demoted,
   sensitive memories are blocked, and Qwen generates the safer exact plan.

## Winning Moment

The Memory Audit board shows:

```text
selected: 13:35 taxi pickup, 14:20 check-in, medication notebook, stair avoidance
demoted: old entrance/weather/accessory memories
contradiction: old 09:00/8:10 train routine conflicts with the newer taxi decision
blocked: synthetic insurance ID, synthetic home address
```

Then Qwen produces a plan that uses only the selected memories.
