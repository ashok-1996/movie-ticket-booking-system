# Movie Ticket Booking System

A concurrency-safe movie ticket booking backend built with Spring Boot. The design goal is correctness under concurrent load: **the same seat can never be sold twice**, seat holds expire automatically, booking is atomic, and downstream notifications never block the customer's request.

---

## 1. Problem interpretation and scope

The requirement (multi-city theaters, seat-level booking, time-bound holds, pricing tiers, discounts, refunds, non-blocking notifications) is intentionally open-ended. I optimized for **depth on the hard part (concurrency) over breadth**, keeping the role surface small (ADMIN, CUSTOMER) so the effort goes into a defensible booking engine and strong tests.

### Built (in scope)
- REST APIs for the full flow: auth, admin catalog/pricing/discount/refund management, browse, seat hold, booking confirm, cancel/refund, booking history.
- Seat selection with **time-bound holds** that auto-release on expiry.
- **Concurrency-safe booking** with a three-layer defense (see §4).
- Multiple pricing tiers (REGULAR/PREMIUM/RECLINER) + configurable weekend surcharge.
- Discount codes (percent/flat, caps, min-amount, validity window).
- Configurable, tiered **refund policy** on cancellation.
- **Asynchronous, non-blocking** confirmation/reminder notifications (mock adapter).
- Append-only **audit trail** of state transitions.
- Role-based access control (JWT), input validation, consistent error responses.
- Unit + integration tests, including a concurrency race test on a real PostgreSQL.

### Not built (out of scope, per the brief)
UI/frontend, deployment/CI-CD, microservices, OAuth/SSO/MFA, production observability.

---

## 2. Tech stack and rationale

| Concern | Choice | Why |
|---|---|---|
| Language/runtime | Java 21 | Modern LTS |
| Framework | Spring Boot 3.3 | Mature web + transaction stack (required) |
| Persistence | Spring Data JPA + PostgreSQL | ACID + row-level locking (`SELECT ... FOR UPDATE`) is central to correctness |
| Migrations | Flyway | Versioned, reproducible schema |
| Locking | Pessimistic lock + optimistic `@Version` + partial unique index | Three independent layers of protection |
| Scheduling | Spring `@Scheduled` | Hold-expiry sweeper, no extra infra |
| Async | `@TransactionalEventListener(AFTER_COMMIT)` + `@Async` bounded pool | Fan-out that never blocks and never fires on a rolled-back tx |
| Security | Spring Security + JWT (jjwt) | Simple stateless RBAC |
| Docs | springdoc-openapi | Swagger UI at `/swagger-ui.html` |
| Tests | JUnit 5, Mockito, **Zonky embedded PostgreSQL** | Real Postgres locking semantics without a Docker daemon |

**Note on test database.** The plan called for Testcontainers, but no Docker daemon was available in the build environment. I used **Zonky embedded PostgreSQL**, which runs a real PostgreSQL 16 binary in-process. This preserves the exact locking/constraint semantics the concurrency tests rely on (H2 would not), with zero Docker dependency. Swapping to Testcontainers is a drop-in change where Docker is available.

---

## 3. Architecture

```
controller  ->  service  ->  repository  ->  PostgreSQL
                   |
                   +-- publishes BookingEvent (AFTER_COMMIT, @Async) --> NotificationListener (mock)
                   +-- writes AuditEvent (append-only)
HoldExpiryScheduler (@Scheduled) --> HoldExpiryService (per-hold REQUIRES_NEW tx)
```

Layering: thin controllers, business logic in `@Transactional` services, Spring Data repositories. DTOs isolate the API from entities.

### Domain model
```
City 1--* Theater 1--* Screen 1--* Seat
Movie 1--* Show (movie + screen + startTime + basePrice)
Show 1--* ShowSeat  (status, price, heldUntil, heldBy, @version)   <-- point of contention
Booking 1--* BookingSeat *--1 ShowSeat ;  Booking 1--1 Payment
PricingTier, DiscountCode, RefundPolicy, User(role), AuditEvent
```
- **Booking lifecycle:** `PENDING -> CONFIRMED -> CANCELLED | REFUNDED`, plus `EXPIRED` when a hold lapses.
- **ShowSeat lifecycle:** `AVAILABLE -> HELD -> BOOKED`, released back to `AVAILABLE` on expiry/cancel.

---

## 4. Concurrency design (the core)

Concurrent attempts to book the same seat are made safe by **three independent layers**:

1. **Pessimistic write lock at hold time.** `ShowSeatRepository.lockByIds(...)` issues `SELECT ... FOR UPDATE` ordered by id. Competing transactions for the same seat serialize; the loser observes the seat as `HELD/BOOKED` and is rejected with `SEAT_UNAVAILABLE`. Locking in **deterministic id order** avoids deadlocks when seat sets overlap.
2. **Optimistic locking.** `ShowSeat` and `Booking` carry a JPA `@Version`; any lost-update race surfaces as an optimistic-lock failure (mapped to `409 CONFLICT`).
3. **Database backstop.** A **partial unique index** `uq_booking_seat_active ON booking_seat(show_seat_id) WHERE active = true` makes it physically impossible for two active allocations to reference the same seat. Correctness therefore does not rely solely on application logic being bug-free. Released allocations are flagged `active = false` (kept for history), so a freed seat can be re-booked without violating the index.

**Atomicity.** Hold and confirm are each `@Transactional`: seat state, booking, and payment commit or roll back together.

**Hold expiry.** Holds carry a configurable TTL (`booking.hold.ttl-seconds`). `HoldExpiryScheduler` runs every `booking.hold.sweep-interval-ms`, expiring lapsed `PENDING` bookings and releasing their seats — each in its own `REQUIRES_NEW` transaction so one failure doesn't abort the batch.

**Non-blocking notifications.** On confirm/cancel a `BookingEvent` is published and handled `AFTER_COMMIT` on a bounded async pool, so the HTTP response returns immediately and no notification is ever sent for a rolled-back booking.

---

## 5. Running locally

### Prerequisites
- Java 21, Maven 3.9+
- A PostgreSQL database (use the bundled compose file, or point to your own)

### Start PostgreSQL (option A: Docker)
```bash
docker compose up -d
```

### Or point to an existing PostgreSQL (option B)
Set env vars: `DB_URL`, `DB_USERNAME`, `DB_PASSWORD` (defaults: `jdbc:postgresql://localhost:5432/moviebooking`, `postgres`/`postgres`).

### Run the app
```bash
mvn spring-boot:run
```
On first start, Flyway applies the schema and reference data, and a demo dataset is seeded (disable with `DEMO_SEED=false`).

- Swagger UI: `http://localhost:8080/swagger-ui.html`
- Seeded accounts: `admin@movies.test / admin123` (ADMIN), `customer@movies.test / customer123` (CUSTOMER)

### Quick demo flow
1. `POST /auth/login` with the customer account -> copy the `token`.
2. `GET /shows` -> pick a `showId`; `GET /shows/{showId}/seats` -> pick `showSeatId`s.
3. `POST /shows/{showId}/holds` (Bearer token) with `{"showSeatIds":[...]}` -> returns a PENDING booking.
4. `POST /bookings/{bookingId}/confirm` with optional `{"discountCode":"SAVE20","paymentMethod":"CARD"}`.
5. `POST /bookings/{bookingId}/cancel` -> refund per policy. `GET /bookings/me` for history.

---

## 6. API reference

| Method | Path | Role | Purpose |
|---|---|---|---|
| POST | `/auth/register` | public | Register (creates CUSTOMER) |
| POST | `/auth/login` | public | Obtain JWT |
| GET | `/shows` | public | Browse shows (filters: `cityId`, `movieId`, `from`, `to`) |
| GET | `/shows/{id}` | public | Show detail |
| GET | `/shows/{id}/seats` | public | Live seat map |
| POST | `/shows/{id}/holds` | CUSTOMER | Hold seats (starts TTL) |
| POST | `/bookings/{id}/confirm` | CUSTOMER | Confirm hold (discount + payment) |
| POST | `/bookings/{id}/cancel` | CUSTOMER | Cancel + refund |
| GET | `/bookings/me` | CUSTOMER | Booking history |
| GET | `/bookings/{id}` | CUSTOMER | Booking detail |
| POST/GET | `/admin/cities`, `/admin/theaters`, `/admin/screens`, `/admin/screens/{id}/seats`, `/admin/movies` | ADMIN | Catalog management |
| POST | `/admin/shows` | ADMIN | Create show (materializes priced seats) |
| POST/PUT/GET | `/admin/pricing-tiers` | ADMIN | Pricing tiers |
| POST/GET | `/admin/discount-codes` | ADMIN | Discount codes |
| POST/PUT/GET | `/admin/refund-policies` | ADMIN | Refund policies |

Errors use a consistent body: `{ timestamp, status, code, message, path, fieldErrors? }` with codes such as `SEAT_UNAVAILABLE`, `HOLD_EXPIRED`, `INVALID_DISCOUNT`, `REFUND_NOT_ALLOWED`, `VALIDATION_ERROR`, `UNAUTHORIZED`, `FORBIDDEN`.

---

## 7. Testing

```bash
mvn test
```

| Test | What it proves |
|---|---|
| `SeatBookingConcurrencyTest` | **The money test.** 20 threads race for one seat -> exactly 1 confirmed, 19 rejected, seat `BOOKED`, no oversell. Runs on real PostgreSQL. |
| `HoldExpiryTest` | An expired hold returns the seat to `AVAILABLE` and the booking to `EXPIRED`. |
| `BookingLifecycleTest` | Hold -> confirm -> cancel (full refund) -> seat freed and re-bookable. |
| `RefundPolicyServiceTest` | Refund amount by cancellation window (parameterized). |
| `DiscountServiceTest` | Percent/flat, max cap, min-amount, validity, cap at order amount. |
| `PricingServiceTest` | Tier multipliers and weekend surcharge. |
| `RbacAndValidationTest` | 401/403 by role, 400 validation, public browse. |

Integration tests use Zonky embedded PostgreSQL (real Postgres 16, no Docker).

---

## 8. Configuration

| Property | Default | Meaning |
|---|---|---|
| `booking.hold.ttl-seconds` | 120 | Seat hold lifetime |
| `booking.hold.sweep-interval-ms` | 5000 | Expiry sweep frequency |
| `pricing.weekend-multiplier` | 1.25 | Weekend surcharge |
| `pricing.zone` | UTC | Time zone for weekend determination |
| `app.jwt.secret` / `app.jwt.expiration-minutes` | (dev default) / 120 | JWT signing |
| `demo.seed` | true | Seed demo data on empty DB |

---

## 9. Key assumptions
- Two roles only (ADMIN, CUSTOMER). Admins are provisioned via seeding, not self-registration.
- Payment is mocked (always succeeds) — real gateways are out of scope.
- Notification delivery is mocked with logging.
- Weekend pricing is derived from the show start time in `pricing.zone` (default UTC).
- `booking_seat` rows are retained for history; the partial unique index enforces uniqueness only over active allocations.
- A freed seat becomes bookable after the next expiry sweep (bounded by the sweep interval).

See [AGENTS.md](AGENTS.md) and [docs/AI_WORKFLOW.md](docs/AI_WORKFLOW.md) for the AI-assisted development workflow, and [docs/prompts](docs/prompts) for the raw prompts used.
