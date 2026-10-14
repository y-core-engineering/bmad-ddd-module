# ycore-ddd knowledge

This document covers the skills of the `ycore-ddd` module: what each one gives the user, when to recommend it, and what to offer next.

## The skills

- `ycore-ddd-big-picture`: prepares a Big-Picture Event Storming in an interview about the product idea, then facilitates it with a team of agents over up to six rounds, ending in `context-map.md`, `ubiquitous-language.md` and `event-storming.md` in the domain model folder; a run resumes in a new session from its files. Recommend it after a product brief or PRFAQ and before `bmad-prd`, or when the user wants to find Bounded Contexts, a Context Map or a glossary. Afterwards offer `bmad-prd` with the three artifacts as input, and `ycore-ddd-model-check` once code exists.
- `ycore-ddd-model-check`: checks the code against the domain model (glossary, Context Map, Design-Level per Bounded Context, invariants) in five checks and writes a report whose findings each name a code location and a model counterpart. It fixes nothing, and it needs an existing domain model (`ubiquitous-language.md`, `context-map.md`, `<context>/design.md` with `❗` invariants); `ycore-ddd-big-picture` produces the glossary and Context Map, while the `design.md` files still have to be provided; without a model every check ends as not checked. Recommend it after `bmad-build` or `bmad-retrospective` finishes an epic, before planning the next one, and whenever the user asks whether the code still matches the model. Afterwards offer `bmad-build` for findings where the code gives way, and an update of the model files for findings where the model gives way.

## Where things land

Both skills keep the domain model in `modules.ycore-ddd.domain_model_folder`; the check writes its reports to `modules.ycore-ddd.review_folder`; `bmad setup ycore-ddd` shows and changes the answers.
