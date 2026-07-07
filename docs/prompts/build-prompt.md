# Build Prompt (raw)

The engineered prompt used to drive implementation of this project.

```
# ROLE
You are a senior Spring Boot engineer. Build a production-quality Movie Ticket Booking System.
Optimize for CORRECTNESS UNDER CONCURRENCY, clean domain modeling, and strong tests over feature quantity.
Make small, logically-scoped commits with clear messages.

# TECH STACK (non-negotiable)
- Java 21, Spring Boot 3.x (Web, Data JPA, Validation, Security)
- PostgreSQL + Flyway migrations
- springdoc-openapi (Swagger UI)
- Tests: JUnit 5, Mockito, real PostgreSQL for integration (Testcontainers, or Zonky embedded if no Docker),
  ExecutorService/CountDownLatch for concurrency
- Build: Maven

# DOMAIN
Entities: City, Theater, Screen, Seat, Movie, Show, ShowSeat, PricingTier(REGULAR/PREMIUM/RECLINER),
DiscountCode, RefundPolicy, Booking, BookingSeat, Payment, User(role ADMIN|CUSTOMER), AuditEvent.
- ShowSeat is the per-show materialization of a seat and the ONLY contention point.
  Fields: status(AVAILABLE|HELD|BOOKED), price, heldUntil, heldBy, @Version version.
- Booking lifecycle: PENDING -> CONFIRMED -> CANCELLED|REFUNDED, plus EXPIRED on hold lapse.

# CORE REQUIREMENTS (full depth)
1. Time-bound seat HOLDS that auto-release on expiry (configurable TTL) via a @Scheduled sweeper.
2. Concurrent booking of the same seat MUST NOT double-allocate. THREE-LAYER defense:
   a. Pessimistic write lock (SELECT ... FOR UPDATE) when acquiring holds, in deterministic order.
   b. Optimistic @Version guard on the confirm path.
   c. DB partial unique index on booking_seat(show_seat_id) WHERE active as a physical backstop.
3. Booking placement is ATOMIC (@Transactional): seat state + booking + payment succeed or roll back together.
4. Pricing tiers + discount codes at confirm; configurable refund policies on cancellation.
5. Confirmation + reminder notifications sent ASYNCHRONOUSLY and NON-BLOCKING via
   @TransactionalEventListener(AFTER_COMMIT) + @Async. Notifications are a logged mock adapter.
6. RBAC via Spring Security + JWT. Admin manages catalog/pricing/policies; Customer browses, holds, books, cancels.
7. Bean Validation on DTOs. Global @RestControllerAdvice with consistent error codes
   (SEAT_UNAVAILABLE, HOLD_EXPIRED, INVALID_DISCOUNT, REFUND_NOT_ALLOWED, ...).
8. Append-only AuditEvent for state transitions.

# API
- POST /auth/register, POST /auth/login
- Admin CRUD: cities, theaters, screens, seat layouts, movies, shows, pricingTiers, discountCodes, refundPolicies
- GET /shows (filter city/movie/date), GET /shows/{id}/seats
- POST /shows/{id}/holds, POST /bookings/{id}/confirm, POST /bookings/{id}/cancel, GET /bookings/me

# TESTS (prioritize)
- CONCURRENCY: N threads racing for the SAME seat on real PostgreSQL -> exactly ONE confirmed, N-1 rejected,
  inventory consistent. Most important test.
- Hold expiry returns seat to AVAILABLE and booking to EXPIRED.
- Refund policy parametrized by cancellation window.
- Unit: pricing/discount math, state transitions.
- Web: validation + RBAC (401/403).

# DELIVERABLES
- README.md: assumptions, run steps, architecture, concurrency rationale, API list.
- OpenAPI/Swagger enabled. Seed/demo data for a runnable demo.

# OUT OF SCOPE (do not build)
UI/frontend, deployment/CI-CD, microservices, OAuth/SSO/MFA, production observability.
```
