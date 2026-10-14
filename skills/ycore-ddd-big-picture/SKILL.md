---
name: ycore-ddd-big-picture
description: 'Runs a Big-Picture Event Storming for strategic DDD with an agent team. Use when the user says "big picture event storming", "find the bounded contexts", "strategic DDD for this product" or "build the context map and ubiquitous language".'
---
# Big-Picture Event Storming

You prepare and facilitate a Big-Picture Event Storming for strategic DDD: from a product idea to Domain Events on a timeline, subdomains, Bounded Contexts, a Context Map and a glossary per context. The consumers are BMad's PRD and architecture, a later Design-Level per context, and `ycore-ddd-model-check`, which holds the code against these files; so every context boundary carries its reason, every domain statement goes back to the idea or to the user, and every open question stands as a Hotspot instead of an assumption. You moderate and synthesise; domain content comes from the user and the team, never from you.

## On activation

1. Config: `uv run {project-root}/_bmad/scripts/resolve_config.py --project-root {project-root} --key core.document_output_language --key modules.ycore-ddd.domain_model_folder`. Script not found: BMad is not set up here; offer the `bmad` skill's setup, installing `bmad` first if needed (`npx skills add bmad-code-org/BMAD-METHOD --skill bmad`), then run it again. `domain_model_folder` missing: offer `bmad setup ycore-ddd`.
2. Artifacts are written in `document_output_language` (English when unset); method terms (Domain Event, Command, Policy, Read Model, Bounded Context, Context Map, Hotspot) and sticky IDs stay in English.

## Where the run stands

The state lives in `{domain_model_folder}`, so a run continues in a new session:

- No `workshop-brief.md`: preparation, resuming from `interview-log.md` when one exists. Read `references/prepare.md` fully and follow it. The brief is written only on the user's approval, so an existing brief counts as approved.
- `workshop-brief.md` and no `board.md`, or a `board.md` whose first line is `Status: round <N> | …`, `Status: checkpoint | …` or `Status: revision <N> | …`: facilitation, continuing from that state. A `board.md` without such a line: ask the user which round was last merged. Read `references/facilitate.md` fully and follow it.
- `board.md` with `Status: done | …`: the storming is done. Say so with the artifact paths. A revision the user asks for runs as one more round on the named part: set the status to `Status: revision <N> | <part>`, N being the next round number, and follow `references/facilitate.md`.

When this session has already finished the preparation or a full round, say so in one sentence before starting the next round; whether to continue in a fresh session is the user's call.

## Afterwards

Offer `bmad-prd` with `event-storming.md`, `context-map.md` and `ubiquitous-language.md` as inputs. Name the Core contexts that need a Design-Level next; this module does not run one yet, and `ycore-ddd-model-check` needs its result as `<context>/design.md` (context name in kebab-case) with Commands carrying `may:` and Aggregates carrying `❗` invariants.
