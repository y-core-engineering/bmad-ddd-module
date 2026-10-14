# The Bounded Context catalog

The outcome is `{domain_model_folder}/design-level-catalog.md`, approved by the user, with the memlog `{domain_model_folder}/design-level.memlog.md` as its derivation. `{domain_model_folder}`, the artifact language, the memlog command and `{skill-root}` come from the skill's activation. The catalog decides which contexts get a full team run, in which order, and what each run must know beforehand, so a run only has to pick its target.

## Input

A `design-level-catalog.draft.md` from a headless run is a proposal: show it, settle every `[ASSUMPTION]` with the user or keep it as a Hotspot, and on approval write it as `design-level-catalog.md` and delete the draft.

A memlog with entries is the state of an interrupted catalog: rebuild catalog and clarification list from it and continue with the first open point.

A catalog that exists but has problems, or differs from `context-map.md` (the `--status` output names both), is revised rather than rebuilt: show each difference, settle it with the user, keep the IDs and folders of unchanged contexts, and log every change.

Otherwise read the Big Picture: `context-map.md`, `event-storming.md`, `ubiquitous-language.md`, `board.md` with its Hotspot outcomes, `workshop-brief.md` and `big-picture.memlog.md` for the team, constraints and regulation, and the idea or product brief they name. Aggregate candidates live only on `board.md` and in `rounds/`. When `--status` reports `big_picture_done` false, the Big Picture is unfinished: recommend finishing it with `ycore-ddd-big-picture` and continue only on the user's word, logged. Look also for decision records (`**/adr/**`, an architecture document) and earlier Design-Level results. A model from elsewhere (a Miro export, a CSV, another team's board) is fine as input; then name the files you used.

Design-Level needs settled context boundaries. Judge the input first:

- Contexts named, Events assigned, subdomains classified: continue.
- Contexts named, classification or assignment incomplete: the gaps go into the interview.
- A timeline with Events but no contexts: recommend finishing the Big Picture with `ycore-ddd-big-picture`; only on the user's word derive context hypotheses from language shifts and Pivotal Events and confirm them one by one.
- Only unordered Events: stop and recommend the Big Picture.

## The catalog

One row per context, each field `evidenced` (with location), `unclear` or `missing`:

| Field | What a run needs it for |
|---|---|
| ID, name, folder `<bc-id>-<kebab-name>` | Target and folder of the run |
| Subdomain type | Depth |
| MVP-relevant | Order, depth |
| Events of the context (IDs) | Starting material of round 1 |
| Aggregate candidates from the Big Picture | Input to round 2, marked as candidates |
| Open and deferred Hotspots (IDs) | Hotspots the run starts with |
| External Systems and ACLs | Round 5, Constraint-Keeper |
| Edges in the Context Map | Boundaries of the run |
| Domain terms and collisions | Language of the team |
| Technical and legal constraints, each with source | Briefing of the Constraint-Keeper |
| Actor perspectives | Number of Domain Experts |
| Most sensitive data and protection need | Red Team, `🔒` invariants |

The folder is the ID and the name in lower-case ASCII: umlauts and ß transliterated (ä → ae, ß → ss), other characters dropped, words joined by hyphens, for example `bc02-bestellpruefung`.

Propose a depth per context: `full` for Core and MVP-relevant contexts, a team run; `lean` for Generic, simple Supporting or postponed contexts, a short design note without a team. Propose an order of the full runs by risk: open Hotspots, compliance constraints, external dependencies, upstream position in the Context Map. Both are proposals for the interview, not decisions.

Look before you ask. The brief's `Stakes` (hobby, internal or launch) set the depth here too; ask for them only when the Big Picture has none. What the Big Picture, the memlogs, existing code or the environment already answer is not a question: log it as `evidenced` with its source. For a hobby, propose `lean` for every context unless the user wants a team run.

From the gaps that remain, build a clarification list, each entry with what depends on it and a priority: A, no meaningful run without it (context boundaries, depth and order, blocking Hotspots); B, clearly better runs (constraints, roles); C, only if time remains. Before the interview, show at most 15 lines: the judgement of the input, contexts with proposed depth, proposed order, open points per priority. Then offer the working mode. The Coaching path, the default: the interview below, a pause after every round, and each context's checkpoint before its design. The Fast path: you batch the remaining A and B points into one or two consolidated questions and draft the catalog with `[ASSUMPTION]` tags; after the catalog's approval each context runs without a halt up to its own final acceptance, and the next context starts without asking. Each `[ASSUMPTION]` also becomes a Hotspot of its context, so that context's final acceptance puts it to the user; the Fast path skips pauses, never a decision. Log the choice.

## Interview

Elicit, don't quiz. One question per message, one point each, A before B, with half a sentence on what depends on it. Ask open, and keep options for a genuine fork, such as two sources that contradict each other ("The board assigns 'Order placed' (E12) to Ordering, the Context Map lists it under Billing. Which applies?"); then offer 2 to 4 options with the best-evidenced first, through `AskUserQuestion` when available. Where you can infer, say so and let the user confirm several inferences in one question. After each answer, update catalog and list. An evasive answer gets one follow-up with a decision aid; still open, it becomes a Hotspot of that context.

By the end, clarified or marked open: depth and order; constraints per full context, each with a source, since what only the user knows is asked and what is evidenced nowhere stays out; Hotspots that must be decided before a run versus those the team may carry; one Domain Expert per context or several where it has several Actor perspectives with their own language; the maximum number of rounds per run, at least 7 and 7 by default, since round 7 is the synthesis.

Log every answer with its decision and effect, and every catalog field as it becomes evidenced, unclear or missing. Stop when every A point is clarified and every B point is clarified or a Hotspot, or when the user says to write now; after about 15 questions, ask whether to write.

## Writing it

Show the catalog in at most 25 lines and write it on approval; show only changed lines after a correction. `design-level-catalog.md` holds:

- `## Contexts`: table `| BC | Context | Folder | Subdomain | MVP | Depth | Order | Events | Aggregate candidates | Hotspots | External systems |`, Depth `full` or `lean`, Order a number for full contexts and `-` for lean ones.
- `## Constraints`: per full context, each constraint with its source.
- `## Team`: the Domain Experts per full context.
- `## Blocking Hotspots`: ID, question, which context and round it blocks, source.
- `## Working mode`: `coaching` or `fast`.
- `## Rounds`: the maximum per run.

Done when the catalog is written and its approval logged, `uv run {skill-root}/scripts/check_design.py --folder {domain_model_folder} --status` reports no `catalog_problems` and no `catalog_stale`, every constraint has a source, every Aggregate candidate is marked as candidate, and every open point is a Hotspot at its context. Then offer the first run, or the lean notes, in this session or a fresh one.
