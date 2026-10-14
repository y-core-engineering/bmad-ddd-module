# Headless

No interactive user: ask nothing and invent nothing. An Event Storming needs the user at two points, the brief's open questions and the checkpoint; headless does everything up to them and stops there. `{domain_model_folder}`, `{skill-root}` and the memlog command come from the skill's activation.

Drive the run from the first message: `intent` (create, update, validate), the idea or product brief, and for update the part to revise. Infer what is absent from the inputs and the model folder.

- Create: build the profile and write the brief as the Fast path of the preparation reference does, every inference tagged `[ASSUMPTION]` and entered as a preliminary Hotspot, every gap that blocks a round as a Hotspot marked "blocks round N". Log each assumption. Then run the rounds, the draft artifacts and the reviewer gate as the Fast path of the facilitation reference describes, and stop where the final acceptance begins: set `Status: checkpoint | waiting for the user`, and return the open Hotspots.
- Update: run the revision round the same way and stop at the checkpoint.
- Validate: run the reviewer gate loaded with this file in its report mode; it needs no user.

The final acceptance needs the user, so a headless create or update ends `partial`, never `complete`.

End with JSON only, leaving out keys for what was not produced:

```json
{
  "status": "complete | partial | blocked",
  "intent": "create | update | validate",
  "domain_model_folder": "<path>",
  "board": "<path>/board.md",
  "brief": "<path>/workshop-brief.md",
  "report": "<path>/reviews/big-picture-validation-<date>.md",
  "memlog": "<path>/big-picture.memlog.md",
  "assumptions": [],
  "open_questions": [],
  "reason": "<one line, only when blocked>"
}
```

`open_questions` holds every Hotspot that waits for the user. `blocked` means nothing was produced, for example no idea to work from.
