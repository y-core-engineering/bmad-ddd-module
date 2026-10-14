# Reviewer gate

The pre-handover review of the Big-Picture artifacts, run when `board.md` says `Status: review | …` and under the validate intent. The outcome differs: at handover you apply the clear fixes and set the status to `done`; under validate you change nothing and deliver a report. `{domain_model_folder}`, `{skill-root}`, the memlog command and `{workflow.finalize_reviewers}` come from the skill's activation.

Run the deterministic pass first, `uv run {skill-root}/scripts/check_artifacts.py --folder {domain_model_folder}`, so the reviewers spend their judgment on meaning rather than format.

Then dispatch every entry of `{workflow.finalize_reviewers}` as a parallel subagent (an entry prefixed `skill:` invokes that skill, `file:` loads its lens from that file, plain text is the lens itself), plus any lens the stakes warrant, such as regulation for a regulated domain. Each reviewer gets the paths of `context-map.md`, `ubiquitous-language.md`, `event-storming.md`, `board.md`, `workshop-brief.md`, the idea and the memlog, never this conversation: a fresh context finds what the facilitator talks past. Each writes its full review to `{domain_model_folder}/reviews/big-picture-review-<lens-slug>.md` (under validate `…-validation-<lens-slug>.md`, so a validation never overwrites the handover reviews) and returns only its verdict, its top two to five findings and the file path. The configured lenses always run, also headless; without a subagent tool, run them one after another and note in the memlog that they were not independent.

## At handover

Apply what changes no domain content: a missing source link, a name spelled two ways, a table cell left empty that the board answers. A finding that needs a domain answer (a boundary, a term, a protection need, a pattern) is not yours to settle: make it a Hotspot on the board, log it, set the status back to `checkpoint` and stop here: the skill routes again and loads the checkpoint rules, which put it to the user. Log every applied fix.

When no finding is left that needs the user, run the script again, set the status to `done` and log the event. Then tell the user, tiered: one sentence of verdict, the fixes applied, and where the full reviews lie.

## Validate

Change no artifact. Fold the reviews into one report at `{domain_model_folder}/reviews/big-picture-validation-<YYYY-MM-DD>.md`: the verdict in one sentence, then critical and high findings with location and source, then the rest as a short tail with the review files named. Show its path and offer an update, which runs the findings as a revision round.
