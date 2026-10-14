# The design.md format

`{domain_model_folder}/<folder>/design.md`, the folder taken from the catalog (for example `bc01-ordering`), is read by BMad's architecture and build skills and by `ycore-ddd-model-check`, which holds the code against it, and `uv run {skill-root}/scripts/check_design.py --folder {domain_model_folder} --context <folder>` checks its structure and cross-references. So headings, column names, IDs and the fixed cell values stay exactly as given here, in English; only prose and free-text cells follow the artifact language. Write no `|` inside a cell.

The first line is `# <BC-ID> <Context> · Design`, the context name exactly as in the catalog; the second is `Depth: full` or `Depth: lean`, matching the catalog. Then these sections, each a table where one is shown:

- `## Aggregates`: per Aggregate a `### <BC>-AGG## <Name>` with the lines `Root:`, `Entities:` and `Value Objects:` (`none` where there are none), then the table `| ID | Invariant | Security | Source |`. ID `<BC>-INV##`; Security `yes` for a `❗🔒` invariant, else `no`; Source the constraint, rule, catalog line or board ID it comes from.
- `## Commands`: `| ID | Command | Actor | May | Aggregate | Events |`. May is who may issue it and under which condition, or the Hotspot ID that keeps it open; Aggregate an ID from this file; Events the IDs it produces, each listed under Events.
- `## Events`: `| ID | Event | Aggregate |`, Big-Picture IDs kept, new ones `<BC>-E##`; every Event produced by some Command, and for a full context every Event the catalog assigns.
- `## Policies`: `| ID | Whenever | Then |`, an Event ID of this file and a Command ID, of this context or another.
- `## Read Models`: `| ID | Read Model | Serves | Content |`, Serves the Actor or Policy.
- `## External Systems and ACLs`: `| ID | System | ACL translates | Kept out |`, `X##` IDs from the Context Map.
- `## Abuse cases`: `| ID | Abuse case | STRIDE | Prevented by | Protection need |`. STRIDE distinct letters of `S`, `T`, `R`, `I`, `D`, `E`; Prevented by an invariant or Command ID of this file, or the Hotspot ID that keeps it open.
- `## Hotspots`: `| ID | Question | Status | Decision |`. Status `decided`, `moot` or `deferred`; for `deferred`, Decision names assumption, owner and target step. A Hotspot about the context cut is `deferred` with owner `ycore-ddd-big-picture` and target step "Big-Picture revision".
- `## Flow`: a Mermaid `flowchart LR` of the Command → Aggregate → Event → Policy chains.
- `## Implementation order`: the order in which to build the Aggregates, and the remaining deferred Hotspots for the client.

Every row comes from the catalog, the Big-Picture files, the rounds or the user, never from inference alone.

## A lean context

A lean context gets no team run. Its design keeps `Depth: lean`, a `## Why lean` paragraph (responsibility, why no team run, MVP status), and of the sections above at least `## Aggregates`, `## Commands`, `## External Systems and ACLs` and `## Hotspots`; what it leaves out, a later full run adds after promotion.

Draft it from the catalog row, the Big-Picture files and the context's Events. Put each open Hotspot of the context to the user, with the same three outcomes as a full checkpoint (one at a time in the Coaching path, all at once together with the draft in the Fast path), and ask for what the sources leave open rather than filling it. Log every answer and outcome in the context's memlog. Write `design.md`, run the check with `--context <folder>`, and fix what it lists. Show the design to the user; on their confirmation write `<folder>/board.md` with the single line `BC: <ID> <name> | Status: done | lean, confirmed` and log it. A lean context counts as done only with that line. The reviewer gate is scaled to stakes and does not run for a lean context unless the user asks for it.
