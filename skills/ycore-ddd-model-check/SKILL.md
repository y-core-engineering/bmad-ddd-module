---
name: ycore-ddd-model-check
description: 'Checks code against the DDD domain model. Use when the user says "check the code against the domain model", "domain model check", "check epic 3 against glossary and context map" or "does the codebase still respect the bounded contexts".'
---
# Domain model check

You answer whether the code reflects the domain model (glossary, Context Map, Design-Level per Bounded Context, invariants), a question that tests, `bmad-build` and `bmad-retrospective` do not ask: they check against the plan, and a plan can shorten the model. The consumer is the human at the gate after the build, who decides per finding whether code or model gives way; the report is the only file this skill changes.

## On activation

1. Customization: `uv run {project-root}/_bmad/scripts/resolve_customization.py --skill {skill-root} --project-root {project-root} --key workflow`; on any other failure read `{skill-root}/customize.toml` and use its defaults. Run each entry of `{workflow.activation_steps_prepend}`, hold every entry of `{workflow.persistent_facts}` as fact for the run (`file:` entries are paths or globs under `{project-root}` to read), then run each entry of `{workflow.activation_steps_append}`.
2. Config: `uv run {project-root}/_bmad/scripts/resolve_config.py --project-root {project-root} --key core.user_name --key core.communication_language --key core.output_folder --key core.document_output_language --key modules.ycore-ddd.domain_model_folder --key modules.ycore-ddd.review_folder`. Script not found: BMad is not set up here; offer the `bmad` skill's setup, installing `bmad` first if needed (`npx skills add bmad-code-org/BMAD-METHOD --skill bmad`), then run it again. A `modules.ycore-ddd` key missing: the module was never set up; offer `bmad setup ycore-ddd`. Other missing keys take neutral defaults.
3. Headless (a `headless: true` flag, no interactive user, or a caller such as an unattended build loop that pre-supplies the inputs): read `references/headless.md` fully and follow it for the whole run. Otherwise greet `{user_name}` in `{communication_language}` and stay in that language. When the request is a review of the diff itself rather than of its fit to the domain model, suggest `bmad-code-review` before continuing.
4. Mode and subject, from the request: `epic <n>` after a build or retrospective, `range <base>..<head>` for a commit range, `codebase` for the main branch as a whole, optionally narrowed to named Bounded Contexts. When the request names none, propose `range` from the merge base with the default branch to `HEAD` and wait for a yes. The report goes to `{review_folder}/domain-model-review-{slug}.md`, `{slug}` being `epic-<n>`, the short hashes of the range, or `codebase-<YYYY-MM-DD>`.

## Hand the check to a fresh context

Whoever built the code read the model while planning and the plan after that, and reads the code through the plan. A check run in that context inherits the blind spot it exists to catch, so the check runs in a subagent that has seen nothing of the build. Give it only:

- the instruction to read `{skill-root}/references/check.md` fully and follow it;
- project root, mode, subject, contexts, `domain_model_folder`, `output_folder` (where BMad's architecture and planning documents live), the report language (`document_output_language`, English when unset) and the report path, every path absolute.

A checker that returns an empty subject gets a `range <base>..<head>` from the user and runs again. Leave out the build conversation, story and spec files, and your own view of the code; each is a lens the checker should not borrow.

Without a subagent tool, say that a fresh session is the independent route and give the user the request for it. If they want it here anyway, read `references/check.md` and follow it yourself, and add "not independent of the builder" to the report's frame.

## Before presenting

Run `uv run {skill-root}/scripts/check_report.py --report <report path> --project-root {project-root}`. Gaps it lists (missing sections, findings without both locations, severity or boundary mark, checks neither run nor listed as not checked) go back to the subagent once, named. Then show its tally, every `high` finding, and the context-boundary findings apart from the rest, since they decide whether the next epic can build on the current boundaries. Give the report path. Per finding, code giving way is a change for `bmad-build`, the model giving way an update of the `design.md` or glossary; put that choice to the human. Then run `{workflow.on_complete}` when it is not empty; to change it, invoke the `bmad-customize` skill and name `workflow.on_complete`, offering `npx skills add bmad-code-org/BMAD-METHOD --skill bmad-customize` when it is not installed.
