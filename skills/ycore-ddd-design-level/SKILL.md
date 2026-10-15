---
name: ycore-ddd-design-level
description: 'Runs Design-Level Event Storming per Bounded Context. Use when the user says "design level event storming", "design the aggregates for <context>", "find the invariants of a bounded context" or "tactical DDD for a bounded context". Not for finding the contexts of a product, checking code against the model, or implementing, testing or storing aggregates in code.'
---
# Design-Level Event Storming

You turn the Big-Picture map into tactical design, one Bounded Context at a time: Commands with who may issue them, Aggregates with their invariants, Events, Policies, Read Models, External Systems behind ACLs, and the abuse cases an attacker would try. The consumers are BMad's architecture and build skills, which implement from `design.md`, and `ycore-ddd-model-check`, which holds the code against it; so every invariant names its Aggregate and its source, every Command its permission, every abuse case its defence, and an invariant that rests on an open domain question is a Hotspot, not a rule. You moderate and synthesise; domain content comes from the user and the team.

## On activation

1. Customization: `uv run {project-root}/_bmad/scripts/resolve_customization.py --skill {skill-root} --project-root {project-root} --key workflow`; on any other failure read `{skill-root}/customize.toml` and use its defaults. Run each entry of `{workflow.activation_steps_prepend}`, hold every entry of `{workflow.persistent_facts}` as fact for the run (`file:` entries are paths or globs under `{project-root}` to read), then run each entry of `{workflow.activation_steps_append}`.
2. Config: `uv run {project-root}/_bmad/scripts/resolve_config.py --project-root {project-root} --key core.user_name --key core.communication_language --key core.document_output_language --key modules.ycore-ddd.domain_model_folder`. Script not found: BMad is not set up here; offer the `bmad` skill's setup and run it again afterwards. If the `bmad` skill itself is missing, say so and point to the Installation section of the module's README; install nothing yourself. `domain_model_folder` missing: offer `bmad setup ycore-ddd`. Other missing keys take neutral defaults.
3. Headless (a `headless: true` flag, no interactive user, or a first message that pre-supplies every input and asks only for paths back): read `references/headless.md` fully, together with the references the route below names, for a full context also `references/design-format.md` and `references/reviewer-gate.md`, for validate `references/reviewer-gate.md`, and follow it for the whole run. Otherwise greet `{user_name}` in `{communication_language}`, stay in that language for every turn, and say once that `bmad-party-mode` and `bmad-advanced-elicitation` can be invoked at any point. When the request belongs elsewhere (finding the contexts: `ycore-ddd-big-picture`; technology and structure: `bmad-architecture`; code: `bmad-build`), suggest that skill before continuing.
4. Artifacts are written in `document_output_language`, or in the language of the conversation when it is unset; method terms (Command, Aggregate, Invariant, Domain Event, Policy, Read Model, ACL, Bounded Context, Hotspot) and IDs stay in English. The Big-Picture IDs (`BC##`, `E##`, `H##`, `X##`) are adopted, never renumbered.

## Memory

Every answer, decision, Hotspot outcome, override and assumption is one line in a memlog, written as it happens and only through `uv run {project-root}/_bmad/scripts/memlog.py append --path <memlog> --type <decision|change|override|assumption|event> --by <user|facilitator> --text "<one line, reason included>"`. When the memlog does not exist yet, create it first with `uv run {project-root}/_bmad/scripts/memlog.py init --path <memlog> --field topic="<what it covers>"`. The catalog's memlog is `{domain_model_folder}/design-level.memlog.md`, a context's is `{domain_model_folder}/<folder>/design.memlog.md`. A resumed session reads them back.

## Intent and state

Route on the intent first, then on `uv run {skill-root}/scripts/check_design.py --folder {domain_model_folder} --status`. When a reference ends by setting a new status, run `--status` again and route again from this list.

- Validate (critique without changing): read `references/reviewer-gate.md` fully and follow its report mode for the contexts the user names, or every context with a `design.md`.
- Update a named context whose `done` is true: set its board to `BC: <ID> <name> | Status: revision <N> | <part>`, N being the next round number, and follow `references/facilitate.md`. Promote a lean context: on the user's word set its catalog row to `full` with an Order, log it, and start its run at round 1 with the lean design as input.
- Create, the default:
  - `catalog` false, `catalog_draft` true, or `catalog_problems` or `catalog_stale` not empty: the catalog, new, approved from a draft, or revised. Read `references/catalog.md` fully and follow it.
  - The target is the context the user names, otherwise `next_target`; say which, and in the Coaching path wait for a yes, while the Fast path (the catalog's `Working mode`) starts it. For a `full` context with `board_status` empty, a round, `revision` or `checkpoint`, or `done` while `design_ok` is false (then set it back to `checkpoint`): read `references/facilitate.md` fully and follow it; from the checkpoint on, also `references/design-format.md`. With `review`: read `references/reviewer-gate.md` and `references/design-format.md` fully and follow them. With `unreadable`: ask the user which round was last merged and rewrite the first line of its `board.md`.
  - A `lean` context that is not done: read `references/design-format.md` fully and follow its lean section.
  - `all_done`: the Design-Level is done; say so with the paths.

In the Coaching path, before starting a round in a session that has already finished the catalog or a full round, say so in one sentence; whether to continue in a fresh session is the user's call. In the Fast path the run goes on without that pause.

## Afterwards

Once `all_done` is true, offer `bmad-spec` with the `design.md` files, the Big-Picture artifacts and the points under `Open for spec` as input. When several people, agents or sessions will build parts that must fit, offer `bmad-architecture` before it: the Context Map gives the major boundaries, and it should record a `Context`/`Path` table, which `ycore-ddd-model-check` later reads. Work larger than one build session goes from the spec through `bmad-ticket` to `bmad-build`; offer `ycore-ddd-model-check` once code exists. Then run `{workflow.on_complete}` when it is not empty. To change the reviewer lenses or the closing step, invoke the `bmad-customize` skill and name `workflow.finalize_reviewers` or `workflow.on_complete`; if it is not installed, say so.
