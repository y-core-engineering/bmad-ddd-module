# Security policy

ycore-ddd consists of prompt files for AI agents and small Python scripts that check Markdown files. The scripts use only the Python standard library and make no network calls.

## Reporting a vulnerability

Please report security issues privately, not in a public issue:

- through GitHub: the "Report a vulnerability" button on the Security tab of this repository, or
- by email to [sebastian.herden@ycore.engineering](mailto:sebastian.herden@ycore.engineering).

Relevant reports include a script that can be made to read or write outside the folder it is given, and a skill instruction that leads an agent to act outside the project or to disclose data it should not.
