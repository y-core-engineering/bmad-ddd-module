# Headless

No interactive user, typically an unattended build loop after an epic: ask nothing, wait for no yes, invent nothing. The check itself is unchanged; only the questions to the human fall away. Config, `{skill-root}` and the report path come from the skill's activation.

Take mode, subject and contexts from the first message. Without a mode, use `range` from the merge base with the default branch to `HEAD` and record that as an assumption. Hand the check to a fresh-context subagent exactly as the skill describes; without a subagent tool, run it inline and mark the report "not independent of the builder". An empty subject ends the run `blocked` with the reason, since no range can be asked for.

Run `uv run {skill-root}/scripts/check_report.py --report <report path> --project-root {project-root}` and send its gaps back to the subagent once; the check of the report is never skipped. Gaps that remain go into `open_questions`.

The human's choice per finding, code or model, is not made here: every finding stays open for the gate that reads this output.

End with JSON only, leaving out keys for what was not produced:

```json
{
  "status": "complete | partial | blocked",
  "mode": "epic <n> | range <base>..<head> | codebase",
  "report": "<report path>",
  "tally": {"total": 0, "by_check": {}, "by_severity": {}, "boundary": 0},
  "high": ["FM-<n>: <finding in one sentence>"],
  "boundary": ["FM-<n>: <finding in one sentence>"],
  "independent": true,
  "assumptions": [],
  "open_questions": [],
  "reason": "<one line, only when blocked>"
}
```

`complete` means the report passed its check; `partial` means it was written but gaps remain; `blocked` means no report.
