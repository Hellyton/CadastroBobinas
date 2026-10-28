## Approach
- Read existing files before writing. Don't re-read unless changed.
- Thorough in reasoning, concise in output.
- Skip files over 100KB unless required.
- No sycophantic openers or closing fluff.
- No emojis or em-dashes.
- Do not guess APIs, versions, flags, commit SHAs, or package names. Verify by reading code or docs before asserting.

## Validation
- Project rules for validation and docs are in AGENTS.md.
- Small UI fixes: run only existing tests for the area. Do not create tests, copy the app, or start test servers.
- Changes that alter data (import, parser, DB, bulk fixes, auth): full validation per AGENTS.md.
