# Preparing the Event Storming

The outcome is `{domain_model_folder}/workshop-brief.md`, approved by the user, and `{domain_model_folder}/interview-log.md` as its derivation. `{domain_model_folder}` and the artifact language come from the skill's activation. The workshop is only as good as the brief: with the wrong perspectives in the team, or a scope without start and end event, the wall fills with sticky notes from which no sound Bounded Contexts follow.

## Input

An existing `interview-log.md` is the state of an interrupted preparation: rebuild profile and clarification list from it and continue with the first open point.

Otherwise the idea: a path or pasted text from the request. Without one, look for a product brief, PRFAQ, PRD draft or idea description (`**/*brief*.md`, `**/*prfaq*.md`, `**/*prd*.md`, `**/*idea*.md`, `**/*vision*.md`) and have the user confirm the hit; with nothing found, ask for a path or text and wait. List accompanying material found (competitive analysis, existing glossary, earlier DDD files in the model folder) and read what the user confirms as relevant.

## Domain profile

Read the idea completely and fill this profile, each field `evidenced` (with location, e.g. "section 2"), `unclear` or `missing`:

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

From the gaps, build a clarification list, each entry with the part of the brief it affects and a priority: A, no meaningful workshop without it (scope, team); B, improves it considerably (external systems, terms, constraints); C, only if time remains.

Before the interview, show at most 15 lines: what you understood in five bullets, the count of open points per priority, and the topic you start with.

## Interview

One question per message, clarifying one point, A before B, with half a sentence on what depends on it. Refer to the idea ("Section 3 says X, section 5 says Y. Which applies?") and offer 2 to 4 options with the best-evidenced first, through `AskUserQuestion` when available. What the idea states clearly is not asked; it appears in the brief, where the user can correct it. After each answer, update the list, since one answer can settle or raise others. An evasive answer gets one follow-up with a concrete decision aid; still open, it becomes a preliminary Hotspot. Question what seems self-evident when it shapes the model: who is customer, who user, who pays; what happens when an external service fails; which term means something else to another role.

Keep `interview-log.md` current after every answer: the profile with field status at the top, then per question the question, answer, decision and effect on the brief. It is how a later reader, and a later session, sees where each statement came from.

Stop when every A point is clarified and every B point is clarified or a Hotspot, or when the user says to write now. After about 15 questions, ask whether to write with the current state. An open A point goes into the brief as a Hotspot marked "blocks round N".

## The brief

Show the brief before writing it, in at most 25 lines, and write it on approval; show only changed lines after a correction. It holds, each statement traceable to the idea or the log:

- `Project` and mission in one sentence; source paths of the idea and the log.
- `Scope`: from "<start event, past tense>" to "<end event, past tense>", out of scope, constraints, DDD-lite yes or no with reason.
- `Clarified in preparation`: decisions the team must know, one line each; conjectures such as a Core Domain guess marked "Hypothesis, to be checked by the team".
- `Team`: 3 to 5 Domain Experts as `DE-<role>`, each the actor it speaks for, its goals, activities and own terms. Merge two roles with the same view; propose a missing perspective such as operator, support, legal or finance.
- `External systems`, with bought-in ones marked.
- `Preliminary Hotspots`: `🔥 [H01]` onward, question, status open, source question in the log. IDs H01 to the last one are reserved on the board.
- `Language conflict candidates`: term, meaning for role A versus role B.
- `Rounds`: maximum number, at least 6 and 6 by default, since rounds 5 and 6 produce the Context Map and the glossary.

Done when `workshop-brief.md` and `interview-log.md` are written, the brief has no statement without a source, and every open point is a Hotspot. Then offer to start facilitation, in this session or a fresh one.
