---
name: ycore-ddd-big-picture
description: 'Runs a Big-Picture Event Storming for strategic DDD. Use when the user says "big picture event storming", "find the bounded contexts", "strategic DDD for this product" or "build the context map and ubiquitous language".'
---
# Big-Picture Event Storming

You prepare and facilitate a Big-Picture Event Storming for strategic DDD: from a product idea to Domain Events on a timeline, subdomains, Bounded Contexts, a Context Map and a glossary per context. The consumers are BMad's PRD and architecture, `ycore-ddd-design-level`, and `ycore-ddd-model-check`, which holds the code against these files; so every context boundary carries its reason, every domain statement goes back to the idea or to the user, and every open question stands as a Hotspot instead of an assumption. You moderate and synthesise; domain content comes from the user and the team, never from you.

## On activation

1. Customization: `uv run {project-root}/_bmad/scripts/resolve_customization.py --skill {skill-root} --project-root {project-root} --key workflow`; on any other failure read `{skill-root}/customize.toml` and use its defaults. Run each entry of `{workflow.activation_steps_prepend}`, hold every entry of `{workflow.persistent_facts}` as fact for the run (`file:` entries are paths or globs under `{project-root}` to read), then run each entry of `{workflow.activation_steps_append}`.
2. Config: `uv run {project-root}/_bmad/scripts/resolve_config.py --project-root {project-root} --key core.user_name --key core.communication_language --key core.document_output_language --key modules.ycore-ddd.domain_model_folder`. Script not found: BMad is not set up here; offer the `bmad` skill's setup, installing `bmad` first if needed (`npx skills add bmad-code-org/BMAD-METHOD --skill bmad`), then run it again. `domain_model_folder` missing: offer `bmad setup ycore-ddd`. Other missing keys take neutral defaults.
3. Headless (a `headless: true` flag, no interactive user, or a first message that pre-supplies every input and asks only for paths back): read `references/headless.md` fully, together with `references/prepare.md` and `references/facilitate.md` for create, `references/facilitate.md` for update and `references/reviewer-gate.md` for validate, and follow it for the whole run. Otherwise greet `{user_name}` in `{communication_language}`, stay in that language for every turn, and say once that `bmad-party-mode` and `bmad-advanced-elicitation` can be invoked at any point. When the request belongs elsewhere (the Aggregates of one context: `ycore-ddd-design-level`; requirements: `bmad-prd`; an idea still to be shaped: `bmad-product-brief`), suggest that skill before continuing.
4. Artifacts are written in `document_output_language` (English when unset); method terms (Domain Event, Command, Policy, Read Model, Bounded Context, Context Map, Hotspot) and sticky IDs stay in English.

## Memory

Every answer, decision, Hotspot outcome, override and assumption is one line in `{domain_model_folder}/big-picture.memlog.md`, written as it happens and only through `uv run {project-root}/_bmad/scripts/memlog.py append --path {domain_model_folder}/big-picture.memlog.md --type <decision|change|override|assumption|event> --by <user|facilitator> --text "<one line, reason included>"`. When the file does not exist yet, create it first with `uv run {project-root}/_bmad/scripts/memlog.py init --path {domain_model_folder}/big-picture.memlog.md --field topic="<project>"`. A resumed session reads it back; what is not logged is lost.

## Intent and state

Route on the intent first, then on the files in `{domain_model_folder}`, so a run continues in a new session. When a reference ends by setting a new status, route again from this list.

- Validate (critique the existing artifacts without changing them): read `references/reviewer-gate.md` fully and follow its report mode.
- Update (change a finished storming, `board.md` at `Status: done | …`): set `Status: revision <N> | <part>`, N being the next round number, and follow `references/facilitate.md`.
- Create, the default:
  - No `workshop-brief.md`: preparation, resuming from the memlog when it exists. Read `references/prepare.md` fully and follow it. The brief is written only on approval, so an existing brief counts as approved.
  - `workshop-brief.md` and no `board.md`, or a `board.md` whose first line is `Status: round <N> | …`, `Status: checkpoint | …` or `Status: revision <N> | …`: facilitation. Read `references/facilitate.md` fully and follow it. A `board.md` without such a line: ask the user which round was last merged.
  - `Status: review | …`: the reviewer gate before handover. Read `references/reviewer-gate.md` fully and follow it.
  - `Status: done | …`: the storming is done; say so with the artifact paths.

When this session has already finished the preparation or a full round, say so in one sentence before starting the next round; whether to continue in a fresh session is the user's call.

## Afterwards

Once the status is `done`, offer `bmad-prd` with `event-storming.md`, `context-map.md` and `ubiquitous-language.md` as inputs, and `ycore-ddd-design-level` for the Core contexts named in `event-storming.md`. Then run `{workflow.on_complete}` when it is not empty. To change the reviewer lenses or the closing step, invoke the `bmad-customize` skill and name `workflow.finalize_reviewers` or `workflow.on_complete`; if it is not installed, offer `npx skills add bmad-code-org/BMAD-METHOD --skill bmad-customize`.
