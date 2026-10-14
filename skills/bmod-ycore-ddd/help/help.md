# ycore-ddd knowledge

This document covers the skills of the `ycore-ddd` module: what each one gives the user, when to recommend it, and what to offer next.

## The skills

- `ycore-ddd-big-picture`: prepares a Big-Picture Event Storming in an interview about the product idea, then facilitates it with a team of agents over up to six rounds, ending in `context-map.md`, `ubiquitous-language.md` and `event-storming.md` in the domain model folder; a run resumes in a new session from its files. Recommend it after a product brief or PRFAQ and before `bmad-prd`, or when the user wants to find Bounded Contexts, a Context Map or a glossary. Afterwards offer `bmad-prd` with the three artifacts as input, and `ycore-ddd-model-check` once code exists.
- `ycore-ddd-design-level`: builds a catalog of the Bounded Contexts from the Big Picture in an interview (full team run or lean note, order by risk, constraints), then runs a Design-Level Event Storming per context with a team of agents: Commands with permissions, Aggregates with invariants, Policies, Read Models, ACLs and abuse cases, ending in `<bc-id>-<name>/design.md` in the domain model folder. Recommend it after `ycore-ddd-big-picture`, or when the user wants to design the Aggregates or find the invariants of a context. Afterwards offer the next context in the catalog, `bmad-architecture` with the design files, and `ycore-ddd-model-check` once code exists.
- `ycore-ddd-model-check`: checks the code against the domain model (glossary, Context Map, Design-Level per Bounded Context, invariants) in five checks and writes a report whose findings each name a code location and a model counterpart. It fixes nothing, and it needs the domain model that `ycore-ddd-big-picture` and `ycore-ddd-design-level` produce; without it every check ends as not checked. Recommend it after `bmad-build` or `bmad-retrospective` finishes an epic, before planning the next one, and whenever the user asks whether the code still matches the model. Afterwards offer `bmad-build` for findings where the code gives way, and an update of the model files for findings where the model gives way.

## How the skills work

Like BMad's own planning skills, the two Event Storming skills know three intents: create, update (a revision round on a named part) and validate (a review report that changes nothing). They offer a Coaching path, the full interview, and a Fast path that drafts the brief or catalog with `[ASSUMPTION]` tags; every assumption becomes a Hotspot that the user decides at the checkpoint, so the Fast path never skips a decision. Before handover a reviewer gate runs independent reviewer subagents (lenses set in `workflow.finalize_reviewers`). Decisions are kept in memlogs in the domain model folder, so a run continues in a new session. Headless, the workshops run up to the first point that needs the user and stop there; the model check runs completely, which suits unattended build loops.

## Where things land

All three skills keep the domain model in `modules.ycore-ddd.domain_model_folder`; the check writes its reports to `modules.ycore-ddd.review_folder`; `bmad setup ycore-ddd` shows and changes the answers.
