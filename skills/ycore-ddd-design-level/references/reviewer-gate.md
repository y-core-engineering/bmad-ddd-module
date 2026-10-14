# Reviewer gate

The pre-handover review of a full context's `design.md`, run when its `board.md` says `Status: review | …`, and under the validate intent for the contexts the user names or all of them. At handover you apply the clear fixes and set the status to `done`; under validate you change nothing and deliver a report. `{domain_model_folder}`, `{skill-root}`, the memlog command and `{workflow.finalize_reviewers}` come from the skill's activation; `{bc}` is the context's folder.

Run the deterministic pass first, `uv run {skill-root}/scripts/check_design.py --folder {domain_model_folder} --context {bc}`, so the reviewers spend their judgment on meaning rather than format.

Then dispatch every entry of `{workflow.finalize_reviewers}` as a parallel subagent (an entry prefixed `skill:` invokes that skill, `file:` loads its lens from that file, plain text is the lens itself), plus any lens the stakes warrant, such as a regulation lens for a regulated context. Each reviewer gets the paths of `{bc}/design.md`, `{bc}/board.md`, the context's memlog, `design-level-catalog.md`, `context-map.md` and `ubiquitous-language.md`, never this conversation: a fresh context finds what the facilitator talks past. Each writes its full review to `{domain_model_folder}/reviews/{bc}-review-<lens-slug>.md` (under validate `…-validation-<lens-slug>.md`, so a validation never overwrites the handover reviews) and returns only its verdict, its top two to five findings and the file path. The configured lenses always run, also headless; without a subagent tool, run them one after another and note in the memlog that they were not independent.

## At handover

Apply what changes no domain content: a missing source, a term spelled unlike the glossary, an ID that does not resolve. A finding that needs a domain answer (an Aggregate boundary, an invariant, a permission, a defence) is not yours to settle: make it a Hotspot on the board, log it, set the status back to `checkpoint` and stop here: the skill routes again and loads the checkpoint rules, which put it to the user. Log every applied fix.

When no finding is left that needs the user, run the check again, set the status to `done` and log the event. Tell the user, tiered: one sentence of verdict, the fixes applied, where the full reviews lie, and the next context from `--status`.

## Validate

Change no artifact; only the reviews and the report are written. Run the gate for each named context, or every context with a `design.md`, and fold the reviews into one report at `{domain_model_folder}/reviews/design-level-validation-<YYYY-MM-DD>.md`: the verdict in one sentence, then critical and high findings with context, location and source, then the rest as a short tail with the review files named. Show its path and offer an update, which runs the findings as a revision round of the affected context.
