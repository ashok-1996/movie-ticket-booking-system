"""
Generates a comprehensive Test Cases document (PDF) for the
Movie Ticket Booking System.

Covers test cases from Level 0 (smoke) to advanced end-to-end and
concurrency scenarios, and explains how to execute each test case
manually (curl / Postman / automated harness).

Run:  python docs/generate_test_cases_pdf.py
Output: docs/Movie-Booking-Test-Cases.pdf
"""

from fpdf import FPDF
from datetime import date

# ---------------------------------------------------------------------------
# Text sanitising: core PDF fonts are latin-1 only, so map common unicode
# glyphs used in the content to safe ASCII equivalents.
# ---------------------------------------------------------------------------
_REPLACEMENTS = {
    "\u2192": "->", "\u2190": "<-", "\u2194": "<->",
    "\u21b3": "->", "\u2265": ">=", "\u2264": "<=",
    "\u00d7": "x", "\u2705": "[OK]", "\u274c": "[X]",
    "\u2013": "-", "\u2014": "-", "\u2018": "'", "\u2019": "'",
    "\u201c": '"', "\u201d": '"', "\u20b9": "Rs.", "\u2022": "-",
    "\u2026": "...", "\u00a0": " ",
}


def s(text):
    if text is None:
        return ""
    text = str(text)
    for k, v in _REPLACEMENTS.items():
        text = text.replace(k, v)
    return text.encode("latin-1", "replace").decode("latin-1")


# ---------------------------------------------------------------------------
# Colours
# ---------------------------------------------------------------------------
NAVY = (23, 42, 69)
BLUE = (37, 99, 175)
LIGHT = (238, 243, 250)
GREY = (110, 110, 110)
GREEN = (33, 120, 70)
ROW_ALT = (247, 249, 252)
BORDER = (205, 214, 226)
DARK = (33, 37, 41)


class PDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_auto_page_break(auto=True, margin=16)
        self.set_margins(15, 15, 15)
        self.section_title = ""

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*GREY)
        self.set_y(8)
        self.cell(0, 5, s("Movie Ticket Booking System - Test Cases"), 0, 0, "L")
        self.cell(0, 5, s(self.section_title), 0, 1, "R")
        self.set_draw_color(*BORDER)
        self.set_line_width(0.2)
        self.line(15, 14, 195, 14)

    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-12)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*GREY)
        self.cell(0, 5, s("Page %d" % self.page_no()), 0, 0, "C")


pdf = PDF()
EPW = pdf.epw  # effective page width


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------
def ensure_space(h):
    if pdf.get_y() + h > pdf.h - pdf.b_margin:
        pdf.add_page()


def h1(text):
    pdf.add_page()
    pdf.set_fill_color(*NAVY)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 15)
    pdf.set_x(15)
    pdf.multi_cell(EPW, 11, s(text), 0, "L", fill=True)
    pdf.ln(3)
    pdf.set_text_color(*DARK)


def h2(text):
    ensure_space(14)
    pdf.ln(2)
    pdf.set_text_color(*BLUE)
    pdf.set_font("Helvetica", "B", 12.5)
    pdf.multi_cell(EPW, 7, s(text), 0, "L")
    pdf.set_draw_color(*BLUE)
    pdf.set_line_width(0.3)
    y = pdf.get_y()
    pdf.line(15, y, 195, y)
    pdf.ln(2)
    pdf.set_text_color(*DARK)


def h3(text):
    ensure_space(10)
    pdf.ln(1)
    pdf.set_text_color(*NAVY)
    pdf.set_font("Helvetica", "B", 11)
    pdf.multi_cell(EPW, 6, s(text), 0, "L")
    pdf.set_text_color(*DARK)
    pdf.ln(0.5)


def para(text, size=10):
    pdf.set_font("Helvetica", "", size)
    pdf.set_text_color(*DARK)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(EPW, 5, s(text), 0, "L")
    pdf.ln(1)


def bullets(items, size=10):
    pdf.set_font("Helvetica", "", size)
    pdf.set_text_color(*DARK)
    for it in items:
        ensure_space(6)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(EPW, 5, s("-  " + it), 0, "L")
    pdf.ln(1)


def code_block(text):
    ensure_space(10)
    pdf.set_font("Courier", "", 8)
    pdf.set_fill_color(244, 246, 249)
    pdf.set_text_color(20, 20, 20)
    pdf.set_draw_color(*BORDER)
    width = 106  # chars that fit at Courier 8pt within the page width
    for raw in text.split("\n"):
        raw = s(raw)
        first = True
        while True:
            prefix = "  " if first else "      "
            avail = max(10, width - len(prefix))
            if len(raw) <= avail:
                ensure_space(5)
                pdf.set_x(15)
                pdf.cell(EPW, 4.4, prefix + raw, 0, 1, "L", fill=True)
                break
            cut = raw.rfind(" ", 0, avail)
            if cut <= 0:
                cut = avail  # no break point: hard wrap, always advances
            ensure_space(5)
            pdf.set_x(15)
            pdf.cell(EPW, 4.4, prefix + raw[:cut], 0, 1, "L", fill=True)
            raw = raw[cut:].lstrip()
            first = False
    pdf.set_text_color(*DARK)
    pdf.ln(1.5)


def kv_table(rows):
    """Two-column key/value table."""
    label_w = 42
    val_w = EPW - label_w
    pdf.set_font("Helvetica", "", 9.5)
    for i, (k, v) in enumerate(rows):
        pdf.set_font("Helvetica", "B", 9.5)
        line_count = max(
            1,
            len(pdf.multi_cell(val_w - 3, 4.8, s(v), 0, "L", dry_run=True, output="LINES")),
        )
        h = max(6.5, line_count * 4.8 + 1.6)
        ensure_space(h)
        x0, y0 = pdf.get_x(), pdf.get_y()
        pdf.set_fill_color(*LIGHT)
        pdf.set_draw_color(*BORDER)
        pdf.rect(x0, y0, label_w, h, "DF")
        pdf.set_text_color(*NAVY)
        pdf.set_xy(x0 + 1.5, y0 + 0.8)
        pdf.multi_cell(label_w - 2, 4.8, s(k), 0, "L")
        pdf.set_font("Helvetica", "", 9.5)
        pdf.set_text_color(*DARK)
        pdf.set_draw_color(*BORDER)
        pdf.rect(x0 + label_w, y0, val_w, h, "D")
        pdf.set_xy(x0 + label_w + 1.5, y0 + 0.8)
        pdf.multi_cell(val_w - 3, 4.8, s(v), 0, "L")
        pdf.set_xy(x0, y0 + h)
        pdf.set_font("Helvetica", "B", 9.5)
    pdf.ln(1)


def data_table(headers, rows, widths):
    """Generic bordered table with header row and zebra striping."""
    total = sum(widths)
    widths = [w / total * EPW for w in widths]
    # header
    ensure_space(9)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(*NAVY)
    pdf.set_text_color(255, 255, 255)
    pdf.set_draw_color(*BORDER)
    x0 = pdf.get_x()
    y0 = pdf.get_y()
    for w, htxt in zip(widths, headers):
        pdf.cell(w, 7, s(htxt), 1, 0, "C", fill=True)
    pdf.ln(7)
    # body
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(*DARK)
    for ri, row in enumerate(rows):
        # compute row height
        heights = []
        for w, cell in zip(widths, row):
            lines = pdf.multi_cell(w - 2, 4.4, s(cell), 0, "L", dry_run=True, output="LINES")
            heights.append(max(1, len(lines)))
        rh = max(heights) * 4.4 + 2
        ensure_space(rh)
        if pdf.get_x() != x0:
            pdf.set_x(x0)
        y = pdf.get_y()
        fill = ri % 2 == 1
        if fill:
            pdf.set_fill_color(*ROW_ALT)
        x = pdf.get_x()
        for w, cell in zip(widths, row):
            pdf.set_draw_color(*BORDER)
            pdf.rect(x, y, w, rh, "DF" if fill else "D")
            pdf.set_xy(x + 1, y + 1)
            pdf.multi_cell(w - 2, 4.4, s(cell), 0, "L")
            x += w
            pdf.set_xy(x, y)
        pdf.set_xy(x0, y + rh)
    pdf.ln(2)


# ---------------------------------------------------------------------------
# Test case renderer
# ---------------------------------------------------------------------------
PRIO_COLORS = {"P0": (192, 57, 43), "P1": (211, 128, 20), "P2": (39, 120, 70)}


def test_case(tc):
    """tc is a dict with keys: id, title, prio, type, pre, steps, data,
    expected, manual (curl/steps), notes(optional)."""
    ensure_space(30)
    pdf.ln(1)
    # Title bar
    pdf.set_font("Helvetica", "B", 10.5)
    pdf.set_fill_color(*LIGHT)
    pdf.set_draw_color(*BLUE)
    pdf.set_text_color(*NAVY)
    y0 = pdf.get_y()
    pdf.set_x(15)
    # priority badge
    prio = tc.get("prio", "P1")
    pc = PRIO_COLORS.get(prio, BLUE)
    badge_w = 12
    title = "%s  %s" % (tc["id"], tc["title"])
    pdf.set_fill_color(*pc)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(badge_w, 7, s(prio), 0, 0, "C", fill=True)
    pdf.set_fill_color(*LIGHT)
    pdf.set_text_color(*NAVY)
    pdf.cell(EPW - badge_w, 7, s("  " + title), 0, 1, "L", fill=True)
    pdf.set_text_color(*DARK)

    rows = []
    rows.append(("Type", tc.get("type", "Functional")))
    if tc.get("pre"):
        rows.append(("Preconditions", tc["pre"]))
    kv_table(rows)

    # Steps
    pdf.set_font("Helvetica", "B", 9.5)
    pdf.set_text_color(*NAVY)
    ensure_space(6)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(EPW, 5, s("Steps:"), 0, "L")
    pdf.set_text_color(*DARK)
    pdf.set_font("Helvetica", "", 9.5)
    for i, st in enumerate(tc["steps"], 1):
        ensure_space(6)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(EPW, 5, s("%d.  %s" % (i, st)), 0, "L")
    pdf.ln(0.5)

    if tc.get("data"):
        pdf.set_font("Helvetica", "B", 9.5)
        pdf.set_text_color(*NAVY)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(EPW, 5, s("Test data:"), 0, "L")
        pdf.set_text_color(*DARK)
        pdf.set_font("Helvetica", "", 9.5)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(EPW, 5, s(tc["data"]), 0, "L")
        pdf.ln(0.5)

    # Expected
    pdf.set_font("Helvetica", "B", 9.5)
    pdf.set_text_color(*GREEN)
    ensure_space(6)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(EPW, 5, s("Expected result:"), 0, "L")
    pdf.set_text_color(*DARK)
    pdf.set_font("Helvetica", "", 9.5)
    exp = tc["expected"]
    if isinstance(exp, list):
        for e in exp:
            ensure_space(6)
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(EPW, 5, s("-  " + e), 0, "L")
    else:
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(EPW, 5, s(exp), 0, "L")
    pdf.ln(0.5)

    # Manual test
    if tc.get("manual"):
        pdf.set_font("Helvetica", "B", 9.5)
        pdf.set_text_color(*BLUE)
        ensure_space(6)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(EPW, 5, s("How to test manually:"), 0, "L")
        pdf.set_text_color(*DARK)
        if isinstance(tc["manual"], list):
            for m in tc["manual"]:
                if m.startswith("$") or m.startswith("curl") or m.startswith("  "):
                    code_block(m[1:] if m.startswith("$") else m)
                else:
                    pdf.set_font("Helvetica", "", 9.5)
                    ensure_space(6)
                    pdf.set_x(pdf.l_margin)
                    pdf.multi_cell(EPW, 5, s(m), 0, "L")
        else:
            code_block(tc["manual"])
    pdf.ln(2)
    pdf.set_draw_color(*BORDER)
    pdf.set_line_width(0.2)
    y = pdf.get_y()
    pdf.line(15, y, 195, y)
    pdf.ln(1)


# ===========================================================================
#  COVER PAGE
# ===========================================================================
pdf.add_page()
pdf.set_fill_color(*NAVY)
pdf.rect(0, 0, 210, 297, "F")
pdf.set_y(70)
pdf.set_text_color(255, 255, 255)
pdf.set_font("Helvetica", "B", 30)
pdf.multi_cell(EPW, 14, s("Movie Ticket Booking System"), 0, "C")
pdf.ln(4)
pdf.set_font("Helvetica", "B", 20)
pdf.set_text_color(120, 190, 255)
pdf.multi_cell(EPW, 11, s("Master Test Case Document"), 0, "C")
pdf.ln(8)
pdf.set_font("Helvetica", "", 13)
pdf.set_text_color(220, 228, 240)
pdf.multi_cell(EPW, 7, s("End-to-end test coverage: from Level 0 smoke tests"), 0, "C")
pdf.multi_cell(EPW, 7, s("to advanced concurrency and E2E scenarios"), 0, "C")
pdf.ln(20)
pdf.set_draw_color(120, 190, 255)
pdf.set_line_width(0.5)
pdf.line(55, pdf.get_y(), 155, pdf.get_y())
pdf.ln(8)
pdf.set_font("Helvetica", "", 11)
pdf.set_text_color(210, 220, 235)
pdf.multi_cell(EPW, 6, s("Spring Boot 3.3  -  Java 21  -  PostgreSQL + Flyway"), 0, "C")
pdf.multi_cell(EPW, 6, s("JWT Security  -  Pessimistic + Optimistic Locking"), 0, "C")
pdf.ln(18)
pdf.set_font("Helvetica", "", 10)
pdf.set_text_color(180, 195, 215)
pdf.multi_cell(EPW, 6, s("Generated: %s" % date.today().strftime("%d %B %Y")), 0, "C")
pdf.multi_cell(EPW, 6, s("Version 1.0"), 0, "C")


# ===========================================================================
#  1. INTRODUCTION
# ===========================================================================
pdf.section_title = "Introduction"
h1("1. Introduction & Scope")
para(
    "This document is the master test-case catalogue for the Movie Ticket Booking "
    "System backend. It is organised as a progression of maturity levels, starting "
    "at Level 0 (environment smoke tests) and building up to advanced, concurrency-"
    "sensitive, end-to-end business scenarios."
)
para(
    "The single most important invariant of the system is: NO SEAT IS EVER SOLD "
    "TWICE. A large share of the advanced test cases exist specifically to prove "
    "that invariant holds under concurrent load, database contention, and hold "
    "expiry."
)
h3("The 'why' behind the levels")
bullets([
    "Level 0 - Smoke: prove the app boots, schema migrates, and docs are reachable.",
    "Level 1 - Authentication: registration and login correctness.",
    "Level 2 - Authorisation / RBAC: who can call what (ADMIN vs CUSTOMER vs anonymous).",
    "Level 3 - Input Validation: bean-validation on every request DTO.",
    "Level 4 - Admin Catalog: cities, theaters, screens, seats, movies.",
    "Level 5 - Pricing / Discount / Refund configuration.",
    "Level 6 - Show management and public browsing/search.",
    "Level 7 - Booking lifecycle happy paths (hold -> confirm -> cancel).",
    "Level 8 - Booking negative & edge cases.",
    "Level 9 - Hold expiry (scheduler + confirm-time).",
    "Level 10 - Concurrency (the crown jewel): one seat, many buyers, one winner.",
    "Level 11 - End-to-end journeys and non-functional checks.",
])
h3("Priority legend")
bullets([
    "P0 - Critical. A failure blocks release (correctness / money / double-sell).",
    "P1 - High. Core functionality; must pass before sign-off.",
    "P2 - Medium. Validation, edge cases, and nice-to-have coverage.",
])


# ===========================================================================
#  2. SYSTEM UNDER TEST
# ===========================================================================
pdf.section_title = "System Overview"
h1("2. System Under Test")
para(
    "A concurrency-safe REST backend for booking cinema seats. Layering is strictly "
    "controller -> service -> repository. Controllers are thin; all business logic "
    "and @Transactional boundaries live in the service layer."
)
h2("2.1 Key components")
data_table(
    ["Area", "Detail"],
    [
        ["Auth", "JWT bearer tokens; roles ADMIN and CUSTOMER; stateless."],
        ["Booking core", "hold -> confirm -> cancel, all @Transactional."],
        ["Seat locking", "Pessimistic SELECT ... FOR UPDATE in deterministic id order."],
        ["Optimistic lock", "@Version on ShowSeat and Booking."],
        ["DB backstop", "Partial unique index uq_booking_seat_active on booking_seat(show_seat_id) WHERE active = true."],
        ["Hold expiry", "TTL (default 120s) swept by scheduler + checked at confirm."],
        ["Pricing", "base x seatClass multiplier x weekend multiplier."],
        ["Notifications", "@TransactionalEventListener(AFTER_COMMIT) + @Async."],
        ["Errors", "ApiException + GlobalExceptionHandler + ErrorCode enum."],
    ],
    [22, 78],
)
h2("2.2 Booking state machine")
code_block(
    "PENDING  --confirm-->  CONFIRMED  --cancel(refund=0)-->  CANCELLED\n"
    "                                 --cancel(refund>0)-->  REFUNDED\n"
    "PENDING  --hold TTL exceeded-->  EXPIRED\n"
    "\n"
    "ShowSeat:  AVAILABLE <-> HELD -> BOOKED\n"
    "           (cancel / expiry releases HELD or BOOKED back to AVAILABLE)"
)
h2("2.3 Error codes reference")
data_table(
    ["ErrorCode", "HTTP", "Raised when"],
    [
        ["VALIDATION_ERROR", "400", "Bean validation / seat-show mismatch"],
        ["INVALID_DISCOUNT", "400", "Bad / inactive / expired / below-min discount"],
        ["UNAUTHORIZED", "401", "Missing or invalid authentication"],
        ["INVALID_CREDENTIALS", "401", "Wrong email/password on login"],
        ["FORBIDDEN", "403", "Wrong role or not the booking owner"],
        ["NOT_FOUND", "404", "Entity id does not exist"],
        ["CONFLICT", "409", "Wrong booking state / duplicate city or code"],
        ["SEAT_UNAVAILABLE", "409", "Seat not AVAILABLE / concurrency loss"],
        ["HOLD_EXPIRED", "409", "Confirm attempted after hold TTL"],
        ["REFUND_NOT_ALLOWED", "409", "Cancel of a non-CONFIRMED booking"],
        ["EMAIL_ALREADY_USED", "409", "Duplicate registration email"],
        ["INTERNAL_ERROR", "500", "Unhandled exception"],
    ],
    [30, 12, 58],
)


# ===========================================================================
#  3. TEST ENVIRONMENT & HOW TO TEST MANUALLY
# ===========================================================================
pdf.section_title = "Environment & Manual Testing"
h1("3. Test Environment & Manual Testing Guide")
para(
    "Every test case below has a 'How to test manually' section. This chapter "
    "describes the one-time setup so those instructions work as-is."
)
h2("3.1 Start the application")
bullets([
    "Ensure PostgreSQL is running. Quickest: 'docker compose up -d' from repo root.",
    "Build without tests: mvn -B -DskipTests package",
    "Run: mvn spring-boot:run   (defaults to http://localhost:8080)",
    "Flyway applies V1 schema + V2 seed data automatically on startup.",
    "With demo.seed=true (default), an admin, a customer and a demo catalog are seeded.",
])
h2("3.2 Seeded credentials (demo.seed=true, empty DB)")
data_table(
    ["Role", "Email", "Password"],
    [
        ["ADMIN", "admin@movies.test", "admin123"],
        ["CUSTOMER", "customer@movies.test", "customer123"],
    ],
    [20, 45, 30],
)
h2("3.3 Tooling options for manual testing")
bullets([
    "Swagger UI (recommended for exploration): http://localhost:8080/swagger-ui.html - lets you Authorize with a bearer token then click Execute on any endpoint.",
    "Postman / Insomnia: import the endpoints, set a collection variable {{token}}, add header 'Authorization: Bearer {{token}}'.",
    "curl (used in this document): copy/paste the snippets. On Windows PowerShell prefer curl.exe to avoid the Invoke-WebRequest alias.",
    "Database inspection (psql / DBeaver): verify show_seat.status, booking.status, booking_seat.active, payment.status directly.",
    "Automated: mvn test runs the JUnit suite including the concurrency race test.",
])
h2("3.4 Get a token (used by most manual steps)")
para("Log in and capture the JWT. All authenticated calls reuse it as $TOKEN / $ADMIN_TOKEN.")
code_block(
    "# Customer token\n"
    "curl -s -X POST http://localhost:8080/auth/login \\\n"
    "  -H \"Content-Type: application/json\" \\\n"
    "  -d '{\"email\":\"customer@movies.test\",\"password\":\"customer123\"}'\n"
    "# -> copy the \"token\" value into $TOKEN\n"
    "\n"
    "# Admin token\n"
    "curl -s -X POST http://localhost:8080/auth/login \\\n"
    "  -H \"Content-Type: application/json\" \\\n"
    "  -d '{\"email\":\"admin@movies.test\",\"password\":\"admin123\"}'\n"
    "# -> copy the \"token\" value into $ADMIN_TOKEN"
)
para(
    "Tip: to discover a live showId and its show-seat ids for booking cases, call "
    "GET /shows and GET /shows/{showId}/seats (both public)."
)


# ===========================================================================
#  LEVEL 0 - SMOKE
# ===========================================================================
pdf.section_title = "Level 0 - Smoke"
h1("4. Level 0 - Smoke & Environment Tests")
para("Goal: prove the environment is healthy before any functional testing.")

test_case({
    "id": "TC-0.1", "title": "Application boots successfully", "prio": "P0",
    "type": "Smoke / Non-functional",
    "pre": "PostgreSQL running; ports free.",
    "steps": [
        "Start the app with mvn spring-boot:run.",
        "Watch the startup log.",
    ],
    "expected": [
        "Log shows 'Started MovieBookingApplication'.",
        "No stack traces; Tomcat listening on 8080.",
    ],
    "manual": "curl -s -o NUL -w \"%{http_code}\\n\" http://localhost:8080/swagger-ui.html\n# expect 200 (or 302 redirect to the UI)",
})

test_case({
    "id": "TC-0.2", "title": "Flyway migrations apply and schema validates", "prio": "P0",
    "type": "Smoke / DB",
    "pre": "Fresh database.",
    "steps": [
        "Start the app against an empty schema.",
        "Inspect the flyway_schema_history table.",
    ],
    "expected": [
        "V1__init_schema and V2__seed_reference_data are marked success.",
        "Hibernate ddl-auto=validate passes (app does not fail to start).",
        "14 tables exist (app_user, city, theater, screen, seat, movie, show_event, pricing_tier, discount_code, refund_policy, show_seat, booking, booking_seat, payment, audit_event).",
    ],
    "manual": "psql moviebooking -c \"select version, description, success from flyway_schema_history order by installed_rank;\"",
})

test_case({
    "id": "TC-0.3", "title": "Swagger / OpenAPI docs are reachable", "prio": "P2",
    "type": "Smoke",
    "pre": "App running.",
    "steps": ["Open the OpenAPI JSON and the Swagger UI."],
    "expected": [
        "GET /v3/api-docs returns 200 with a valid OpenAPI document.",
        "Swagger UI renders all controllers and an Authorize button.",
    ],
    "manual": "curl -s -o NUL -w \"%{http_code}\\n\" http://localhost:8080/v3/api-docs\n# expect 200",
})

test_case({
    "id": "TC-0.4", "title": "Reference seed data present", "prio": "P1",
    "type": "Smoke / DB",
    "pre": "App started once.",
    "steps": ["Query pricing_tier and refund_policy tables."],
    "expected": [
        "pricing_tier has REGULAR=1.0, PREMIUM=1.5, RECLINER=2.0.",
        "refund_policy 'Standard Policy' with full=24h, partial=4h @ 50%, active=true.",
    ],
    "manual": "psql moviebooking -c \"select seat_class, multiplier from pricing_tier; select * from refund_policy;\"",
})


# ===========================================================================
#  LEVEL 1 - AUTH
# ===========================================================================
pdf.section_title = "Level 1 - Authentication"
h1("5. Level 1 - Authentication")
para("Endpoints: POST /auth/register, POST /auth/login (both public).")

test_case({
    "id": "TC-1.1", "title": "Register a new customer (happy path)", "prio": "P0",
    "type": "Functional",
    "pre": "Email not already used.",
    "steps": [
        "POST /auth/register with a valid email, password (>=6 chars) and fullName.",
    ],
    "data": "{ email: alice@test.com, password: secret1, fullName: Alice }",
    "expected": [
        "201 Created; body contains a JWT token and role=CUSTOMER.",
        "New row in app_user with hashed password (never plaintext).",
        "Self-registration always yields CUSTOMER (never ADMIN).",
    ],
    "manual": "curl -i -X POST http://localhost:8080/auth/register \\\n  -H \"Content-Type: application/json\" \\\n  -d '{\"email\":\"alice@test.com\",\"password\":\"secret1\",\"fullName\":\"Alice\"}'",
})

test_case({
    "id": "TC-1.2", "title": "Login with valid credentials", "prio": "P0",
    "type": "Functional",
    "pre": "User exists (e.g. seeded customer).",
    "steps": ["POST /auth/login with correct email/password."],
    "expected": ["200 OK; body contains a valid JWT usable on protected endpoints."],
    "manual": "curl -i -X POST http://localhost:8080/auth/login \\\n  -H \"Content-Type: application/json\" \\\n  -d '{\"email\":\"customer@movies.test\",\"password\":\"customer123\"}'",
})

test_case({
    "id": "TC-1.3", "title": "Register with invalid email format", "prio": "P1",
    "type": "Validation",
    "pre": "None.",
    "steps": ["POST /auth/register with email='not-an-email'."],
    "expected": [
        "400 Bad Request; code=VALIDATION_ERROR.",
        "fieldErrors contains an entry for 'email'.",
    ],
    "manual": "curl -i -X POST http://localhost:8080/auth/register \\\n  -H \"Content-Type: application/json\" \\\n  -d '{\"email\":\"not-an-email\",\"password\":\"secret1\",\"fullName\":\"Bob\"}'",
})

test_case({
    "id": "TC-1.4", "title": "Register with too-short password", "prio": "P1",
    "type": "Validation",
    "pre": "None.",
    "steps": ["POST /auth/register with a 3-char password."],
    "expected": ["400; VALIDATION_ERROR; fieldErrors mentions 'password' (@Size min=6)."],
    "manual": "curl -i -X POST http://localhost:8080/auth/register \\\n  -H \"Content-Type: application/json\" \\\n  -d '{\"email\":\"bob@test.com\",\"password\":\"abc\",\"fullName\":\"Bob\"}'",
})

test_case({
    "id": "TC-1.5", "title": "Register with missing required fields", "prio": "P2",
    "type": "Validation",
    "pre": "None.",
    "steps": ["POST /auth/register with an empty body {}."],
    "expected": ["400; VALIDATION_ERROR; fieldErrors for email, password, fullName (@NotBlank)."],
    "manual": "curl -i -X POST http://localhost:8080/auth/register \\\n  -H \"Content-Type: application/json\" -d '{}'",
})

test_case({
    "id": "TC-1.6", "title": "Register with an already-used email", "prio": "P1",
    "type": "Negative / Conflict",
    "pre": "Email already registered (e.g. customer@movies.test).",
    "steps": ["POST /auth/register reusing an existing email."],
    "expected": ["409 Conflict; code=EMAIL_ALREADY_USED."],
    "manual": "curl -i -X POST http://localhost:8080/auth/register \\\n  -H \"Content-Type: application/json\" \\\n  -d '{\"email\":\"customer@movies.test\",\"password\":\"secret1\",\"fullName\":\"Dup\"}'",
})

test_case({
    "id": "TC-1.7", "title": "Login with wrong password", "prio": "P1",
    "type": "Negative",
    "pre": "User exists.",
    "steps": ["POST /auth/login with correct email, wrong password."],
    "expected": ["401 Unauthorized; code=INVALID_CREDENTIALS; no token issued."],
    "manual": "curl -i -X POST http://localhost:8080/auth/login \\\n  -H \"Content-Type: application/json\" \\\n  -d '{\"email\":\"customer@movies.test\",\"password\":\"wrongpass\"}'",
})

test_case({
    "id": "TC-1.8", "title": "Login with unknown email", "prio": "P2",
    "type": "Negative",
    "pre": "Email not registered.",
    "steps": ["POST /auth/login with a non-existent email."],
    "expected": ["401; INVALID_CREDENTIALS (message must not reveal whether email exists)."],
    "manual": "curl -i -X POST http://localhost:8080/auth/login \\\n  -H \"Content-Type: application/json\" \\\n  -d '{\"email\":\"ghost@test.com\",\"password\":\"whatever\"}'",
})


# ===========================================================================
#  LEVEL 2 - RBAC / SECURITY
# ===========================================================================
pdf.section_title = "Level 2 - Authorisation"
h1("6. Level 2 - Authorisation & RBAC")
para(
    "Verifies who may call what. Public: /auth/**, GET /shows/**, swagger. "
    "CUSTOMER: booking endpoints. ADMIN: /admin/**."
)

test_case({
    "id": "TC-2.1", "title": "Anonymous cannot access admin endpoint", "prio": "P0",
    "type": "Security",
    "pre": "No Authorization header.",
    "steps": ["Call an /admin endpoint without a token."],
    "expected": ["401 Unauthorized; code=UNAUTHORIZED."],
    "manual": "curl -i http://localhost:8080/admin/cities",
})

test_case({
    "id": "TC-2.2", "title": "CUSTOMER forbidden on admin endpoints", "prio": "P0",
    "type": "Security",
    "pre": "Valid CUSTOMER token ($TOKEN).",
    "steps": ["Call an /admin endpoint with a customer token."],
    "expected": ["403 Forbidden; code=FORBIDDEN."],
    "manual": "curl -i http://localhost:8080/admin/cities \\\n  -H \"Authorization: Bearer $TOKEN\"",
})

test_case({
    "id": "TC-2.3", "title": "ADMIN forbidden on customer booking endpoints", "prio": "P1",
    "type": "Security",
    "pre": "Valid ADMIN token ($ADMIN_TOKEN).",
    "steps": ["Call GET /bookings/me with an admin token (endpoint requires ROLE_CUSTOMER)."],
    "expected": ["403 Forbidden; code=FORBIDDEN (role separation enforced)."],
    "manual": "curl -i http://localhost:8080/bookings/me \\\n  -H \"Authorization: Bearer $ADMIN_TOKEN\"",
})

test_case({
    "id": "TC-2.4", "title": "Anonymous cannot create a hold", "prio": "P0",
    "type": "Security",
    "pre": "None.",
    "steps": ["POST /shows/{id}/holds without a token."],
    "expected": ["401 Unauthorized."],
    "manual": "curl -i -X POST http://localhost:8080/shows/1/holds \\\n  -H \"Content-Type: application/json\" -d '{\"showSeatIds\":[1]}'",
})

test_case({
    "id": "TC-2.5", "title": "Malformed / tampered JWT is rejected", "prio": "P1",
    "type": "Security",
    "pre": "None.",
    "steps": ["Send a protected request with a garbage bearer token."],
    "expected": ["401 Unauthorized; request never reaches the controller."],
    "manual": "curl -i http://localhost:8080/bookings/me \\\n  -H \"Authorization: Bearer not.a.valid.jwt\"",
})

test_case({
    "id": "TC-2.6", "title": "Expired JWT is rejected", "prio": "P2",
    "type": "Security",
    "pre": "A token past app.jwt.expiration-minutes (temporarily lower the config, or wait).",
    "steps": ["Call a protected endpoint with an expired token."],
    "expected": ["401 Unauthorized."],
    "manual": ["Set app.jwt.expiration-minutes to a tiny value in a test profile, log in, wait, then:",
               "curl -i http://localhost:8080/bookings/me -H \"Authorization: Bearer $EXPIRED\""],
})

test_case({
    "id": "TC-2.7", "title": "Public browse allowed without token", "prio": "P1",
    "type": "Security",
    "pre": "None.",
    "steps": ["GET /shows without any Authorization header."],
    "expected": ["200 OK; list returned (read-only browsing is public)."],
    "manual": "curl -i http://localhost:8080/shows",
})


# ===========================================================================
#  LEVEL 3 - VALIDATION (cross-cutting)
# ===========================================================================
pdf.section_title = "Level 3 - Validation"
h1("7. Level 3 - Input Validation")
para(
    "Bean-validation must reject malformed request bodies with 400 VALIDATION_ERROR "
    "and a fieldErrors array, before any business logic runs."
)
data_table(
    ["DTO", "Field", "Rule to violate"],
    [
        ["HoldRequest", "showSeatIds", "@NotEmpty - send empty list"],
        ["ShowDto.Request", "basePrice", "@Positive - send 0 or negative"],
        ["ShowDto.Request", "movieId/screenId/startTime", "@NotNull - omit them"],
        ["CityDto.Request", "name/state", "@NotBlank - send blanks"],
        ["TheaterDto.Request", "cityId", "@NotNull - omit"],
        ["SeatDto.RowSpec", "seatCount", "@Min(1) - send 0"],
        ["MovieDto.Request", "durationMinutes", "@NotNull @Min(1)"],
        ["DiscountCodeDto.Request", "value", "@Positive"],
        ["PricingTierDto.Request", "multiplier", "@DecimalMin(0.0)"],
        ["RefundPolicyDto.Request", "partialRefundPercent", "@DecimalMin/Max 0..100"],
    ],
    [34, 40, 40],
)

test_case({
    "id": "TC-3.1", "title": "Hold with empty seat list rejected", "prio": "P1",
    "type": "Validation",
    "pre": "Valid CUSTOMER token; valid showId.",
    "steps": ["POST /shows/{id}/holds with {\"showSeatIds\":[]}."],
    "expected": ["400; VALIDATION_ERROR; fieldErrors for showSeatIds (@NotEmpty)."],
    "manual": "curl -i -X POST http://localhost:8080/shows/1/holds \\\n  -H \"Authorization: Bearer $TOKEN\" -H \"Content-Type: application/json\" \\\n  -d '{\"showSeatIds\":[]}'",
})

test_case({
    "id": "TC-3.2", "title": "Create show with non-positive base price", "prio": "P1",
    "type": "Validation",
    "pre": "Valid ADMIN token.",
    "steps": ["POST /admin/shows with basePrice = 0."],
    "expected": ["400; VALIDATION_ERROR; fieldErrors for basePrice (@Positive)."],
    "manual": "curl -i -X POST http://localhost:8080/admin/shows \\\n  -H \"Authorization: Bearer $ADMIN_TOKEN\" -H \"Content-Type: application/json\" \\\n  -d '{\"movieId\":1,\"screenId\":1,\"startTime\":\"2027-01-01T18:00:00\",\"basePrice\":0}'",
})

test_case({
    "id": "TC-3.3", "title": "Content-Type / malformed JSON handling", "prio": "P2",
    "type": "Validation",
    "pre": "Valid token.",
    "steps": ["POST a body that is not valid JSON."],
    "expected": ["400 Bad Request; consistent ApiError shape (no stack trace leaked)."],
    "manual": "curl -i -X POST http://localhost:8080/auth/register \\\n  -H \"Content-Type: application/json\" -d '{ this is not json '",
})


# ===========================================================================
#  LEVEL 4 - ADMIN CATALOG
# ===========================================================================
pdf.section_title = "Level 4 - Admin Catalog"
h1("8. Level 4 - Admin Catalog Management")
para("Endpoints under /admin (ADMIN only). Build the physical catalog hierarchy: City -> Theater -> Screen -> Seats, plus Movies.")

test_case({
    "id": "TC-4.1", "title": "Create a city", "prio": "P1",
    "type": "Functional",
    "pre": "ADMIN token.",
    "steps": ["POST /admin/cities with a unique name and state."],
    "expected": ["201 Created; response contains generated id."],
    "manual": "curl -i -X POST http://localhost:8080/admin/cities \\\n  -H \"Authorization: Bearer $ADMIN_TOKEN\" -H \"Content-Type: application/json\" \\\n  -d '{\"name\":\"Bengaluru\",\"state\":\"Karnataka\"}'",
})

test_case({
    "id": "TC-4.2", "title": "Duplicate city name rejected", "prio": "P2",
    "type": "Negative / Conflict",
    "pre": "City 'Bengaluru' already exists.",
    "steps": ["POST /admin/cities with the same name again."],
    "expected": ["409 Conflict; code=CONFLICT (city.name is UNIQUE)."],
    "manual": "curl -i -X POST http://localhost:8080/admin/cities \\\n  -H \"Authorization: Bearer $ADMIN_TOKEN\" -H \"Content-Type: application/json\" \\\n  -d '{\"name\":\"Bengaluru\",\"state\":\"Karnataka\"}'",
})

test_case({
    "id": "TC-4.3", "title": "Create theater, screen and seat layout", "prio": "P1",
    "type": "Functional",
    "pre": "ADMIN token; a cityId exists.",
    "steps": [
        "POST /admin/theaters (with cityId).",
        "POST /admin/screens (with theaterId).",
        "POST /admin/screens/{screenId}/seats with a row layout.",
    ],
    "data": "seats: rows=[{rowLabel:A, seatCount:10, seatClass:REGULAR}, {rowLabel:B, seatCount:8, seatClass:PREMIUM}]",
    "expected": [
        "Each POST returns 201 with an id.",
        "Seat layout returns the created seats; UNIQUE(screen_id,row_label,seat_number) enforced.",
    ],
    "manual": [
        "curl -i -X POST http://localhost:8080/admin/theaters -H \"Authorization: Bearer $ADMIN_TOKEN\" -H \"Content-Type: application/json\" -d '{\"name\":\"PVR\",\"address\":\"MG Road\",\"cityId\":1}'",
        "curl -i -X POST http://localhost:8080/admin/screens -H \"Authorization: Bearer $ADMIN_TOKEN\" -H \"Content-Type: application/json\" -d '{\"name\":\"Screen 1\",\"theaterId\":1}'",
        "curl -i -X POST http://localhost:8080/admin/screens/1/seats -H \"Authorization: Bearer $ADMIN_TOKEN\" -H \"Content-Type: application/json\" -d '{\"rows\":[{\"rowLabel\":\"A\",\"seatCount\":10,\"seatClass\":\"REGULAR\"}]}'",
    ],
})

test_case({
    "id": "TC-4.4", "title": "Create a movie", "prio": "P1",
    "type": "Functional",
    "pre": "ADMIN token.",
    "steps": ["POST /admin/movies with title, language, genre, durationMinutes."],
    "expected": ["201 Created; movie id returned."],
    "manual": "curl -i -X POST http://localhost:8080/admin/movies \\\n  -H \"Authorization: Bearer $ADMIN_TOKEN\" -H \"Content-Type: application/json\" \\\n  -d '{\"title\":\"Inception\",\"language\":\"English\",\"genre\":\"SciFi\",\"durationMinutes\":148,\"certification\":\"UA\"}'",
})

test_case({
    "id": "TC-4.5", "title": "Create entity with non-existent parent id", "prio": "P2",
    "type": "Negative",
    "pre": "ADMIN token.",
    "steps": ["POST /admin/theaters with cityId=999999 (missing)."],
    "expected": ["404 Not Found; code=NOT_FOUND."],
    "manual": "curl -i -X POST http://localhost:8080/admin/theaters \\\n  -H \"Authorization: Bearer $ADMIN_TOKEN\" -H \"Content-Type: application/json\" \\\n  -d '{\"name\":\"Ghost\",\"address\":\"Nowhere\",\"cityId\":999999}'",
})


# ===========================================================================
#  LEVEL 5 - PRICING / DISCOUNT / REFUND CONFIG
# ===========================================================================
pdf.section_title = "Level 5 - Pricing/Discount/Refund"
h1("9. Level 5 - Pricing, Discount & Refund Configuration")

test_case({
    "id": "TC-5.1", "title": "Create and update a pricing tier", "prio": "P1",
    "type": "Functional",
    "pre": "ADMIN token.",
    "steps": [
        "POST /admin/pricing-tiers with seatClass + multiplier.",
        "PUT /admin/pricing-tiers/{id} to change the multiplier.",
    ],
    "expected": ["201 on create, 200 on update; GET reflects the new multiplier."],
    "manual": [
        "curl -i -X POST http://localhost:8080/admin/pricing-tiers -H \"Authorization: Bearer $ADMIN_TOKEN\" -H \"Content-Type: application/json\" -d '{\"name\":\"Premium\",\"seatClass\":\"PREMIUM\",\"multiplier\":1.5}'",
        "curl -i http://localhost:8080/admin/pricing-tiers -H \"Authorization: Bearer $ADMIN_TOKEN\"",
    ],
})

test_case({
    "id": "TC-5.2", "title": "Pricing formula correctness (unit)", "prio": "P0",
    "type": "Unit",
    "pre": "None (PricingServiceTest).",
    "steps": [
        "Compute price for REGULAR weekday, PREMIUM weekday, and PREMIUM weekend.",
    ],
    "data": "base=100; PREMIUM=1.5x; weekend=1.25x.",
    "expected": [
        "REGULAR weekday = 100.00.",
        "PREMIUM weekday = 150.00.",
        "PREMIUM weekend = 187.50 (rounded HALF_UP, 2 dp).",
        "Missing tier defaults multiplier to 1.0.",
    ],
    "manual": "mvn -Dtest=PricingServiceTest test",
})

test_case({
    "id": "TC-5.3", "title": "Create a discount code", "prio": "P1",
    "type": "Functional",
    "pre": "ADMIN token.",
    "steps": ["POST /admin/discount-codes with code, type, value, caps and validity."],
    "data": "SAVE20 = PERCENT 20, maxDiscount=100, minAmount=300, active=true.",
    "expected": ["201 Created; code stored (matching is case-insensitive on use)."],
    "manual": "curl -i -X POST http://localhost:8080/admin/discount-codes \\\n  -H \"Authorization: Bearer $ADMIN_TOKEN\" -H \"Content-Type: application/json\" \\\n  -d '{\"code\":\"SAVE20\",\"type\":\"PERCENT\",\"value\":20,\"maxDiscount\":100,\"minAmount\":300,\"active\":true}'",
})

test_case({
    "id": "TC-5.4", "title": "Discount computation rules (unit)", "prio": "P0",
    "type": "Unit",
    "pre": "None (DiscountServiceTest).",
    "steps": ["Exercise blank code, percent, flat, cap, min-amount, inactive, unknown."],
    "expected": [
        "Blank/null code -> 0 discount.",
        "PERCENT applies value%, capped by maxDiscount.",
        "FLAT applies fixed value.",
        "Discount never exceeds order amount.",
        "Below minAmount / inactive / unknown -> INVALID_DISCOUNT (or 0 per rules).",
    ],
    "manual": "mvn -Dtest=DiscountServiceTest test",
})

test_case({
    "id": "TC-5.5", "title": "Refund policy tiers (unit)", "prio": "P0",
    "type": "Unit",
    "pre": "None (RefundPolicyServiceTest).",
    "steps": ["Compute refund for various hours-before-show on a Rs.500 booking."],
    "expected": [
        ">=24h before -> 100% (Rs.500).",
        ">=4h and <24h -> 50% (Rs.250).",
        "<4h -> 0%.",
    ],
    "manual": "mvn -Dtest=RefundPolicyServiceTest test",
})


# ===========================================================================
#  LEVEL 6 - SHOWS & BROWSING
# ===========================================================================
pdf.section_title = "Level 6 - Shows & Browsing"
h1("10. Level 6 - Show Management & Public Browsing")

test_case({
    "id": "TC-6.1", "title": "Create a show and materialize seats", "prio": "P0",
    "type": "Functional",
    "pre": "ADMIN token; movie + screen (with seats) exist.",
    "steps": ["POST /admin/shows with movieId, screenId, startTime, basePrice."],
    "expected": [
        "201 Created; a show_event row created.",
        "One show_seat row per physical seat, status=AVAILABLE, price computed by PricingService.",
    ],
    "manual": "curl -i -X POST http://localhost:8080/admin/shows \\\n  -H \"Authorization: Bearer $ADMIN_TOKEN\" -H \"Content-Type: application/json\" \\\n  -d '{\"movieId\":1,\"screenId\":1,\"startTime\":\"2027-03-01T18:00:00\",\"basePrice\":200}'",
})

test_case({
    "id": "TC-6.2", "title": "Weekend pricing applied at show creation", "prio": "P1",
    "type": "Functional",
    "pre": "ADMIN token; startTime on a Saturday/Sunday (in pricing.zone).",
    "steps": ["Create a show whose startTime falls on a weekend.", "GET /shows/{id}/seats."],
    "expected": ["show_seat.price includes the weekend multiplier (default 1.25x)."],
    "manual": "curl -s http://localhost:8080/shows/{showId}/seats | more",
})

test_case({
    "id": "TC-6.3", "title": "Public browse all shows", "prio": "P1",
    "type": "Functional",
    "pre": "At least one show exists.",
    "steps": ["GET /shows (no auth)."],
    "expected": ["200 OK; list of ShowDto.Response."],
    "manual": "curl -s http://localhost:8080/shows",
})

test_case({
    "id": "TC-6.4", "title": "Filter shows by city / movie / date range", "prio": "P2",
    "type": "Functional",
    "pre": "Shows exist across cities and dates.",
    "steps": ["GET /shows?cityId=..&movieId=..&from=..&to=.. (ISO date-time)."],
    "expected": ["200 OK; only shows matching all provided filters are returned."],
    "manual": "curl -s \"http://localhost:8080/shows?cityId=1&movieId=1&from=2027-01-01T00:00:00&to=2027-12-31T23:59:59\"",
})

test_case({
    "id": "TC-6.5", "title": "Get a single show and its seat map", "prio": "P1",
    "type": "Functional",
    "pre": "A valid showId.",
    "steps": ["GET /shows/{id} then GET /shows/{id}/seats."],
    "expected": ["200 OK; seat view lists each show-seat id, label, class, price and status."],
    "manual": ["curl -s http://localhost:8080/shows/1", "curl -s http://localhost:8080/shows/1/seats"],
})

test_case({
    "id": "TC-6.6", "title": "Get non-existent show", "prio": "P2",
    "type": "Negative",
    "pre": "None.",
    "steps": ["GET /shows/999999."],
    "expected": ["404 Not Found; code=NOT_FOUND."],
    "manual": "curl -i http://localhost:8080/shows/999999",
})


# ===========================================================================
#  LEVEL 7 - BOOKING LIFECYCLE (HAPPY)
# ===========================================================================
pdf.section_title = "Level 7 - Booking Lifecycle"
h1("11. Level 7 - Booking Lifecycle (Happy Paths)")
para("The core value: hold seats, confirm payment, and cancel with refund. All CUSTOMER-only and @Transactional.")

test_case({
    "id": "TC-7.1", "title": "Hold a single available seat", "prio": "P0",
    "type": "Functional",
    "pre": "CUSTOMER token; a showId with an AVAILABLE show-seat id.",
    "steps": ["POST /shows/{showId}/holds with one showSeatId."],
    "expected": [
        "201 Created; booking status=PENDING; holdExpiresAt = now + ttl (120s).",
        "show_seat -> HELD with heldByUserId set; booking_seat active=true.",
        "totalAmount / finalAmount = that seat's price.",
    ],
    "manual": "curl -i -X POST http://localhost:8080/shows/1/holds \\\n  -H \"Authorization: Bearer $TOKEN\" -H \"Content-Type: application/json\" \\\n  -d '{\"showSeatIds\":[10]}'",
})

test_case({
    "id": "TC-7.2", "title": "Hold multiple seats (amount is the sum)", "prio": "P1",
    "type": "Functional",
    "pre": "CUSTOMER token; several AVAILABLE seats in one show.",
    "steps": ["POST holds with a list of showSeatIds."],
    "expected": [
        "201; all listed seats -> HELD in one atomic transaction.",
        "finalAmount equals the sum of the seat prices.",
        "Seat ids are locked in ascending order (deterministic).",
    ],
    "manual": "curl -i -X POST http://localhost:8080/shows/1/holds \\\n  -H \"Authorization: Bearer $TOKEN\" -H \"Content-Type: application/json\" \\\n  -d '{\"showSeatIds\":[11,12,13]}'",
})

test_case({
    "id": "TC-7.3", "title": "Confirm a held booking (payment)", "prio": "P0",
    "type": "Functional",
    "pre": "A PENDING booking owned by $TOKEN, hold not expired.",
    "steps": ["POST /bookings/{bookingId}/confirm (optional paymentMethod)."],
    "expected": [
        "200 OK; booking status=CONFIRMED; confirmedAt set.",
        "Seats -> BOOKED; hold fields cleared.",
        "Payment row status=SUCCESS, method from request or 'MOCK'.",
        "A CONFIRMED notification fires AFTER commit (async, in logs).",
    ],
    "manual": "curl -i -X POST http://localhost:8080/bookings/1/confirm \\\n  -H \"Authorization: Bearer $TOKEN\" -H \"Content-Type: application/json\" \\\n  -d '{\"paymentMethod\":\"CARD\"}'",
})

test_case({
    "id": "TC-7.3a", "title": "Preview applicable discount coupons before confirming", "prio": "P1",
    "type": "Functional",
    "pre": "A PENDING booking owned by $TOKEN; one or more active discount codes exist (e.g. SAVE20).",
    "steps": [
        "GET /bookings/{bookingId}/discounts.",
        "Inspect the returned coupon options (code, discountAmount, finalAmount).",
    ],
    "expected": [
        "200 OK; totalAmount echoes the booking's seat-price total.",
        "options lists ONLY coupons the customer can actually apply now (active, within validity window, order >= minAmount).",
        "Each option shows discountAmount and the resulting finalAmount; sorted best-saving first.",
        "Coupons below their minimum (e.g. order < minAmount) are omitted.",
        "Read-only: booking stays PENDING; the customer then picks one and confirms (TC-7.4).",
        "409 CONFLICT if the booking is no longer PENDING (already confirmed/cancelled/expired).",
    ],
    "manual": "curl -i http://localhost:8080/bookings/1/discounts \\\n  -H \"Authorization: Bearer $TOKEN\"\n# Response: { bookingId, totalAmount, options: [ {code, type, value, discountAmount, finalAmount} ] }",
})

test_case({
    "id": "TC-7.4", "title": "Confirm with a valid discount code", "prio": "P1",
    "type": "Functional",
    "pre": "PENDING booking with finalAmount >= discount minAmount; SAVE20 active (see preview TC-7.3a).",
    "steps": ["POST confirm with discountCode=SAVE20 (the code chosen from the preview)."],
    "expected": [
        "200; discount applied (20% capped at maxDiscount=100).",
        "Payment amount = finalAmount - discount.",
        "The applied discount matches what TC-7.3a previewed for that code.",
    ],
    "manual": "curl -i -X POST http://localhost:8080/bookings/1/confirm \\\n  -H \"Authorization: Bearer $TOKEN\" -H \"Content-Type: application/json\" \\\n  -d '{\"discountCode\":\"SAVE20\",\"paymentMethod\":\"CARD\"}'",
})

test_case({
    "id": "TC-7.5", "title": "Cancel confirmed booking - full refund", "prio": "P0",
    "type": "Functional",
    "pre": "A CONFIRMED booking >= 24h before show start.",
    "steps": ["POST /bookings/{bookingId}/cancel."],
    "expected": [
        "200; booking status=REFUNDED (refund > 0).",
        "Seats -> AVAILABLE; booking_seat active=false (rows not deleted).",
        "Payment status=REFUNDED; seat becomes re-holdable.",
    ],
    "manual": "curl -i -X POST http://localhost:8080/bookings/1/cancel \\\n  -H \"Authorization: Bearer $TOKEN\"",
})

test_case({
    "id": "TC-7.6", "title": "Cancel - partial refund window", "prio": "P1",
    "type": "Functional",
    "pre": "CONFIRMED booking between 4h and 24h before show.",
    "steps": ["POST cancel."],
    "expected": [
        "200; refund = 50% (partialRefundPercent).",
        "Payment status=PARTIALLY_REFUNDED; booking status=REFUNDED.",
    ],
    "manual": "curl -i -X POST http://localhost:8080/bookings/{id}/cancel \\\n  -H \"Authorization: Bearer $TOKEN\"",
})

test_case({
    "id": "TC-7.7", "title": "Cancel - no-refund window", "prio": "P1",
    "type": "Functional",
    "pre": "CONFIRMED booking < 4h before show.",
    "steps": ["POST cancel."],
    "expected": [
        "200; refund = 0; booking status=CANCELLED (not REFUNDED).",
        "Payment stays SUCCESS; seats still released to AVAILABLE.",
    ],
    "manual": "curl -i -X POST http://localhost:8080/bookings/{id}/cancel \\\n  -H \"Authorization: Bearer $TOKEN\"",
})

test_case({
    "id": "TC-7.8", "title": "List my bookings / get one booking", "prio": "P2",
    "type": "Functional",
    "pre": "CUSTOMER token with at least one booking.",
    "steps": ["GET /bookings/me then GET /bookings/{id}."],
    "expected": ["200; only the caller's bookings are returned."],
    "manual": ["curl -s http://localhost:8080/bookings/me -H \"Authorization: Bearer $TOKEN\"",
               "curl -s http://localhost:8080/bookings/1 -H \"Authorization: Bearer $TOKEN\""],
})


# ===========================================================================
#  LEVEL 8 - BOOKING NEGATIVE / EDGE
# ===========================================================================
pdf.section_title = "Level 8 - Booking Edge Cases"
h1("12. Level 8 - Booking Negative & Edge Cases")

test_case({
    "id": "TC-8.1", "title": "Hold a seat that is already HELD/BOOKED", "prio": "P0",
    "type": "Negative",
    "pre": "A seat currently HELD by another booking.",
    "steps": ["POST holds for that show-seat id."],
    "expected": ["409 Conflict; code=SEAT_UNAVAILABLE; no state change."],
    "manual": "curl -i -X POST http://localhost:8080/shows/1/holds \\\n  -H \"Authorization: Bearer $TOKEN\" -H \"Content-Type: application/json\" \\\n  -d '{\"showSeatIds\":[10]}'   # 10 already held",
})

test_case({
    "id": "TC-8.2", "title": "Hold seat that belongs to a different show", "prio": "P1",
    "type": "Negative",
    "pre": "A valid show-seat id that is NOT part of {showId}.",
    "steps": ["POST /shows/{showId}/holds with a foreign show-seat id."],
    "expected": ["400 Bad Request; code=VALIDATION_ERROR (seat-show mismatch)."],
    "manual": "curl -i -X POST http://localhost:8080/shows/1/holds \\\n  -H \"Authorization: Bearer $TOKEN\" -H \"Content-Type: application/json\" \\\n  -d '{\"showSeatIds\":[99999]}'",
})

test_case({
    "id": "TC-8.3", "title": "Confirm after hold expired", "prio": "P0",
    "type": "Negative",
    "pre": "PENDING booking whose holdExpiresAt is in the past.",
    "steps": ["POST confirm on the expired booking."],
    "expected": [
        "409 Conflict; code=HOLD_EXPIRED.",
        "Booking set to EXPIRED and seats released as a side-effect.",
    ],
    "manual": ["Lower booking.hold.ttl-seconds (e.g. 2s), hold a seat, wait >2s, then:",
               "curl -i -X POST http://localhost:8080/bookings/{id}/confirm -H \"Authorization: Bearer $TOKEN\""],
})

test_case({
    "id": "TC-8.4", "title": "Confirm a non-PENDING booking", "prio": "P1",
    "type": "Negative",
    "pre": "An already CONFIRMED (or CANCELLED) booking.",
    "steps": ["POST confirm again."],
    "expected": ["409 Conflict; code=CONFLICT (illegal state transition)."],
    "manual": "curl -i -X POST http://localhost:8080/bookings/1/confirm \\\n  -H \"Authorization: Bearer $TOKEN\"",
})

test_case({
    "id": "TC-8.5", "title": "Cancel a non-CONFIRMED booking", "prio": "P1",
    "type": "Negative",
    "pre": "A PENDING or EXPIRED booking.",
    "steps": ["POST cancel."],
    "expected": ["409 Conflict; code=REFUND_NOT_ALLOWED."],
    "manual": "curl -i -X POST http://localhost:8080/bookings/{pendingId}/cancel \\\n  -H \"Authorization: Bearer $TOKEN\"",
})

test_case({
    "id": "TC-8.6", "title": "Access another user's booking", "prio": "P0",
    "type": "Security / Negative",
    "pre": "Booking owned by user A; call with user B's token.",
    "steps": ["GET /bookings/{A_bookingId} as user B (also try confirm/cancel)."],
    "expected": ["403 Forbidden; code=FORBIDDEN (ownership enforced in service)."],
    "manual": "curl -i http://localhost:8080/bookings/1 \\\n  -H \"Authorization: Bearer $OTHER_TOKEN\"",
})

test_case({
    "id": "TC-8.7", "title": "Confirm with invalid/expired discount code", "prio": "P2",
    "type": "Negative",
    "pre": "PENDING booking.",
    "steps": ["POST confirm with a non-existent or below-min discount code."],
    "expected": ["400 Bad Request; code=INVALID_DISCOUNT; booking stays PENDING."],
    "manual": "curl -i -X POST http://localhost:8080/bookings/1/confirm \\\n  -H \"Authorization: Bearer $TOKEN\" -H \"Content-Type: application/json\" \\\n  -d '{\"discountCode\":\"NOPE999\"}'",
})

test_case({
    "id": "TC-8.8", "title": "Hold on non-existent show", "prio": "P2",
    "type": "Negative",
    "pre": "CUSTOMER token.",
    "steps": ["POST /shows/999999/holds."],
    "expected": ["404 Not Found (or VALIDATION_ERROR) - never a 500."],
    "manual": "curl -i -X POST http://localhost:8080/shows/999999/holds \\\n  -H \"Authorization: Bearer $TOKEN\" -H \"Content-Type: application/json\" \\\n  -d '{\"showSeatIds\":[1]}'",
})


# ===========================================================================
#  LEVEL 9 - HOLD EXPIRY
# ===========================================================================
pdf.section_title = "Level 9 - Hold Expiry"
h1("13. Level 9 - Hold Expiry")
para("Holds must not leak seats. Expiry happens two ways: the background scheduler and the confirm-time check.")

test_case({
    "id": "TC-9.1", "title": "Scheduler expires an abandoned hold", "prio": "P0",
    "type": "Functional / Timing",
    "pre": "Short TTL for the test (e.g. ttl-seconds=1, sweep=300ms as in HoldExpiryTest).",
    "steps": [
        "Hold a seat and do nothing.",
        "Wait past TTL + one sweep interval.",
        "Re-inspect booking and seat.",
    ],
    "expected": [
        "Booking status -> EXPIRED.",
        "show_seat -> AVAILABLE; booking_seat active=false.",
        "Audit records HOLD_EXPIRED_SWEEP.",
    ],
    "manual": ["Automated: mvn -Dtest=HoldExpiryTest test",
               "Manual: set ttl-seconds low, hold via curl, wait, then GET /shows/{id}/seats and confirm the seat is AVAILABLE again."],
})

test_case({
    "id": "TC-9.2", "title": "Expired seat is immediately re-holdable", "prio": "P1",
    "type": "Functional",
    "pre": "A seat that just expired (TC-9.1).",
    "steps": ["POST a new hold on the same show-seat id from any customer."],
    "expected": ["201 Created; the new hold succeeds (partial unique index allows re-book)."],
    "manual": "curl -i -X POST http://localhost:8080/shows/1/holds \\\n  -H \"Authorization: Bearer $TOKEN\" -H \"Content-Type: application/json\" \\\n  -d '{\"showSeatIds\":[10]}'",
})


# ===========================================================================
#  LEVEL 10 - CONCURRENCY (advanced)
# ===========================================================================
pdf.section_title = "Level 10 - Concurrency"
h1("14. Level 10 - Concurrency (Advanced, Highest Value)")
para(
    "These prove the core invariant: NO SEAT IS EVER SOLD TWICE. They combine the "
    "pessimistic lock (SELECT ... FOR UPDATE in id order), the @Version optimistic "
    "checks, and the partial unique DB index as a final backstop."
)

test_case({
    "id": "TC-10.1", "title": "N buyers race for one seat - exactly one wins", "prio": "P0",
    "type": "Concurrency (crown jewel)",
    "pre": "One AVAILABLE seat; N=20 threads (SeatBookingConcurrencyTest).",
    "steps": [
        "Spawn 20 threads that each try hold+confirm on the same show-seat.",
        "Await all; count outcomes; inspect final DB state.",
    ],
    "expected": [
        "Exactly 1 thread ends CONFIRMED; the other 19 fail with SEAT_UNAVAILABLE.",
        "Final show_seat status=BOOKED.",
        "Exactly 1 CONFIRMED booking and 1 active booking_seat for that seat.",
        "No duplicate/double-sell; no deadlock; no 500s.",
    ],
    "manual": ["Automated (authoritative): mvn -Dtest=SeatBookingConcurrencyTest test",
               "Manual load approximation: fire many parallel holds and count 201 vs 409:",
               "for i in $(seq 1 20); do curl -s -o /dev/null -w \"%{http_code}\\n\" -X POST http://localhost:8080/shows/1/holds -H \"Authorization: Bearer $TOKEN\" -H \"Content-Type: application/json\" -d '{\"showSeatIds\":[10]}' & done; wait"],
})

test_case({
    "id": "TC-10.2", "title": "Concurrent holds on different seats all succeed", "prio": "P1",
    "type": "Concurrency",
    "pre": "Many AVAILABLE seats; each thread targets a distinct seat.",
    "steps": ["Spawn threads each holding a different show-seat id."],
    "expected": [
        "All holds succeed (no false contention - locks are per-row, in id order).",
        "No deadlock despite parallel FOR UPDATE.",
    ],
    "manual": "Fire parallel curls each with a different showSeatId; expect all 201.",
})

test_case({
    "id": "TC-10.3", "title": "DB unique index backstop prevents double active seat", "prio": "P0",
    "type": "Concurrency / DB",
    "pre": "Ability to force two active booking_seat rows for one show_seat.",
    "steps": [
        "Attempt (via a race or direct insert) to create a second active booking_seat for the same show_seat_id.",
    ],
    "expected": [
        "DataIntegrityViolation on uq_booking_seat_active -> mapped to 409 SEAT_UNAVAILABLE.",
        "Only one active row survives; invariant preserved even if app logic were bypassed.",
    ],
    "manual": ["Direct DB proof:",
               "psql moviebooking -c \"insert into booking_seat(booking_id,show_seat_id,active) values (1,10,true),(2,10,true);\"",
               "# second row must be rejected by the partial unique index"],
})

test_case({
    "id": "TC-10.4", "title": "Optimistic lock (@Version) rejects stale write", "prio": "P1",
    "type": "Concurrency",
    "pre": "Two transactions read the same ShowSeat/Booking version.",
    "steps": ["Both attempt to update; the second commit uses a stale version."],
    "expected": ["OptimisticLockingFailureException -> 409 SEAT_UNAVAILABLE; no lost update."],
    "manual": "Covered indirectly by TC-10.1; verified via GlobalExceptionHandler mapping.",
})


# ===========================================================================
#  LEVEL 11 - E2E & NON-FUNCTIONAL
# ===========================================================================
pdf.section_title = "Level 11 - End-to-End"
h1("15. Level 11 - End-to-End Journeys & Non-Functional")

test_case({
    "id": "TC-11.1", "title": "Full admin-to-customer journey", "prio": "P0",
    "type": "End-to-end",
    "pre": "Fresh app; admin and customer tokens.",
    "steps": [
        "ADMIN: create city -> theater -> screen -> seats -> movie -> pricing tier -> show + discount code.",
        "CUSTOMER: browse shows -> view seat map -> hold seats.",
        "CUSTOMER: preview applicable coupons (GET /bookings/{id}/discounts) and pick the best one.",
        "CUSTOMER: confirm with the chosen discount code -> verify payment.",
        "CUSTOMER: cancel -> verify refund and seat release.",
        "CUSTOMER: re-hold the released seat successfully.",
    ],
    "expected": [
        "Every step returns the documented status.",
        "Money math is consistent end to end (price -> discount -> payment -> refund).",
        "Seat status transitions AVAILABLE -> HELD -> BOOKED -> AVAILABLE correctly.",
    ],
    "manual": "Chain the curl snippets from Levels 4-8 in order; or drive it in Swagger UI. Also see BookingLifecycleTest for the automated version.",
})

test_case({
    "id": "TC-11.2", "title": "Notification fires only after commit", "prio": "P2",
    "type": "Non-functional / Async",
    "pre": "App running; confirm a booking.",
    "steps": ["Confirm a booking and watch application logs."],
    "expected": [
        "Notification log line appears AFTER the transaction commits (AFTER_COMMIT).",
        "It runs on an async thread (not the request thread); a rolled-back tx sends nothing.",
    ],
    "manual": "Confirm via curl (TC-7.3) and tail the app logs for the async notification entry.",
})

test_case({
    "id": "TC-11.3", "title": "Error responses have a consistent shape", "prio": "P1",
    "type": "Non-functional",
    "pre": "None.",
    "steps": ["Trigger several errors (401, 403, 404, 409, 400)."],
    "expected": [
        "Every error body has timestamp, status, code, message, path.",
        "Validation errors additionally include fieldErrors.",
        "No stack traces or internal details leak to the client.",
    ],
    "manual": "Compare bodies from TC-1.3, TC-2.1, TC-6.6, TC-8.1 - all share the ApiError schema.",
})

test_case({
    "id": "TC-11.4", "title": "Full regression suite is green", "prio": "P0",
    "type": "Non-functional / CI",
    "pre": "Zonky embedded PostgreSQL (no Docker needed).",
    "steps": ["Run the entire test suite."],
    "expected": [
        "mvn test passes: unit (pricing/discount/refund) + integration (lifecycle, expiry, RBAC) + concurrency race.",
    ],
    "manual": "mvn test",
})


# ===========================================================================
#  16. TRACEABILITY MATRIX
# ===========================================================================
pdf.section_title = "Traceability"
h1("16. Traceability Matrix")
para("Maps automated tests in the repository to the manual test cases above.")
data_table(
    ["Automated test", "Covers TC(s)"],
    [
        ["SeatBookingConcurrencyTest", "TC-10.1, TC-10.4"],
        ["BookingLifecycleTest", "TC-7.1, 7.3, 7.5, TC-11.1"],
        ["BookingDiscountPreviewTest", "TC-7.3a"],
        ["HoldExpiryTest", "TC-9.1, TC-9.2"],
        ["RbacAndValidationTest", "TC-1.3, TC-2.1, TC-2.2, TC-2.7, TC-4.1"],
        ["PricingServiceTest", "TC-5.2"],
        ["DiscountServiceTest", "TC-5.4, TC-7.3a"],
        ["RefundPolicyServiceTest", "TC-5.5"],
        ["(manual/exploratory)", "TC-0.x, TC-6.x, TC-8.x, TC-10.2/10.3, TC-11.2/11.3"],
    ],
    [40, 60],
)
h2("16.1 Coverage summary by level")
data_table(
    ["Level", "Theme", "# TCs"],
    [
        ["0", "Smoke & environment", "4"],
        ["1", "Authentication", "8"],
        ["2", "Authorisation / RBAC", "7"],
        ["3", "Input validation", "3 (+matrix)"],
        ["4", "Admin catalog", "5"],
        ["5", "Pricing / discount / refund", "5"],
        ["6", "Shows & browsing", "6"],
        ["7", "Booking lifecycle (happy)", "9"],
        ["8", "Booking negative/edge", "8"],
        ["9", "Hold expiry", "2"],
        ["10", "Concurrency (advanced)", "4"],
        ["11", "End-to-end & non-functional", "4"],
    ],
    [14, 66, 20],
)
pdf.ln(3)
para(
    "End of document. To keep this catalogue current, regenerate the PDF after "
    "changing endpoints or business rules: python docs/generate_test_cases_pdf.py",
    size=9,
)


# ---------------------------------------------------------------------------
import sys
OUT = sys.argv[1] if len(sys.argv) > 1 else "docs/Movie-Booking-Test-Cases.pdf"
pdf.output(OUT)
print("Wrote", OUT)
