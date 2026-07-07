# AGENTS.md

Guidance for AI coding agents (and humans) working in this repository. This is the instruction file used during AI-assisted development.

## Project
Movie Ticket Booking System — a concurrency-safe Spring Boot backend. The single most important property is **no seat is ever sold twice**. Prioritize correctness under concurrency and test strength over feature count.

## Tech constraints
- Java 21, Spring Boot 3.3, Maven.
- PostgreSQL + Flyway (schema is authoritative; `spring.jpa.hibernate.ddl-auto=validate`, never `update`).
- Integration tests run on real PostgreSQL via Zonky embedded database (no Docker daemon required).

## Architecture rules
- Layering: `controller -> service -> repository`. Controllers are thin; business logic and `@Transactional` boundaries live in services. Never put queries in controllers.
- Expose DTOs (`dto/**`), never JPA entities, from controllers.
- All errors go through `ApiException` + `GlobalExceptionHandler`; use the `ErrorCode` enum. Do not return ad-hoc error strings.
- Validate all request DTOs with Bean Validation annotations.

## Concurrency rules (do not weaken)
1. Acquire seats with the pessimistic lock query `ShowSeatRepository.lockByIds` (`SELECT ... FOR UPDATE`), always in deterministic id order.
2. Keep the `@Version` field on `ShowSeat` and `Booking`.
3. Keep the partial unique index `uq_booking_seat_active` on `booking_seat(show_seat_id) WHERE active = true` as the DB backstop. Release seats by setting `active = false`, not by deleting rows.
4. Hold/confirm/cancel must be atomic (`@Transactional`).
5. Notifications must be published via `@TransactionalEventListener(AFTER_COMMIT)` and run `@Async` — never inline in the request path.

## Testing rules
- The concurrency race test (`SeatBookingConcurrencyTest`) is the highest-value test; keep it green and meaningful (N threads, one seat, exactly one winner).
- Integration tests use `@IntegrationTest` (`@SpringBootTest` + Zonky). Unit tests for pure logic (pricing/discount/refund) use Mockito, no Spring.
- Run `mvn test` before considering work complete.

## Conventions
- Small, focused commits with conventional messages (`feat:`, `fix:`, `test:`, `docs:`).
- Do not add comments that restate the code; comment only non-obvious intent (e.g., why a lock order is chosen).
- Keep the role surface to ADMIN and CUSTOMER.

## Build / run
- Build: `mvn -B -DskipTests package`
- Test: `mvn test`
- Run: `mvn spring-boot:run` (needs PostgreSQL; `docker compose up -d` provides one)
