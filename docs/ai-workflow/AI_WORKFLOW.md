# AI-Assisted Development Workflow

This project was built with an AI coding agent (Cursor). This document describes how AI was used, for transparency and reproducibility.

## Approach
1. **Framing / selection.** Analyzed the requirement and the evaluation rubric, then scoped deliberately: two roles, depth on the concurrency engine over breadth of features.
2. **Plan first.** Produced an explicit implementation plan (architecture, domain model, API surface, concurrency strategy, test plan, milestone breakdown) before writing code.
3. **Layered implementation.** Built bottom-up: schema + entities -> repositories -> auth/RBAC -> admin catalog -> browse -> hold/booking concurrency core -> async notifications -> tests -> docs.
4. **Verification loop.** Compiled and ran the test suite iteratively; fixed issues (e.g., the Zonky provider dependency, and a PostgreSQL `:param IS NULL` type-inference issue resolved by switching show search to a JPA Specification).

## How AI was directed
- A single, detailed "build prompt" (see [prompts/build-prompt.md](../prompts/build-prompt.md)) defined the stack, domain, the mandatory three-layer concurrency defense, the API, and the test priorities.
- [AGENTS.md](../../AGENTS.md) captured durable rules the agent had to respect on every change (layering, concurrency invariants, testing).
- Tight, testable acceptance criteria (especially the concurrency race test) kept the agent honest — correctness was demonstrated, not asserted.

## What AI produced vs. verified
- Produced: entities, migrations, services, controllers, security, tests, and documentation.
- Verified by execution: `mvn test` runs a 20-thread race against a real embedded PostgreSQL and asserts exactly one booking wins with no oversell.

## Environment note
No Docker daemon was available, so integration tests use Zonky embedded PostgreSQL (a real Postgres binary) instead of Testcontainers, preserving true locking semantics.
