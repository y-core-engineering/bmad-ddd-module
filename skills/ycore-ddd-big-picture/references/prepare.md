# Preparing the Event Storming

The outcome is `{domain_model_folder}/workshop-brief.md`, approved by the user, with the memlog `{domain_model_folder}/big-picture.memlog.md` as its derivation. `{domain_model_folder}`, the artifact language and the memlog command come from the skill's activation. The workshop is only as good as the brief: with the wrong perspectives in the team, or a scope without start and end event, the wall fills with sticky notes from which no sound Bounded Contexts follow.

## Input

A memlog with entries is the state of an interrupted preparation: rebuild profile and clarification list from it and continue with the first open point.

Otherwise the idea: a path or pasted text from the request. Without one, look for a product brief, PRFAQ, PRD draft or idea description (`**/*brief*.md`, `**/*prfaq*.md`, `**/*prd*.md`, `**/*idea*.md`, `**/*vision*.md`) and have the user confirm the hit; with nothing found, ask for a path or text and wait. List accompanying material found (competitive analysis, existing glossary, earlier DDD files in the model folder) and read what the user confirms as relevant.

Look before you ask. What the project or the machine already answers is not a question: the README, existing code, manifests and configuration in the project, and facts of the environment the idea depends on, such as the operating system (`uname -a`, `sw_vers`) or the shell (`echo $SHELL`). Log each such finding as `evidenced (environment)` with the command or file it came from, and do not tell the user what they can see themselves.

## Domain profile

Read the idea completely and fill this profile, each field `evidenced` (with location, e.g. "section 2", or the environment source), `unclear` or `missing`:

| Field | What the workshop needs it for |
|---|---|
| Vision and problem, 1 to 3 sentences | Mission, context summary |
| Actors and stakeholders with their goals | Choice of Domain Expert roles |
| Conflicts of interest between actors | Narrowing of view per role, expected language conflicts |
| Scope: start and end event of the flow | Frame for round 1 and the timeline |
| Out of scope | Protection against sprawl |
| Happy path in one paragraph | Plausibility check of the timeline |
| External systems, integrations, bought-in services | External System examples, ACL and Generic candidates |
| Business model and differentiation | Core Domain hypothesis |
| Domain terms, synonyms, ambiguous terms | Language conflict candidates, start of the glossary |
| Regulation, compliance, data protection | A perspective of its own or a Hotspot; mandatory once personal data or a high protection need appears |
| Constraints: deadline, team size, MVP cut | Round budget, DDD-lite or full map |
| Known risks and open questions | Preliminary Hotspots |

Before anything else, ask one short question about the stakes: a hobby or experiment, an internal tool, or a product launch. The answer sets the depth. For a hobby or experiment only scope and team are A points, DDD-lite is the default, the team has two or three Domain Experts, and business model, regulation and constraints are asked only where the idea itself raises them. An internal tool adds external systems and terms. A launch asks every field. Log the answer.

From the gaps that remain, build a clarification list, each entry with the part of the brief it affects and a priority within the stakes: A, no meaningful workshop without it (scope, team); B, improves it considerably (external systems, terms, constraints); C, only if time remains. A gap the stakes do not call for is no entry.

Before the interview, show at most 15 lines: what you understood in five bullets, the count of open points per priority, and the topic you start with. Then offer the working mode. The Coaching path, the default: the interview below, a pause after every round, and the checkpoint before the artifacts. The Fast path: you batch the remaining A and B points into one or two consolidated questions and draft the brief with `[ASSUMPTION]` tags where you inferred; after the brief's approval the rounds, the draft artifacts and the reviewer gate run without a halt, up to one final acceptance. Each `[ASSUMPTION]` is also a preliminary Hotspot, so the final acceptance puts it to the user; the Fast path skips pauses, never a decision. Log the choice.

## Interview

Elicit, don't quiz. One question per message, clarifying one point, A before B, with half a sentence on what depends on it. Ask open ("How do you think about X?") and keep options for a genuine fork, such as two places in the idea that contradict each other ("Section 3 says X, section 5 says Y. Which applies?"); then offer 2 to 4 options with the best-evidenced first, through `AskUserQuestion` when available. Where you can infer, say so and let the user confirm several inferences in one question ("I am assuming X, Y and Z. Right?"). What the idea states clearly is not asked; it appears in the brief, where the user can correct it. After each answer, update the list, since one answer can settle or raise others. An evasive answer gets one follow-up with a concrete decision aid; still open, it becomes a preliminary Hotspot. Question what seems self-evident when it shapes the model: who is customer, who user, who pays; what happens when an external service fails; which term means something else to another role.

Log every answer as it comes, with the decision and its effect on the brief, and every profile field as it becomes evidenced, unclear or missing. The memlog is how a later reader, and a later session, sees where each statement came from.

Stop when every A point is clarified and every B point is clarified or a Hotspot, or when the user says to write now. After about 15 questions, ask whether to write with the current state. An open A point goes into the brief as a Hotspot marked "blocks round N".

## The brief

Show the brief before writing it, in at most 25 lines, and write it on approval; show only changed lines after a correction. It holds, each statement traceable to the idea or the log:

- `Project` and mission in one sentence; source paths of the idea and the memlog.
- `Stakes`: hobby, internal or launch.
- `Scope`: from "<start event, past tense>" to "<end event, past tense>", out of scope, constraints, DDD-lite yes or no with reason.
- `Clarified in preparation`: decisions the team must know, one line each; conjectures such as a Core Domain guess marked "Hypothesis, to be checked by the team".
- `Team`: Domain Experts as `DE-<role>`, two or three for a hobby or DDD-lite, three to five otherwise, each the actor it speaks for, its goals, activities and own terms. Merge two roles with the same view; propose a missing perspective such as operator, support, legal or finance.
- `External systems`, with bought-in ones marked.
- `Preliminary Hotspots`: `🔥 [H01]` onward, question, status open, source entry in the memlog. IDs H01 to the last one are reserved on the board.
- `Language conflict candidates`: term, meaning for role A versus role B.
- `Working mode`: `coaching` or `fast`.
- `Rounds`: maximum number, at least 6 and 6 by default, since rounds 5 and 6 produce the Context Map and the glossary.

Done when `workshop-brief.md` is written and its approval logged, the brief has no statement without a source, and every open point is a Hotspot. Then offer to start facilitation, in this session or a fresh one.
