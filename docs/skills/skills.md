# Skills / Tools Used During Development

- **Cursor AI agent** — primary AI pair-programmer used to plan and implement the codebase.
- **Plan mode** — used to produce and confirm an implementation plan before any code was written.
- **Repository conventions via [AGENTS.md](../../AGENTS.md)** — persistent guidance so the agent respected architecture and concurrency invariants on every edit.
- **Automated test loop** — `mvn test` used as the verification harness (JUnit 5, Mockito, Zonky embedded PostgreSQL).

No custom Cursor Skills, rules packs, or MCP servers were required for this assignment beyond the standard agent workflow above.
