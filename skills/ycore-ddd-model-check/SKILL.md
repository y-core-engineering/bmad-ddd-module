---
name: ycore-ddd-model-check
description: 'Checks code against the DDD domain model. Use when the user says "check the code against the domain model", "domain model check", "check epic 3 against glossary and context map", "does the codebase still respect the bounded contexts" or "bind the model check to the retrospective".'
---
# Domain model check

You answer whether the code reflects the domain model (glossary, Context Map, Design-Level per Bounded Context, invariants), a question that tests, `bmad-build` and `bmad-retrospective` do not ask: they check against the plan, and a plan can shorten the model. The consumer is the human at the gate after the build, who decides per finding whether the code is fixed, the model is updated or the deviation is accepted. You change no code and no model; you write the report, and an accepted deviation as one row in `{domain_model_folder}/accepted-deviations.md`.

## On activation

1. Customization: `uv run {project-root}/_bmad/scripts/resolve_customization.py --skill {skill-root} --project-root {project-root} --key workflow`; on any other failure read `{skill-root}/customize.toml` and use its defaults. Run each entry of `{workflow.activation_steps_prepend}`, hold every entry of `{workflow.persistent_facts}` as fact for the run (`file:` entries are paths or globs under `{project-root}` to read), then run each entry of `{workflow.activation_steps_append}`.
2. Config: `uv run {project-root}/_bmad/scripts/resolve_config.py --project-root {project-root} --key core.user_name --key core.communication_language --key core.output_folder --key core.document_output_language --key modules.ycore-ddd.domain_model_folder --key modules.ycore-ddd.review_folder`. Script not found: BMad is not set up here; offer the `bmad` skill's setup and run it again afterwards. If the `bmad` skill itself is missing, say so and point to the Installation section of the module's README; install nothing yourself. A `modules.ycore-ddd` key missing: the module was never set up; offer `bmad setup ycore-ddd`. Other missing keys take neutral defaults.
3. Headless (a `headless: true` flag, no interactive user, or a caller such as an unattended build loop or `bmad-retrospective` that pre-supplies the inputs): read `references/headless.md` fully and follow it for the whole run. Otherwise greet `{user_name}` in `{communication_language}` and stay in that language. When the request is a review of the diff itself rather than of its fit to the domain model, suggest `bmad-code-review` before continuing.

## Scope

When the request is only to bind the retrospective, follow the section on binding the retrospective and stop there; no check runs.

The mode comes from the request: `epic <name>` after an epic is built, `plan <file>` for one build plan, `range <base>..<head>`, or `codebase`, optionally narrowed to named contexts. When the request names none, propose `range` from the merge base with the default branch to `HEAD` and wait for a yes. For an epic, its folder is the one under `{output_folder}` that holds the epic's `tickets.toml` and build plans; ask when several match.

Which context a file belongs to comes from a table with a `Context` and a `Path` (or `Module`) column: `{domain_model_folder}/code-map.md` when it exists, otherwise such a table in the architecture document under `{output_folder}`. Without either, offer once to write `code-map.md` with the user: propose one row per context of `context-map.md` from the project's folders and write it on approval; declined, the checker assigns by judgment and the report says so.

Run `uv run {skill-root}/scripts/scope.py <mode> --repo {project-root} [--plans <epic folder> | --plan <file> | --range <a>..<b>] [--map <table file>]` and save its JSON beside the report as `.scope-{slug}.json`. When its range end is derived (`to_derived`), ask whether `HEAD` is the end of the work, and run it again with `--to <commit>` if not; its notes, such as a plan without a baseline, go to the report's frame. The report goes to `{review_folder}/domain-model-review-{slug}.md`, `{slug}` being `epic-<name>`, `plan-<stem>`, the short hashes of the range, or `codebase-<YYYY-MM-DD>`.

## Hand the check to a fresh context

Whoever built the code read the model while planning and the plan after that, and reads the code through the plan. A check run in that context inherits the blind spot it exists to catch, so the check runs in a subagent that has seen nothing of the build. Give it only:

- the instruction to read `{skill-root}/references/check.md` fully and follow it;
- project root, the scope JSON, contexts, `domain_model_folder`, `output_folder` (where BMad's architecture and planning documents live), the report language (`document_output_language`, otherwise the conversation's language) and the report path, every path absolute.

Leave out the build conversation, plan and spec files, and your own view of the code; each is a lens the checker should not borrow.

Without a subagent tool, say that a fresh session is the independent route and give the user the request for it. If they want it here anyway, read `references/check.md` and follow it yourself, and add "not independent of the builder" to the report's frame.

## Before presenting

Run `uv run {skill-root}/scripts/check_report.py --report <report path> --project-root {project-root}`. Gaps it lists (missing sections, findings without both locations, severity or boundary mark, checks neither run nor listed as not checked) go back to the subagent once, named. Then show its tally, every `high` finding, and the context-boundary findings apart from the rest, since they decide whether the next epic can build on the current boundaries. Give the report path.

## Decide

Go through every `high` and `medium` finding with the user, `high` first, one question each, through `AskUserQuestion` where available. Each question stands on its own: what the finding is about in plain words, its place in the code and its counterpart in the model by name, the ID only in brackets, and a plain-word header. The user chooses:

- fix in code: the follow-up is a change for `bmad-build`, or `bmad-correct-course` when it reaches across several tickets;
- update model: the code learned something the model lacks or has wrong; the follow-up is an update with `ycore-ddd-design-level` for the context, or with `ycore-ddd-big-picture` when a context-boundary finding questions the cut;
- accept deviation: with the user's reason, appended as the next `DEV-##` row to `{domain_model_folder}/accepted-deviations.md` (`| ID | Finding | Report | Deviation | Reason | Date |`, created with that header when missing), so later checks do not report it again.

List the `low` findings together; the user decides them together or leaves them open. Write a `## Decisions` table `| Finding | Decision | Follow-up |` into the report, one row per decided finding, set its frontmatter to `status: final`, and run `check_report.py` again with `--require-decisions` until it reports nothing missing.

## Afterwards

Offer the follow-ups the decisions named, and `bmad-retrospective` when the epic is otherwise complete. Then run `{workflow.on_complete}` when it is not empty; to change it, invoke the `bmad-customize` skill and name `workflow.on_complete`, saying so when it is not installed.

After the first final report, offer once to bind the retrospective, unless it is bound already.

## Binding the retrospective

A module cannot ship an override for another skill, so the binding is made per project, at setup or later. It is in place when `{project-root}/_bmad/custom/bmad-retrospective.toml` contains the line that starts with "ycore-ddd domain model check"; then say so and change nothing. Otherwise check that `bmad-retrospective` and `bmad-customize` are installed, and name what is missing with a pointer to the Installation section of the module's README. Then invoke the `bmad-customize` skill to append the text of `{skill-root}/assets/retrospective-step.md` to `workflow.activation_steps_append` of `bmad-retrospective` as a team override, and tell the user what it does: every retrospective reads this check's report for its epic, runs the check headless when the report is missing, and does not accept an epic with an undecided high finding. You read that file but never write under `_bmad/custom/` yourself; removing the binding also goes through `bmad-customize`.
