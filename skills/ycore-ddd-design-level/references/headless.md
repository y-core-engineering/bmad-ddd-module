# Headless

No interactive user: ask nothing and invent nothing. A Design-Level needs the user for the catalog's open questions and at each context's checkpoint; headless does everything up to them and stops there. `{domain_model_folder}`, `{skill-root}` and the memlog command come from the skill's activation; the route comes from `check_design.py --status`.

Drive the run from the first message: `intent` (create, update, validate), the target context if one is named, and for update the part to revise. Infer what is absent from the model folder.

- Catalog missing: draft it as the Fast path of the catalog reference does, every inference tagged `[ASSUMPTION]` and entered as a Hotspot of its context, and write it as `design-level-catalog.draft.md`, never as the catalog itself: an unapproved catalog does not start a run. Return the open points.
- A full context: run its rounds, the draft design and the reviewer gate as the Fast path of the facilitation reference describes, and stop where its final acceptance begins, with the first line of its board at `BC: <ID> <name> | Status: checkpoint | waiting for the user`.
- A lean context: draft its design as the lean section of the format reference describes and stop before its board is written: the lean design counts as done only on the user's confirmation.
- Validate: run the reviewer gate in its report mode; it needs no user.

The final acceptance needs the user, so a headless create or update ends `partial`, never `complete`.

End with JSON only, leaving out keys for what was not produced:

```json
{
  "status": "complete | partial | blocked",
  "intent": "create | update | validate",
  "domain_model_folder": "<path>",
  "catalog": "<path>/design-level-catalog.md or .draft.md",
  "context": "<folder>",
  "design": "<path>/<folder>/design.md",
  "report": "<path>/reviews/design-level-validation-<date>.md",
  "memlog": "<path of the memlog written>",
  "assumptions": [],
  "open_questions": [],
  "reason": "<one line, only when blocked>"
}
```

`open_questions` holds every Hotspot and catalog point that waits for the user. `blocked` means nothing was produced, for example no Big Picture to work from.
