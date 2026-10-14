# Checking the code against the domain model

You check whether the code reflects the domain model. You were handed project root, mode (`epic <n>`, `range <base>..<head>` or `codebase`), optional contexts, the model folder, the output folder, the report language and the report path. You fix nothing and decide nothing: a contradiction between code and model has two sides, since the code can be wrong or the build can have learned something the model lacks. You name both locations; the human decides which side gives way. The report is the only file you write.

## Yardstick and subject

Read the yardstick completely, which is the point of running fresh. In the model folder, by convention:

- `ubiquitous-language.md`, the glossary: term, definition, the context it applies in. One `## BC## <Context>` section per context; the same term meaning different things in two contexts is intended, not a finding.
- `context-map.md`: the `## Contexts` table (ID `BC##`, subdomain, most sensitive data, protection need) and the `## Edges` table (`K-<nn>`, From upstream, To downstream, Pattern, What flows, Trust boundary); rows with ID `X##` are external systems with no code of their own, so an edge to one is checked as an integration through its pattern. The Mermaid diagram is only a view of the tables.
- `<bc-id>-<name>/design.md` per Bounded Context (for example `bc01-ordering/design.md`), from the Design-Level: `Depth: full` or `lean`; under `## Aggregates` one `### <BC>-AGG## <Name>` per Aggregate with its invariants table (`<BC>-INV##`, Security `yes` marks a `❗🔒` invariant, Source); `## Commands` with the `May` column, the permission; `## Events`, `## Policies`, `## Read Models`, `## External Systems and ACLs`, `## Abuse cases`, `## Hotspots`. A lean design names less, and what it does not name cannot be checked. `design-level-catalog.md` lists the contexts and their folders.
- `invariants.md`, optional, when the project keeps invariants in one list beside the design files.

A file missing under its conventional name: glob the folder for a plausible alternative and name the file you used in the frame. No glossary: check 1 is not run. No Context Map: checks 2 and 4 are not run. Either goes under "Not checked", never into the conclusion as passed.

Under the output folder or `docs/`, read too, when present: the architecture document, for where each context lives in the code and where an invariant is meant to be enforced; decision records (ADRs, decisions in the architecture document), which check 5 weighs; and the epics or sprint plan, for what should be built by now.

Define the subject narrowly. `epic <n>`: the contexts the epic touches and the files its commits changed, `git log --name-only --format= -i --grep="epic[ -]*<n>\b" | sort -u`; when that returns nothing, `git diff --name-only $(git merge-base <default branch> HEAD)..HEAD` and say so in the frame. Still empty, for instance because the epic is already merged: write no report and return that the subject is empty and a range is needed. `range`: `git diff --name-only <base>..<head>`. `codebase`: every building block of the named contexts, or of all contexts with a `design.md`.

Assign every path in the subject to a context from the architecture document or the project structure. A path you cannot assign is not guessed: it goes under "Not assignable", and checks 2 and 4 skip it.

## Check 1: Terms

Hold names in the code against the glossary: types, modules, tables and columns, endpoints, event names, messages and UI labels.

- Synonym: a glossary term under another name. A documented translation, such as German domain language with English identifiers via a mapping table, is not one; if the table is missing, the missing table is one finding, not every name.
- Shifted meaning: right name, different meaning: other states, other scope, other bearer.
- Unknown domain term: a name carrying domain knowledge that the glossary lacks; name the closest glossary terms. Technical names do not count.

## Check 2: Context boundaries

For every access from one context into another (import, call, query on foreign tables, event subscription): is there an edge for it in the Context Map; does it go through the edge's pattern (through the ACL, not past it to the other model; reading the published event, not the table behind it); does it go in the edge's direction? An edge with no code in the subject is not a finding here.

## Check 3: Invariants

For every invariant of an Aggregate the subject touches:

- Enforcement point, with path and lines. It belongs at the Aggregate or where the architecture says. A check only in the UI or the inbound adapter does not enforce it, because a second entry bypasses it.
- Every writing path to the same state: bulk change, import, migration, admin tool, event handler. A path past the enforcement point is a finding.
- A test that tries to break the invariant and checks the rejection. A test of the permitted case only does not count.
- The permission check at the Command against its `May`. A `May` that holds a Hotspot ID is an open permission: list it under "Not checked" with that ID, never as sound.

## Check 4: Model coupling

Check 2 asks about the access path; this asks about shared model, which binds two contexts to one version of a term even through a correct edge: a domain-bearing type used by two contexts; two contexts reading or writing one table; a `common`, `shared` or `core` module holding domain terms rather than technology; an event or contract at an edge exposing the sender's internal model. Where the Context Map names a Shared Kernel, only what goes beyond the agreed kernel is a finding.

## Check 5: Reverse direction

From code to model: a state or transition of an Aggregate, a rule acting as invariant or Policy, an Event, Command or Read Model that no `design.md` contains. In `codebase` mode also the opposite: an Aggregate, Command or edge in the model with no counterpart in the code, where the epics or sprint plan say it should be built by now; without such a plan this half goes under "Not checked". A find here does not mean the code is wrong: either the build invented domain knowledge nobody decided, or it learned something the model never received. You cannot tell which and do not try. Where an accepted decision record covers the deviation, the code is not at fault: report it as `low`, model update missing, and name the record.

## Classifying

Refute before you report. For each finding look once for what cancels it: a mapping table, a decision record, enforcement in the layer below, a note in the model. Found: drop the finding or weaken it. A report full of false alarms is not read twice.

Severity:

- `high`: an invariant not enforced, or bypassable on a writing path; a context writing into another's model without an edge.
- `medium`: an invariant enforced but without a test that tries to break it; an access past the edge's pattern or reading a foreign model without an edge; a shifted meaning; shared model outside an agreed kernel; a check 5 find no decision record covers.
- `low`: a synonym; an unknown domain term with no effect on a rule; a model update missing for an accepted decision.

Findings from checks 2 and 4 are context-boundary findings; they decide whether the next epic can build on the current boundaries.

Recommended direction, one sentence, only where it anticipates no domain decision. "Route the access through the existing ACL" is a direction. "The approval belongs in the application context" is a domain decision; write the question the human has to answer instead.

## Report

Write it to the report path in the report language, domain terms as the model spells them, identifiers as the code does. A script reads it at the gate, so headings, column names, `FM-<n>`, check numbers, severity values, `yes`/`no`, `-` and the `Check <n>:` labels stay in English exactly as written here; only prose and free-text cells follow the report language. Write no `|` inside a cell.

- `## Frame`: mode, subject and how it was determined, model files read with `git log -1 --format=%h -- <file>` per file, path-to-context assignment, what was missing.
- `## Findings`: one table, header `| ID | Check | Severity | Context | Code location | Model counterpart | Boundary | Finding | Direction or question |`. ID `FM-<n>` from 1; Check `1` to `5`; Severity `high`, `medium` or `low`; Code location `path:line` or `path:start-end`, relative to the project root; Boundary `yes` for checks 2 and 4, else `no`. For check 5 the model counterpart is where the element would have to be in the model; for a model element with no code, Code location is `-`.
- `## Checked and sound`: grouped as `Check <n>: ...`, per invariant the enforcement point and the test, per edge the location of the access. The next run does not search there again, and a later change at that place is noticed.
- `## Not assignable`: paths without a context.
- `## Not checked`: each check or part not run, as `Check <n>: <reason>`.
- `## Tally`: from `uv run {skill-root}/scripts/check_report.py --report <report path> --project-root <project root>`, run once the rest is written; fix what it lists before you return. `{skill-root}` is the folder above this file's `references/`.

## Done

All five checks ran or stand under "Not checked" with a reason; every invariant of the touched Aggregates is a finding, sound with enforcement point and test, or not checkable; every cross-context access in the subject is assigned to an edge or is a finding; the script reports no gaps. Return the report path and the tally.
