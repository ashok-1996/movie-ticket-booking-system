# Loom Recording Script (target <= 10 minutes)

A tight talk-track for the required video. Time budget in brackets.

## 0. Intro [0:30]
- "This is a Movie Ticket Booking System in Spring Boot. My design goal was one thing above all: a seat can never be sold twice, even under heavy concurrency."
- "I deliberately kept scope tight — two roles — and spent the effort on a bulletproof, well-tested booking engine."

## 1. Approach & solution at a high level [1:30]
- Show the domain diagram in the README.
- Explain the lifecycle: browse -> hold (time-bound) -> confirm (pay) -> optionally cancel (refund).
- Call out `ShowSeat` as the single point of contention (per-show materialization of a seat).

## 2. Tech stack and why [1:30]
- Java 21 + Spring Boot 3.3.
- PostgreSQL specifically because I rely on real row-level locking (`SELECT ... FOR UPDATE`) and a partial unique index.
- Flyway for authoritative, versioned schema (Hibernate is `validate`, never `update`).
- Zonky embedded PostgreSQL for tests (real Postgres, no Docker) — honest locking semantics, unlike H2.

## 3. The concurrency design — the heart of it [2:30]
- Open `BookingService.hold` and `ShowSeatRepository.lockByIds`.
- Walk the **three-layer defense**:
  1. Pessimistic `FOR UPDATE` lock, acquired in deterministic id order (deadlock-free) — serializes racers; losers see HELD/BOOKED and get `SEAT_UNAVAILABLE`.
  2. Optimistic `@Version` on `ShowSeat`/`Booking` — catches lost updates -> 409.
  3. Partial unique index `booking_seat(show_seat_id) WHERE active` — the database physically forbids two active allocations. "Correctness doesn't depend on my code being bug-free."
- Mention atomic `@Transactional` hold/confirm, and the `@Scheduled` expiry sweeper releasing lapsed holds.
- Show the async notification: `@TransactionalEventListener(AFTER_COMMIT)` + `@Async` — response never blocks, never notifies on rollback.

## 4. The AI workflow [1:30]
- Plan-first: produced and confirmed an implementation plan before coding.
- One engineered build prompt (`docs/prompts/build-prompt.md`) + durable rules in `AGENTS.md` that the agent had to respect on every edit (layering, concurrency invariants, testing).
- Verification loop: I let the test suite — especially the race test — prove correctness; fixed real issues found by running it (Zonky provider wiring; a Postgres null-parameter type-inference bug fixed by moving show search to a JPA Specification).

## 5. Testing — demonstrate, don't assert [2:00]
- Open `SeatBookingConcurrencyTest`: 20 threads, one seat, `CountDownLatch` to maximize contention.
- Run it live (or show the green result): exactly 1 CONFIRMED, 19 rejected, seat BOOKED, no oversell — on a real embedded Postgres.
- Briefly show `HoldExpiryTest`, `BookingLifecycleTest` (confirm -> full refund -> seat re-bookable), and the parameterized refund test.
- `mvn test` -> 26 tests green.

## 6. Close [0:30]
- "Depth over breadth: a small, correct, well-tested core with a concurrency story I can defend line by line. Thanks for watching."
