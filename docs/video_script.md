# Three-Minute Demo Video Script

## Goal

Show that ERINYS Care Memory is not a generic chatbot. It is a memory-governance layer for Qwen Cloud agents.

Recording URL:

```text
http://127.0.0.1:5173/?video=1
```

Use the normal URL for judge interaction and `?video=1` for the compact 16:9 recording layout.

## 0:00-0:20 Opening

Narration:

> This is ERINYS Care Memory, a MemoryAgent for Qwen Cloud. The problem is simple: long-running assistants should not append every memory they retrieve. Some memories are current, some are stale, some conflict, and some are private.

Screen:

- Show the app title.
- Point to `Qwen Cloud live` and `ERINYS Care Memory v1.0.0`.

## 0:20-0:50 Same Prompt Setup

Narration:

> I send the same caregiver request through three memory strategies. The user asks for an exact door-to-door clinic plan, but also says not to invent missing details.

Screen:

- Show the prompt.
- Show the banner: `Same prompt, three memory strategies`.

## 0:50-1:15 Persistent Memory Proof

Narration:

> Before comparing answers, I save a new caregiver note. This proves the app is not just reading a fixed prompt. The note is persisted, loaded again, and used by the governed answer.

Screen:

- Show `Persistent memory proof`.
- Save: `Ask reception to arrange wheelchair assistance at the north entrance before check-in.`
- Show `Persistent memory saved as u001` and the persisted memory count.

## 1:15-1:35 No Memory

Narration:

> First, this is Qwen without personal memory. This answer is safe, but it is not useful enough for a real caregiver. It cannot know the pickup time, the check-in time, the accessible entrance, or what documents were forgotten last time. So no memory means low risk, but also low actionability.

Screen:

- Show No Memory card.
- Highlight `Cannot know exact timing`.

## 1:35-2:05 Raw Memory

Narration:

> Now watch the raw memory baseline. It becomes more confident, but not more reliable. Because every retrieved memory is passed directly to Qwen, stale routes, old appointment assumptions, and synthetic private identifiers enter the plan. This is the realistic failure mode: the model is not dumb, the memory layer is ungoverned.

> In other words, more memory alone does not make an agent safer. It can make the wrong answer more detailed.

Screen:

- Scroll to Raw Memory.
- Highlight `Private IDs may leak` and stale route.

## 2:05-2:40 ERINYS + Qwen

Narration:

> This is the ERINYS-governed answer. Before Qwen generates anything, ERINYS decides which memories are current, useful, and safe. It selects the 13:35 taxi pickup, the 14:20 check-in, the medication notebook, and the newly persisted wheelchair assistance note. It blocks synthetic private IDs and keeps stale train and stair routes out of the prompt.

> The result is the important difference: Qwen can still give a concrete plan, but it no longer needs to see every raw memory. The answer becomes safer, more current, and more token-efficient.

Screen:

- Show ERINYS + Qwen card.
- Show Memory Decisions panel.
- Show `64% fewer tokens`.

## 2:40-2:58 Memory Decision Proof

Narration:

> The right panel is the audit trail. This is not just prompt wording. ERINYS produces explicit memory decisions: selected, conflict, demoted, and blocked. That means a reviewer can inspect why a memory was used or withheld before it ever reaches Qwen.

> The backend exposes the same proof through APIs: `/health` shows Qwen Cloud live mode, `/memories` shows persisted memory, and `/run/governance` returns every decision without another generation call.

Screen:

- Show terminal or docs with the two endpoints.

## 2:58-3:10 Close

Narration:

> The point of this project is simple: the future of memory agents is not just larger memory. It is governed memory. ERINYS Care Memory gives Qwen Cloud agents a memory layer that can persist useful context, reject dangerous context, and explain the decision before generation.

> The live demo URL lets judges save a synthetic memory and rerun this comparison themselves.
