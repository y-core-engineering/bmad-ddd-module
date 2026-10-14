# Headless

No interactive user, typically an unattended build loop after an epic or `bmad-retrospective` looking for the report: ask nothing, wait for no yes, invent nothing. The check itself is unchanged; the questions to the human and the decisions fall away. Config, `{skill-root}` and the report path come from the skill's activation.

Take mode, epic folder, plan, range and contexts from the first message. Without a mode, use `range` from the merge base with the default branch to `HEAD` and record that as an assumption. Run `scope.py` as the skill describes, with the code map when one exists; without one, never write it, and let the checker assign by judgment. A derived range end stays `HEAD` and is recorded as an assumption. A scope that cannot be determined, or an empty one, ends the run `blocked` with the reason.

Hand the check to a fresh-context subagent exactly as the skill describes; without a subagent tool, run it inline and mark the report "not independent of the builder". Run `uv run {skill-root}/scripts/check_report.py --report <report path> --project-root {project-root}` and send its gaps back to the subagent once; the check of the report is never skipped. Gaps that remain go into `open_questions`.

Decisions need the user: the report stays `status: draft`, and every `high` and `medium` finding is listed in `decisions_pending` for whoever reads this output.

End with JSON only, leaving out keys for what was not produced:

```json
{
  "status": "complete | partial | blocked",
  "mode": "epic <name> | plan <file> | range <base>..<head> | codebase",
  "report": "<report path>",
  "scope": "<path of the scope JSON>",
  "tally": {"total": 0, "by_check": {}, "by_severity": {}, "boundary": 0},
  "high": ["FM-<n>: <finding in one sentence>"],
  "boundary": ["FM-<n>: <finding in one sentence>"],
  "decisions_pending": ["FM-<n>"],
  "independent": true,
  "mapped": true,
  "assumptions": [],
  "open_questions": [],
  "reason": "<one line, only when blocked>"
}
```

`complete` means the report passed its check; `partial` means it was written but gaps remain; `blocked` means no report. `mapped` is false when no code map assigned the files.
