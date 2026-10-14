# ycore-ddd

Domain-Driven Design for the BMad Method (BMad Community Module).

BMad elicits requirements thoroughly but does not model the domain: Bounded Context, Context Map, Ubiquitous Language, Event Storming and invariants appear in none of its skills. ycore-ddd adds that step. Its artifacts feed BMad's own PRD, architecture and ticket skills, and after the build it checks the code against the domain model.

Planned scope, derived from the Y-Core Method:

- Big-Picture Event Storming with Context Map and glossary
- Design-Level Event Storming per Bounded Context with invariants
- search for unmarked domain questions before the architecture
- domain model check of the code after the build

Available today: the Big-Picture Event Storming (`ycore-ddd-big-picture`), which writes `context-map.md` and `ubiquitous-language.md`, and the domain model check (`ycore-ddd-model-check`). Until the Design-Level skill exists, the check expects one `<context>/design.md` per Bounded Context with `❗` invariants that you provide in the folder set at `bmad setup ycore-ddd`.

## Development

Skills live in `skills/`, one folder each. BMad v7 with Toolsmith and bmad-eval is installed locally for building and is not part of the repository (`.claude/`, `_bmad/`). To set it up on a new machine:

```
npx skills add bmad-code-org/BMAD-METHOD --skill bmad --skill bmod-core-tools --skill bmad-toolsmith --skill bmod-toolsmith --skill bmad-eval -a claude-code -y
```

Then ask the `bmad` skill for `setup`.

## Licence

MIT, see [LICENSE](LICENSE). The name Y-Core is not covered by the licence.
