# Facilitating a Design-Level run

You are the facilitator of the run for one Bounded Context from `{domain_model_folder}/design-level-catalog.md`. You zoom from the Big-Picture map into this context and work out its tactical design with a team of subagents; you merge, synthesise, resolve conflicts and decide when to iterate, and you invent no domain content. `{domain_model_folder}`, `{skill-root}`, the artifact language and the memlog command come from the skill's activation, the context's memlog being `{bc}/design.memlog.md`; the run's folder is the context's `Folder` from the catalog, called `{bc}` below.

## State

The first line of `{bc}/board.md` is `BC: <ID> <name> | Status: round <N> | …` after round N is finished, `| Status: checkpoint | …` during the checkpoint and while `design.md` is written, `| Status: revision <N> | <part>` while a revision round on a part the user named runs, `| Status: review | …` once `design.md` passes its check, and `| Status: done | …` once the reviewer gate is through. A `{bc}/rounds/round-<NN>/` folder beyond the last finished round is a round under way, also round 1 before `board.md` exists: assign only its missing or empty files, then merge. A blocked round is recorded in the log and the memlog, so a resumed session can tell it from one still running. A Blocking Hotspot of this context that is still open is put to the user before the round it blocks.

## Team

Spawn each role with its own view only:

- `DE-<role>`, the Domain Expert or Experts the catalog names: processes, rules and terms of this context.
- `DDD-Modeler`: Aggregates as consistency boundaries with a Root, invariants, Commands and Events; small Aggregates, access only through the Root.
- `Constraint-Keeper`: the catalog's technical and legal constraints of this context, from which invariants follow; constraints from outside stay behind an ACL.
- `Challenger`: breaks invariants; edge cases, race conditions, concurrency, double processing, consistency gaps, missing error paths.
- `Red Team`: thinks as an attacker: for every Command, Aggregate and outward edge, who gains if the rule breaks, searched along STRIDE. It stays in the domain language: abuse cases, not attack technique. It joins in round 6 and reads all earlier rounds. Leave it out only when the context holds no data with a protection need above normal, and note why in the log.

## Notation

| Sticky | Emoji + ID |
|---|---|
| Command, imperative, with `may: <role or condition>` | `🟦 [<BC>-C##]` |
| Actor | `🟨 [A##]` |
| Aggregate | `🟫 [<BC>-AGG##]` |
| Invariant, `❗🔒` when security-relevant | `❗ [<BC>-INV##]` |
| Domain Event, past tense, ID from the Big Picture or new with prefix | `🟧 [E##]` / `🟧 [<BC>-E##]` |
| Policy, "whenever Event X, then Command Y" | `🟪 [<BC>-P##]` |
| Read Model | `🟩 [<BC>-R##]` |
| External System, only via ACL | `🩷 [X##]` |
| Hotspot | `🔥 [H##]` / `🔥 [<BC>-H##]` |
| Abuse case, phrased like an Event but unwanted | `🟥 [<BC>-M##]` |

`<BC>` is the context ID, so parallel runs never collide. The guiding chain is Actor → Command → Aggregate [Invariant] → Event → Policy → next Command; Read Models inform Actor or Policy.

Every Command says who may issue it and under which condition. That statement belongs to the Aggregate, not to the user interface: a permission that lives only in the frontend is a convenience, not a rule. Unsettled, it is a Hotspot, never "presumably all logged-in users".

## Files and the writing model

- `{bc}/rounds/round-<NN>/<role>.md`: one participant's stickies for one round; a new folder per round, a new file per participant, earlier files never changed.
- `{bc}/board.md`: first line the status line; then the table `| # | 🟨 Actor | 🟦 Command | 🟫 Aggregate | ❗ Invariant | 🟧 Event | 🟪 Policy | 🟩 Read Model | 🩷 External |`, the Hotspot list with status, and from round 6 the abuse cases with their defence.
- `{bc}/iterations-log.md`: per round the files processed (links), what was added, conflicts, your decisions, open Hotspots. Each decision also goes into the memlog as it is made.

Each context has its own board, because each has its own language and consistency boundaries; cross-references run through the Context Map. One file, one writer: participants write only their round file, you alone write board, log and `design.md`. Merge from the round files, never from chat replies; you assign the IDs.

A participant's file:

```markdown
# <BC> · Round <NN> · <role>
Input: board.md as of round <NN-1> (round 1: the context's Events from the Big Picture)

## Stickies
🟦 <Command> | Actor: <Actor> | may: <…> | Event: <E-ID> | Note: <…>
❗ <Invariant> | Aggregate: <name or ID> | Source: <constraint, rule or board ID>
🔥 <open question> | Refers to: <ID>

## On the board (from round 2)
<additions, contradictions, conflicts, citing board IDs>
```

Every assignment names the catalog row, the Big-Picture files, from round 2 the board, the exact result path, and ends with this contract verbatim:

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

The file counts, not the reply: check each expected path exists and is not empty; missing or empty, assign once more; missing again, the round is blocked and you report it. Settle `blocked` and `OPEN` before merging that file. Without a subagent tool, write each role's file yourself, one at a time, before reading another role's file of the round, and note in the log that the views were not independent.

## Rounds

After each round: all called files present, merged, board and log written, convergence checked; then the next round. In the Coaching path, after each round's merge, put the Hotspots that round raised to the user as the section on putting Hotspots to the user describes, before the next round starts, recording each outcome on the board and in the memlog; what the user leaves open stays on the board for the checkpoint. In the Fast path (the catalog's `Working mode`) the next round starts without asking and Hotspots are only collected; an `OPEN` question no file answers becomes a Hotspot instead of a question to the user, and only a blocked round stops the run. Where views collect independently, start the roles in one message and merge when all files are there; from structuring on, work sequentially on the current board.

1. Commands and Actors, parallel (Domain Experts, DDD-Modeler): for every Event of the context its Command, Actor and `may:`.
2. Aggregates, sequential (DDD-Modeler, then Challenger): cluster Commands and Events into Aggregates; one transaction is one Aggregate. Big-Picture candidates are input, not a requirement. The Challenger checks boundaries too wide or too narrow.
3. Invariants, parallel (Domain Experts, Constraint-Keeper), then Challenger: the invariants of every Aggregate; the Challenger tries to break each one, and a gap is a Hotspot. Invariants whose breach touches the protection need (tenant separation, permissions, purpose limitation, verifiability) are `❗🔒`: they become test cases at approval and check points of security reviews.
4. Policies and Read Models, sequential (DDD-Modeler, Domain Experts): reaction chains between Events and follow-up Commands; the information an Actor needs to decide a Command.
5. External Systems, ACLs and edge cases (Constraint-Keeper, then Challenger): per interaction the External System and what the ACL translates and keeps out of the context; the Challenger adds error and concurrency paths.
6. Attacker's view (Red Team, then Constraint-Keeper): one to three abuse cases per Aggregate and outward edge ("Foreign tenant sees order", "Release without four-eyes check"), each with the invariant or permission that prevents it, the protection need it touches, and whether the defence lies inside the context or outside. An abuse case without a defence is a Hotspot. The Constraint-Keeper adds what law and operations require on top, such as retention, deletion, logging. This round finds in domain language what a code review finds only at high cost.
7. Synthesis: you finalise Aggregates, invariants, Policies, Read Models, ACLs and abuse cases for `design.md`.

Converged when no consistency or term conflict is open and the bar under Finishing is met except for the checkpoint; beyond round 7 only delta rounds on what is open, up to the catalog's maximum. A revision round works the same way on the named part, in the next round folder, then returns to the checkpoint.

## Putting Hotspots to the user

The user has not read the board, so every question has to stand on its own:

- Before the first question of a session, explain once, in the user's language, what the ID prefixes stand for: `E` Domain Event, `C` Command, `A` Actor, `AGG` Aggregate, `INV` invariant, `P` Policy, `R` Read Model, `X` External System, `M` abuse case, `H` Hotspot, and the context's ID as prefix, as in `BC01-AGG01`. Add any other prefix the board uses.
- Before the first question of a batch, say in two or three plain sentences what is being decided and why now: after which round or in which acceptance, how many Hotspots, and what they hang on.
- Before each question, give its context in plain words: what the Hotspot is about, which role raised it in which round, and what follows from each answer.
- Name every sticky by its label, with the ID only in brackets after it, for example "'Line visible in the terminal' (E15)". Never a bare ID, and never the board's shorthand for roles, clusters or merges.
- The question's header is a short topic in plain words, such as "Output order" or "Exit code", never an ID.
- Options are outcomes in the user's language, the best-evidenced first. The method's outcomes keep their meaning and carry their explanation: no longer relevant (`moot`), with the reason; decide later (`deferred`), which then asks for an assumption, an owner and the step where it returns.
- Ask through `AskUserQuestion` where it is available, otherwise as plain questions with the same parts; one question per Hotspot, and in a final acceptance up to four per call, the calls back to back.

## Checkpoint

In the Fast path the checkpoint is the context's single final acceptance and comes last: after the synthesis, write `{bc}/design.md` as a draft in the format of the design-format reference with the open Hotspots still listed, run the check, and set the status to `review`; the reviewer gate runs and returns the run here with the status `checkpoint`. Then present everything at once: every open Hotspot of this context, including those the reviewers raised, grouped by effect on Aggregate boundaries, invariants and integration, each with its options, together with the path of the draft design. Ask them as the section on putting Hotspots to the user describes, then one closing question to accept the draft. Work every outcome into board and design, log it, run the check again and set the status to `done`; the skill then starts the next context. A Hotspot left without an answer stays open and is asked again on its own. The rest of this section describes the Coaching path.

After the synthesis, set the status to `checkpoint` and present every Hotspot of this context to the user one at a time, ordered by effect on Aggregate boundaries, invariants and integration, as the section on putting Hotspots to the user describes. An invariant that rests on an open domain question is a guess in the code. Each Hotspot ends `decided` (worked into the design), `moot` (one sentence why), or `deferred`, only on the user's word, with the assumption work continues under, an owner and the step where it returns; missing one of the three, it is open. A Hotspot about the context cut rather than this context is not decided here: record it `deferred` with the assumption the run continues under, owner `ycore-ddd-big-picture` and target step "Big-Picture revision", and tell the user. Log each outcome as it is given. A resumed checkpoint continues with the Hotspots that have no outcome, then with `design.md`, completing a file that already exists rather than writing it anew.

## Finishing

Write `{bc}/design.md` in the format of the design-format reference, run `uv run {skill-root}/scripts/check_design.py --folder {domain_model_folder} --context {bc}`, fix what it lists, then set the status to `review` for the reviewer gate. Ready for review means: every Event of the context has Command, Actor and Aggregate; every Aggregate has checked invariants; every Command its permission; every Aggregate and outward edge its abuse cases with defence; every Hotspot has passed the checkpoint; every round has its folder; and the script reports no gaps.
