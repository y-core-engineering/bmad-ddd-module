# Facilitating the Event Storming

Contents: team · sticky notation · files and writing model · rounds · checkpoint · final artifacts · done.

You are the facilitator of the workshop that `{domain_model_folder}/workshop-brief.md` describes, and you orchestrate a team of subagents through it. `{domain_model_folder}` and the artifact language come from the skill's activation. You merge contributions onto one board, synthesise, resolve conflicts and decide when to iterate; you invent no domain content. The run resumes from the files: the first line of `board.md` is `Status: round <N> | …` after round N is finished, `Status: checkpoint | …` during the checkpoint and the writing of the artifacts, `Status: revision <N> | <part>` while a revision round runs, and `Status: review | …` once the artifacts are written and checked; the reviewer gate sets `done`. A `rounds/round-<NN>/` folder beyond the last finished round is a round under way, also round 1 before `board.md` exists: assign only its missing or empty files, then merge.

## Team

Spawn each role with its perspective only. The narrowing of view is intended: context boundaries emerge from it.

- `DE-<role>`, one per Domain Expert in the brief: that actor's goals, activities and terms.
- `DDD-Modeler`: derives Bounded Contexts, subdomain types, Aggregate candidates and the Ubiquitous Language, in the manner of Evans and Vernon.
- `Challenger`: adversarial; finds missing Events, edge cases, Hotspots, terms used two ways and unevidenced assumptions.

## Sticky notation

Every sticky on the board carries emoji, stable ID and short label. Events are in the past tense. IDs never change across rounds.

| Sticky | Emoji + ID |
|---|---|
| Domain Event | `🟧 [E##]` |
| Command | `🟦 [C##]` |
| Actor | `🟨 [A##]` |
| Policy, "whenever …, then …" | `🟪 [P##]` |
| External System | `🩷 [X##]` |
| Read Model, information an Actor needs to decide | `🟩 [R##]` |
| Hotspot | `🔥 [H##]` |
| Bounded Context, from round 5 | `⬛ [BC##]` |

## Files and the writing model

- `rounds/round-<NN>/<role>.md`: one participant's stickies for one round. A new folder per round, a new file per participant; earlier files are never changed, corrections come in the next round. Every sticky stays traceable to author and round.
- `board.md`: the wall. First line the status line described at the top of this file; then a timeline table `| # | 🟨 Actor | 🟦 Command | 🟧 Event | 🟪 Policy | 🩷 External | 🟩 Read Model |`; the Hotspot list with status; from round 5, Events grouped under Bounded Context headings.
- `iterations-log.md`: per round the participant files processed (links), what was added, term conflicts, your decisions and open Hotspots, so a reader sees why the wall looks as it does. Each decision also goes into the memlog as it is made; a blocked round is recorded in both, so a resumed session can tell it from one still running.

One file, one writer: each participant writes only its own round file, you alone write board and log, so parallel agents lose nothing. Merge from the round files, never from chat replies: place stickies on the timeline, deduplicate, merge synonyms. Different terms for one thing, or one term for different things, signal a context boundary: such a term is a Hotspot until a boundary separates the meanings or the user decides, never smoothed over.

A participant's file:

```markdown
# Round <NN> · <role>
Input: board.md as of round <NN-1> (round 1: brief and idea only)

## Stickies
🟧 <Event> | Actor: <Actor> | Note: <…>
🔥 <open question> | Reference: <Event or ID>

## On the wall (from round 2)
<additions, contradictions, term conflicts, citing board IDs>
```

One line per sticky, without IDs; you assign them when merging.

Every assignment names the brief, the idea, from round 2 the board, the exact result path, and ends with this contract verbatim:

```text
1. Result file: <exact path>. Change no other file.
2. Write the file completely first, then answer. No tool call after the answer.
3. Your last message is exactly these lines:
   STATUS: done | partial | blocked
   FILE: <path>
   SIZE: <number of stickies>
   GIST: <one sentence>
   OPEN: <questions for the facilitator, or none>
```

The file counts, not the reply: check each expected path exists and is not empty. Missing or empty, assign once more with the same assignment; missing again, the round is blocked and you report it. Settle `blocked` and `OPEN` before merging that file.

Without a subagent tool, write each perspective's file yourself, one role at a time, before reading any other role's file for the round, and note in the log that the perspectives were not independent.

## Rounds

After each round: all called participants' files present, merged, board and log written, convergence checked; only then the next round.

1. Chaotic exploration, divergent and parallel: every `DE-*` independently delivers its Events, unordered, better too many than too few. Start all in one message; none sees another's file. No discussion.
2. Timeline, convergent: order every Event between the scope's start and end event, deduplicate, merge synonyms. The Challenger marks gaps and term conflicts.
3. Hotspots and Pivotal Events: the Challenger sets Hotspots and checks the preliminary ones from the brief; the DDD-Modeler marks Pivotal Events.
4. Commands, Actors, Policies, External Systems: per Event the Command and Actor, the Policies, External Systems with ACL candidates marked, and the Read Models a decision needs.
5. Strategic structure: the DDD-Modeler groups Events into Bounded Contexts (a boundary is a change of language or responsibility), classifies subdomains Core, Supporting or Generic, and drafts the Context Map; the Challenger checks every boundary for its reason. In the same round each context gets the most sensitive data type it holds with its protection need from the idea, and each Context Map edge the note whether it crosses a trust boundary (other operator, other permission domain, open network, other tenant). That later decides where an Anti-Corruption Layer is also a security boundary. A protection need the idea does not state is a Hotspot, not an estimate.
6. Ubiquitous Language: a glossary per context, conflicts noted.

From round 2 on, work mostly sequentially: the board is the input, Challenger and Modeler deliver deltas, you integrate at once so everyone builds on the same state. First all stickies on the wall, then discussion, and only where a conflict or Hotspot needs it.

Converged when no new Events come, no term conflict is unresolved and every context boundary has its reason. Not converged after round 6: further rounds are deltas on the open conflicts and Hotspots, up to the brief's maximum.

A revision round works the same way on the part the user named, in the next `rounds/round-<NN>/` folder; after its merge the status becomes `checkpoint` for the Hotspots it raised, and the affected artifacts are updated.

## Checkpoint before the synthesis

After the last round's merge, set the status to `checkpoint`; a resumed checkpoint continues with the Hotspots that have no outcome recorded, and once every Hotspot has one, with the final artifacts, completing and checking files that already exist rather than writing them anew. The run ends only when no domain question is open. Present every Hotspot on the board to the user one at a time, ordered by effect on scope, context boundaries and language, with question, location and the options noted on the board. Decide nothing and recommend nothing where you lack the domain basis. Each Hotspot ends in one of three states, recorded on the board with decision and date:

- decided: the answer is worked into timeline, context cut and glossary;
- moot: one sentence why it no longer touches the Big Picture;
- deferred: only on the user's explicit word, with the assumption work continues under, an owner, and the step where it returns (Design-Level of a named context, or architecture). Missing any of the three, it counts as open.

Log each outcome in the memlog as it is given. What is not settled here returns in the Design-Level or the architecture and costs many times as much there.

## Final artifacts

Write into `{domain_model_folder}`. `ycore-ddd-model-check` reads the Contexts and Edges tables and the glossary sections, a Design-Level reads all three files, so headings, column names, IDs and the fixed cell values stay exactly as given here in English: Subdomain `Core`, `Supporting`, `Generic`, `External`; the pattern names; Trust boundary `no` or `yes: <which>`. Only prose and free-text cells follow the artifact language. Context IDs and names are identical across the three files. Diagrams are Mermaid code blocks; the tables are the record, the diagram is a view of them.

`context-map.md`:

- `## Contexts`, table `| ID | Context | Subdomain | Responsibility | Most sensitive data | Protection need |`, one row per `BC##`, Subdomain `Core`, `Supporting` or `Generic` (Generic marked as buy candidate in Responsibility). External systems get rows too, ID `X##`, Subdomain `External`.
- `## Edges`, table `| ID | From | To | Pattern | What flows | Trust boundary |`, IDs `K-01` onward, From (upstream) and To (downstream) holding `BC##` or `X##` IDs, Pattern one of Partnership, Shared Kernel, Customer/Supplier, Conformist, Anti-Corruption Layer, Open Host Service, Published Language, Separate Ways (an edge may name two, such as `Open Host Service / Anti-Corruption Layer`), Trust boundary `no` or `yes: <which>`.
- `## Diagram`: Mermaid `graph LR`, nodes labelled with context name and subdomain type, edges labelled with what flows, ACL edges as `-.ACL.->`.

`ubiquitous-language.md`: one section per context, `## BC## <Context>`, table `| Term | Definition | Conflicts |`, Conflicts naming the other context and its meaning. The same term meaning different things in two contexts is intended and stands in both.

`event-storming.md`: the event flow as Mermaid `flowchart LR` (Command → Event chains, Policies as nodes); the subdomain classification with one reason per context; per context a `## BC## <Context>` section with responsibility and the Events it owns (board IDs); the deferred Hotspots with assumption, owner and target step; and which Core contexts to deepen next in a Design-Level, or the DDD-lite note with its reason.

`board.md`, `iterations-log.md` and `rounds/` stay as the derivation.

## Done

Run `uv run {skill-root}/scripts/check_artifacts.py --folder {domain_model_folder}`, `{skill-root}` being the folder above this file's `references/`, and fix what it lists; then set the status to `review` for the reviewer gate. Ready for review means: the timeline covers the scope with the happy path and the essential edge cases; every context boundary has a reason; every context has its most sensitive data type and protection need and every edge its trust-boundary note; subdomains are classified with Generic marked as a buy candidate; every Hotspot has passed the checkpoint; every round has its folder with one file per participant called; and the script reports no gaps.
