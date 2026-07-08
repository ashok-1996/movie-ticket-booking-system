"""
Generates a landscape presentation deck (PDF) for a ~10 minute video
walkthrough of the Movie Ticket Booking System.

Pages:
  1. Functional Requirements
  2. High-Level Design (HLD)        - Excalidraw-style hand-drawn sketch
  3. Concurrency: Approach & Trade-offs
  4. ER Diagram                     - SmartDraw-style entity tables + crow's foot
  5. Tech Stack & Reasoning
  6. Testing Approach
  7. AI Workflow

Run:    python docs/generate_presentation_pdf.py [output.pdf]
Output: docs/Movie-Booking-Presentation.pdf
"""

import sys
import math
import random
from fpdf import FPDF

# --------------------------------------------------------------------------- #
_REPL = {
    "\u2192": "->", "\u2190": "<-", "\u2194": "<->", "\u21b3": "->",
    "\u2265": ">=", "\u2264": "<=", "\u00d7": "x", "\u2013": "-", "\u2014": "-",
    "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"', "\u20b9": "Rs.",
    "\u2022": "-", "\u2026": "...", "\u00a0": " ", "\u2705": "", "\u274c": "",
}


def s(t):
    if t is None:
        return ""
    t = str(t)
    for k, v in _REPL.items():
        t = t.replace(k, v)
    return t.encode("latin-1", "replace").decode("latin-1")


# --------------------------------------------------------------------------- #
NAVY = (23, 42, 69)
BLUE = (37, 99, 175)
SKY = (86, 156, 214)
LIGHT = (236, 242, 249)
CARD = (247, 250, 253)
GREEN = (33, 120, 70)
AMBER = (200, 130, 20)
RED = (176, 58, 46)
GREY = (110, 118, 130)
BORDER = (200, 210, 222)
DARK = (33, 37, 43)
WHITE = (255, 255, 255)

# Excalidraw-ish pastels + near-black ink
INK = (28, 28, 33)
EX_BLUE = (165, 216, 255)
EX_GREEN = (178, 242, 187)
EX_YELLOW = (255, 236, 153)
EX_RED = (255, 201, 201)
EX_VIOLET = (208, 191, 255)

PAGE_W, PAGE_H = 297, 210
MARGIN = 14
CW = PAGE_W - 2 * MARGIN
TOTAL = 7


class Deck(FPDF):
    def __init__(self):
        super().__init__(orientation="L", unit="mm", format="A4")
        self.set_auto_page_break(False)
        self.set_margins(MARGIN, MARGIN, MARGIN)
        self.idx = 0

    def footer(self):
        if self.idx == 0:
            return
        self.set_y(-11)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*GREY)
        self.cell(0, 5, s("Movie Ticket Booking System"), 0, 0, "L")
        self.cell(0, 5, s("Page %d of %d" % (self.idx, TOTAL)), 0, 0, "R")


pdf = Deck()

# hand-drawn font (Comic Sans MS on Windows) for the Excalidraw-style slide
HAND = "Helvetica"
for reg, bold, fam in [(r"C:\Windows\Fonts\comic.ttf", r"C:\Windows\Fonts\comicbd.ttf", "Hand")]:
    try:
        pdf.add_font(fam, "", reg)
        pdf.add_font(fam, "B", bold)
        HAND = fam
    except Exception:
        HAND = "Helvetica"


def new_page(title, subtitle):
    pdf.add_page()
    pdf.idx += 1
    number = pdf.idx
    pdf.set_xy(MARGIN, 8)
    pdf.set_font("Helvetica", "B", 8.5)
    pdf.set_text_color(*SKY)
    pdf.cell(0, 4, s("MOVIE TICKET BOOKING SYSTEM  -  ARCHITECTURE DECK"), 0, 0, "L")
    pdf.cell(0, 4, s("%d / %d" % (number, TOTAL)), 0, 0, "R")
    pdf.set_fill_color(*NAVY)
    pdf.rect(MARGIN, 14, CW, 16, "F")
    pdf.set_xy(MARGIN + 4, 14)
    pdf.set_font("Helvetica", "B", 17)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 16, s("%d.  %s" % (number, title)), 0, 0, "L")
    pdf.set_fill_color(*SKY)
    pdf.rect(MARGIN, 30, CW, 1.4, "F")
    if subtitle:
        pdf.set_xy(MARGIN, 33)
        pdf.set_font("Helvetica", "I", 10)
        pdf.set_text_color(*GREY)
        pdf.cell(0, 5, s(subtitle), 0, 0, "L")
    pdf.set_text_color(*DARK)


def box(x, y, w, h, lines, fill=WHITE, fg=DARK, border=BORDER, lw=0.4):
    pdf.set_fill_color(*fill)
    pdf.set_draw_color(*border)
    pdf.set_line_width(lw)
    pdf.rect(x, y, w, h, "DF")
    heights = []
    for (t, sz, b) in lines:
        lh = sz * 0.44 + 0.6
        pdf.set_font("Helvetica", "B" if b else "", sz)
        cnt = max(1, len(pdf.multi_cell(w - 2, lh, s(t), dry_run=True, output="LINES")))
        heights.append(lh * cnt)
    total = sum(heights)
    cy = y + (h - total) / 2.0
    for (t, sz, b), hh in zip(lines, heights):
        pdf.set_font("Helvetica", "B" if b else "", sz)
        pdf.set_text_color(*fg)
        pdf.set_xy(x + 1, cy)
        lh = sz * 0.44 + 0.6
        pdf.multi_cell(w - 2, lh, s(t), 0, "C")
        cy += hh
    pdf.set_text_color(*DARK)


def arrow(x1, y1, x2, y2, color=BLUE, lw=0.6):
    pdf.set_draw_color(*color)
    pdf.set_line_width(lw)
    pdf.line(x1, y1, x2, y2)
    ang = math.atan2(y2 - y1, x2 - x1)
    size = 2.6
    for da in (math.radians(155), math.radians(-155)):
        pdf.line(x2, y2, x2 + size * math.cos(ang + da), y2 + size * math.sin(ang + da))


def bullet(x, y, w, text, size=11, gap=6.2, color=DARK, dot=BLUE):
    pdf.set_fill_color(*dot)
    pdf.ellipse(x, y + 1.6, 1.8, 1.8, "F")
    pdf.set_font("Helvetica", "", size)
    pdf.set_text_color(*color)
    pdf.set_xy(x + 4, y)
    pdf.multi_cell(w - 4, gap - 1.2, s(text), 0, "L")
    end_y = pdf.get_y()
    pdf.set_text_color(*DARK)
    return max(y + gap, end_y + 1.5)


# ----- Excalidraw-style sketch primitives ---------------------------------- #
def _jline(x1, y1, x2, y2, jitter=0.45, segs=3):
    pts = [(x1, y1)]
    for i in range(1, segs):
        t = i / segs
        mx = x1 + (x2 - x1) * t + random.uniform(-jitter, jitter)
        my = y1 + (y2 - y1) * t + random.uniform(-jitter, jitter)
        pts.append((mx, my))
    pts.append((x2, y2))
    for a, b in zip(pts, pts[1:]):
        pdf.line(a[0], a[1], b[0], b[1])


def sketch_rect(x, y, w, h, fill=None, stroke=INK, lw=0.55, o=1.3):
    if fill:
        pdf.set_fill_color(*fill)
        pdf.set_draw_color(*fill)
        pdf.rect(x, y, w, h, "F")
    pdf.set_draw_color(*stroke)
    pdf.set_line_width(lw)
    for _ in range(2):  # doubled strokes = hand-drawn look
        _jline(x - o, y, x + w + o, y)
        _jline(x + w, y - o * 0.5, x + w, y + h + o * 0.5)
        _jline(x + w + o, y + h, x - o, y + h)
        _jline(x, y + h + o * 0.5, x, y - o * 0.5)


def sketch_box(x, y, w, h, lines, fill=WHITE):
    sketch_rect(x, y, w, h, fill=fill)
    heights = []
    for (t, sz, b) in lines:
        lh = sz * 0.46 + 0.8
        pdf.set_font(HAND, "B" if b else "", sz)
        cnt = max(1, len(pdf.multi_cell(w - 3, lh, s(t), dry_run=True, output="LINES")))
        heights.append(lh * cnt)
    total = sum(heights)
    cy = y + (h - total) / 2.0
    for (t, sz, b), hh in zip(lines, heights):
        pdf.set_font(HAND, "B" if b else "", sz)
        pdf.set_text_color(*INK)
        lh = sz * 0.46 + 0.8
        pdf.set_xy(x + 1.5, cy)
        pdf.multi_cell(w - 3, lh, s(t), 0, "C")
        cy += hh
    pdf.set_text_color(*DARK)


def sketch_arrow(x1, y1, x2, y2, stroke=INK, lw=0.6):
    pdf.set_draw_color(*stroke)
    pdf.set_line_width(lw)
    _jline(x1, y1, x2, y2, jitter=0.4)
    ang = math.atan2(y2 - y1, x2 - x1)
    for da in (math.radians(150), math.radians(-150)):
        pdf.line(x2, y2, x2 + 3.0 * math.cos(ang + da), y2 + 3.0 * math.sin(ang + da))


# =========================================================================== #
# COVER
# =========================================================================== #
pdf.add_page()
pdf.idx = 0
pdf.set_fill_color(*NAVY)
pdf.rect(0, 0, PAGE_W, PAGE_H, "F")
pdf.set_fill_color(*BLUE)
pdf.rect(0, 86, PAGE_W, 3, "F")
pdf.set_xy(0, 52)
pdf.set_font("Helvetica", "B", 34)
pdf.set_text_color(*WHITE)
pdf.cell(PAGE_W, 16, s("Movie Ticket Booking System"), 0, 1, "C")
pdf.set_font("Helvetica", "B", 17)
pdf.set_text_color(*SKY)
pdf.cell(PAGE_W, 12, s("Design & Architecture Walkthrough"), 0, 1, "C")
pdf.ln(10)
pdf.set_font("Helvetica", "", 12)
pdf.set_text_color(220, 228, 240)
pdf.cell(PAGE_W, 7, s("A concurrency-safe seat-booking backend  -  no seat is ever sold twice"), 0, 1, "C")
pdf.ln(6)
pdf.set_font("Helvetica", "", 10.5)
pdf.set_text_color(180, 195, 215)
pdf.cell(PAGE_W, 6, s("Requirements | HLD | Concurrency | ER Diagram | Tech Stack | Testing | AI Workflow"), 0, 1, "C")
pdf.cell(PAGE_W, 6, s("Java 21  -  Spring Boot 3.3  -  PostgreSQL + Flyway  -  JWT"), 0, 1, "C")


# =========================================================================== #
# PAGE 1 - FUNCTIONAL REQUIREMENTS
# =========================================================================== #
new_page("Functional Requirements", "What the system must do - in plain terms")

col_w = (CW - 8) / 2
lx, rx = MARGIN, MARGIN + col_w + 8
top = 42


def group(x, y, w, heading, items, hcolor=BLUE):
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(*hcolor)
    pdf.set_xy(x, y)
    pdf.cell(w, 6, s(heading), 0, 0, "L")
    yy = y + 8
    for it in items:
        yy = bullet(x + 1, yy, w - 1, it, size=10.5, gap=6.0)
    return yy + 3


y = group(lx, top, col_w, "Core booking journey", [
    "Browse shows by city, movie and date.",
    "View the live seat map with prices.",
    "Hold selected seats for a short window.",
    "Confirm & pay to lock the booking.",
    "Cancel a booking and get a refund.",
])
y = group(lx, y + 1, col_w, "Pricing & money", [
    "Tiered seat pricing (Regular / Premium / Recliner).",
    "One booking = one pricing tier (no mixing).",
    "Preview & apply discount coupons before paying.",
    "Policy-based refunds on cancellation.",
])

y2 = group(rx, top, col_w, "Correctness & scale", [
    "No seat is ever sold twice (prime invariant).",
    "Safe under thousands of concurrent requests.",
    "Unpaid holds expire automatically.",
    "Every state change is auditable.",
])
y2 = group(rx, y2 + 1, col_w, "Roles & access", [
    "ADMIN: manage catalog, shows, pricing, discounts.",
    "CUSTOMER: browse, book, cancel own bookings.",
    "Stateless JWT authentication.",
])

by = max(max(y, y2) + 2, 176)
pdf.set_fill_color(*LIGHT)
pdf.set_draw_color(*BLUE)
pdf.set_line_width(0.5)
pdf.rect(MARGIN, by, CW, 14, "DF")
pdf.set_xy(MARGIN + 4, by)
pdf.set_font("Helvetica", "B", 12)
pdf.set_text_color(*NAVY)
pdf.cell(0, 14, s("Prime invariant:  NO SEAT IS EVER SOLD TWICE  -  correctness is prioritized over feature count."), 0, 0, "L")
pdf.set_text_color(*DARK)


# =========================================================================== #
# PAGE 2 - HLD  (Excalidraw style)
# =========================================================================== #
new_page("High-Level Design", "Request flow: thin controllers -> services -> repositories -> PostgreSQL")
random.seed(7)

x_client, w_client = MARGIN, 40
x_api, w_api = 66, 46
x_svc, w_svc = 124, 58
x_repo, w_repo = 194, 40
x_db, w_db = 246, 37
py, bh = 52, 26

sketch_box(x_client, py, w_client, bh, [("Client", 13, True), ("web / mobile", 9, False)], fill=WHITE)
sketch_box(x_api, py, w_api, bh, [("API Layer", 13, True), ("Controllers", 9, False), ("+ JWT filter", 9, False)], fill=EX_BLUE)
sketch_box(x_svc, py, w_svc, bh, [("Service Layer", 13, True), ("Booking / Pricing / Discount", 8.5, False), ("Refund / Auth  (@Transactional)", 8.5, False)], fill=EX_BLUE)
sketch_box(x_repo, py, w_repo, bh, [("Repositories", 12, True), ("Spring Data JPA", 8.5, False)], fill=EX_GREEN)
sketch_box(x_db, py, w_db, bh, [("PostgreSQL", 13, True), ("+ Flyway", 9, False)], fill=EX_YELLOW)

mid = py + bh / 2
sketch_arrow(x_client + w_client + 1, mid, x_api - 1, mid)
sketch_arrow(x_api + w_api + 1, mid, x_svc - 1, mid)
sketch_arrow(x_svc + w_svc + 1, mid, x_repo - 1, mid)
sketch_arrow(x_repo + w_repo + 1, mid, x_db - 1, mid)

pdf.set_font(HAND, "B", 12)
pdf.set_text_color(*GREEN)
pdf.set_xy(x_svc, py - 9)
pdf.cell(w_svc, 5, s("hold -> confirm -> cancel"), 0, 0, "C")
pdf.set_text_color(*DARK)

# concurrency callout under DB
cy = py + bh + 12
sketch_box(x_db - 22, cy, w_db + 22, 36,
           [("Concurrency safeguards", 10, True),
            ("1) SELECT ... FOR UPDATE", 8.5, False),
            ("(locked in seat-id order)", 7.8, False),
            ("2) @Version optimistic lock", 8.5, False),
            ("3) partial UNIQUE index", 8.5, False),
            ("(DB backstop)", 7.8, False)],
           fill=EX_RED)
sketch_arrow(x_db + w_db / 2, py + bh + 1, x_db + w_db / 2, cy - 1)

# cross-cutting sketch boxes
ccy = 150
pdf.set_font(HAND, "B", 11)
pdf.set_text_color(*GREY)
pdf.set_xy(MARGIN, ccy - 8)
pdf.cell(0, 5, s("cross-cutting concerns"), 0, 0, "L")
cc_w = 58
gap = (CW - 3 * cc_w) / 2
labels = [
    ("Global Exception Handler", "uniform ApiError + ErrorCode"),
    ("Hold Expiry Scheduler", "sweeps expired holds"),
    ("Async Notifications", "AFTER_COMMIT + @Async"),
]
for i, (t, sub) in enumerate(labels):
    sketch_box(MARGIN + i * (cc_w + gap), ccy, cc_w, 20,
               [(t, 10, True), (sub, 8, False)], fill=EX_VIOLET)

pdf.set_font("Helvetica", "I", 8.5)
pdf.set_text_color(*GREY)
pdf.set_xy(MARGIN, 176)
pdf.multi_cell(CW, 4.6, s("Controllers are thin; business logic and transaction boundaries live in the service layer. "
                          "Seat contention is per-row, so unrelated seats/shows proceed fully in parallel."), 0, "L")
pdf.set_text_color(*DARK)


# =========================================================================== #
# PAGE 3 - CONCURRENCY: APPROACH & TRADE-OFFS
# =========================================================================== #
new_page("Concurrency: Approach & Trade-offs", "Goal: no double-sell, with low latency and simple engineering")

gx = MARGIN
cols = [46, 84, 78, 61]  # Approach | Latency | Engineering | Fit
hx = [gx, gx + cols[0], gx + cols[0] + cols[1], gx + cols[0] + cols[1] + cols[2]]
hy = 42
hh = 8
headers = ["Approach", "Latency impact", "Engineering effort", "Fit for our goal"]
pdf.set_font("Helvetica", "B", 9.5)
pdf.set_fill_color(*NAVY)
pdf.set_text_color(*WHITE)
for x, w, t in zip(hx, cols, headers):
    pdf.set_xy(x, hy)
    pdf.cell(w, hh, s(t), 1, 0, "C", fill=True)
pdf.set_text_color(*DARK)

rows = [
    ("PostgreSQL row locks\n(SELECT FOR UPDATE)",
     "Lowest - synchronous ms answer; blocks only on the same seat row.",
     "Simplest - native ACID; no extra infra to run or monitor.",
     "BEST FIT", GREEN),
    ("Synchronous queue",
     "High - all bookings serialize through one worker.",
     "In-memory queue breaks across multiple app nodes.",
     "Anti-pattern", RED),
    ("Async queue",
     "Fast 202, but slow real answer (eventual consistency).",
     "Broker + consumers + idempotency + result delivery.",
     "Bursts only", AMBER),
    ("Event-specific queues",
     "Better globally, but a hot show still serializes.",
     "Dynamic per-event queues, routing, autoscaling.",
     "Reinvents DB", AMBER),
    ("Non-overlapping queues\n(shard by seat)",
     "Great parallelism once built correctly.",
     "Sharding + cross-shard atomicity + rebalancing.",
     "Too complex", RED),
]
ry = hy + hh
rh = 18
pdf.set_font("Helvetica", "", 8.3)
for i, (appr, lat, eng, fit, fitcol) in enumerate(rows):
    base = CARD if i % 2 == 0 else WHITE
    for x, w in zip(hx, cols):
        pdf.set_fill_color(*base)
        pdf.set_draw_color(*BORDER)
        pdf.rect(x, ry, w, rh, "DF")
    # approach (bold)
    pdf.set_font("Helvetica", "B", 8.6)
    pdf.set_text_color(*NAVY)
    pdf.set_xy(hx[0] + 1.5, ry + 2)
    pdf.multi_cell(cols[0] - 3, 3.9, s(appr), 0, "L")
    # latency + engineering
    pdf.set_font("Helvetica", "", 8.2)
    pdf.set_text_color(*DARK)
    pdf.set_xy(hx[1] + 1.5, ry + 2.5)
    pdf.multi_cell(cols[1] - 3, 4.0, s("- " + lat), 0, "L")
    pdf.set_xy(hx[2] + 1.5, ry + 2.5)
    pdf.multi_cell(cols[2] - 3, 4.0, s("- " + eng), 0, "L")
    # fit chip
    pdf.set_fill_color(*fitcol)
    pdf.rect(hx[3] + 6, ry + rh / 2 - 4, cols[3] - 12, 8, "F")
    pdf.set_font("Helvetica", "B", 8.6)
    pdf.set_text_color(*WHITE)
    pdf.set_xy(hx[3] + 6, ry + rh / 2 - 4)
    pdf.cell(cols[3] - 12, 8, s(fit), 0, 0, "C")
    pdf.set_text_color(*DARK)
    ry += rh

# verdict banner
vy = ry + 4
pdf.set_fill_color(*NAVY)
pdf.rect(MARGIN, vy, CW, 24, "F")
pdf.set_xy(MARGIN + 4, vy + 2.5)
pdf.set_font("Helvetica", "B", 11.5)
pdf.set_text_color(*WHITE)
pdf.cell(0, 6, s("Verdict:  PostgreSQL row-level locking wins."), 0, 1, "L")
pdf.set_xy(MARGIN + 4, vy + 9.5)
pdf.set_font("Helvetica", "", 9.3)
pdf.set_text_color(220, 228, 240)
pdf.multi_cell(CW - 8, 4.6, s("The 'seat taken' decision must be serialized at one point per seat anyway - Postgres does exactly that, "
                              "synchronously, with an immediate answer and zero extra infrastructure. Queues sit IN FRONT OF the DB, "
                              "not instead of it: keep them for async side-effects (notifications), never for seat arbitration."), 0, "L")
pdf.set_text_color(*DARK)


# =========================================================================== #
# PAGE 4 - ER DIAGRAM  (SmartDraw style: entity tables + crow's foot)
# =========================================================================== #
new_page("ER Diagram", "SmartDraw-style physical model: PK / FK attributes with crow's-foot cardinality")


def er_table(x, y, w, name, pk_rows, rows, head=BLUE, headfg=WHITE):
    rowh, headh = 4.5, 6.2
    h = headh + (len(pk_rows) + len(rows)) * rowh + 1.2
    pdf.set_fill_color(255, 255, 255)
    pdf.set_draw_color(*NAVY)
    pdf.set_line_width(0.3)
    pdf.rect(x, y, w, h, "DF")
    pdf.set_fill_color(*head)
    pdf.rect(x, y, w, headh, "F")
    pdf.set_font("Helvetica", "B", 7.6)
    pdf.set_text_color(*headfg)
    pdf.set_xy(x, y)
    pdf.cell(w, headh, s(name), 0, 0, "C")
    yy = y + headh
    pdf.set_font("Helvetica", "", 6.5)
    pdf.set_text_color(*DARK)
    for r in pk_rows:
        pdf.set_fill_color(235, 242, 250)
        pdf.rect(x, yy, w, rowh, "F")
        pdf.set_xy(x + 1.4, yy)
        pdf.cell(w - 2, rowh, s(r), 0, 0, "L")
        yy += rowh
    if pk_rows:
        pdf.set_draw_color(*BORDER)
        pdf.line(x, yy, x + w, yy)
    for r in rows:
        pdf.set_xy(x + 1.4, yy)
        pdf.cell(w - 2, rowh, s(r), 0, 0, "L")
        yy += rowh
    pdf.set_draw_color(*NAVY)
    pdf.rect(x, y, w, h, "D")
    return (x, y, w, h)


def edge(b, side):
    x, y, w, h = b
    return {
        "R": (x + w, y + h / 2), "L": (x, y + h / 2),
        "T": (x + w / 2, y), "B": (x + w / 2, y + h),
    }[side]


def _one_tick(ex, ey, ox, oy, size=2.0):
    dx, dy = ex - ox, ey - oy
    L = math.hypot(dx, dy) or 1
    ux, uy = dx / L, dy / L
    bx, by = ex - ux * 2.6, ey - uy * 2.6
    px, py = -uy, ux
    pdf.line(bx + px * size, by + py * size, bx - px * size, by - py * size)


def _crowsfoot(ex, ey, ox, oy, size=3.4, spread=2.2):
    dx, dy = ex - ox, ey - oy
    L = math.hypot(dx, dy) or 1
    ux, uy = dx / L, dy / L
    px, py = ex - ux * size, ey - uy * size
    perpx, perpy = -uy, ux
    pdf.line(px, py, ex + perpx * spread, ey + perpy * spread)
    pdf.line(px, py, ex - perpx * spread, ey - perpy * spread)
    pdf.line(px, py, ex, ey)


def rel(b_one, side_one, b_many, side_many):
    p1 = edge(b_one, side_one)
    p2 = edge(b_many, side_many)
    pdf.set_draw_color(*GREY)
    pdf.set_line_width(0.4)
    pdf.line(p1[0], p1[1], p2[0], p2[1])
    _one_tick(p1[0], p1[1], p2[0], p2[1])
    _crowsfoot(p2[0], p2[1], p1[0], p1[1])


AMB = (170, 110, 20)
VIO = (120, 90, 170)
GRN = (40, 120, 80)

# column 1 - catalog chain (vertical)
c1x, c1w = MARGIN, 52
city = er_table(c1x, 40, c1w, "City", ["PK id"], ["name (U)", "state"])
theater = er_table(c1x, 66, c1w, "Theater", ["PK id"], ["FK city_id", "name"])
screen = er_table(c1x, 92, c1w, "Screen", ["PK id"], ["FK theater_id", "name"])
seat = er_table(c1x, 118, c1w, "Seat", ["PK id"], ["FK screen_id", "row, number", "seat_class"])
rel(city, "B", theater, "T")
rel(theater, "B", screen, "T")
rel(screen, "B", seat, "T")

# column 2 - movie / show / showseat
c2x, c2w = 74, 62
movie = er_table(c2x, 40, c2w, "Movie", ["PK id"], ["title", "duration_min"])
show = er_table(c2x, 66, c2w, "Show (show_event)", ["PK id"], ["FK movie_id", "FK screen_id", "start_time", "base_price"])
showseat = er_table(c2x, 101, c2w, "ShowSeat", ["PK id"], ["FK show_id", "FK seat_id", "status, price", "@version",
                                                           "U(show_id, seat_id)"], head=AMB)
rel(movie, "B", show, "T")
rel(screen, "R", show, "L")
rel(seat, "R", showseat, "L")
rel(show, "B", showseat, "T")

# column 3 - user / booking / bookingseat
c3x, c3w = 148, 60
user = er_table(c3x, 40, c3w, "User (app_user)", ["PK id"], ["email (U)", "role"])
booking = er_table(c3x, 66, c3w, "Booking", ["PK id"], ["FK user_id", "FK show_id", "status", "final_amount", "@version"])
bseat = er_table(c3x, 106, c3w, "BookingSeat", ["PK id"], ["FK booking_id", "FK show_seat_id", "active",
                                                           "U(show_seat_id)", "  WHERE active"], head=AMB)
rel(user, "B", booking, "T")
rel(booking, "B", bseat, "T")
rel(showseat, "R", bseat, "L")

# column 4 - payment
c4x, c4w = 216, 62
payment = er_table(c4x, 72, c4w, "Payment", ["PK id"], ["FK booking_id (U)", "amount", "status", "method"], head=GRN)
rel(booking, "R", payment, "L")

# bottom strip - configuration & audit (standalone)
sy = 150
pdf.set_font("Helvetica", "B", 8)
pdf.set_text_color(*GREY)
pdf.set_xy(MARGIN, sy - 6)
pdf.cell(0, 4, s("Configuration & audit  (reference data - no FK into the booking flow)"), 0, 0, "L")
er_table(MARGIN, sy, 60, "PricingTier", ["PK id"], ["seat_class (U)", "multiplier"], head=VIO)
er_table(MARGIN + 68, sy, 60, "DiscountCode", ["PK id"], ["code (U)", "type, value"], head=VIO)
er_table(MARGIN + 136, sy, 60, "RefundPolicy", ["PK id"], ["hours_before", "percent"], head=VIO)
er_table(MARGIN + 204, sy, 65, "AuditEvent", ["PK id"], ["entity, action", "append-only"], head=(90, 100, 115))

# legend
pdf.set_font("Helvetica", "I", 7)
pdf.set_text_color(*GREY)
pdf.set_xy(MARGIN + 204, sy + 22)
pdf.multi_cell(65, 3.6, s("PK=primary key  FK=foreign key\n(U)=unique   ->|< = crow's foot 'many'"), 0, "L")
pdf.set_text_color(*DARK)


# =========================================================================== #
# PAGE 5 - TECH STACK
# =========================================================================== #
new_page("Tech Stack & Reasoning", "Every choice serves: correctness, low latency, simple engineering")

stack = [
    ("Java 21 + Spring Boot 3.3", "Mature ecosystem; declarative @Transactional, DI, and security out of the box."),
    ("PostgreSQL", "ACID + row-level locking + partial indexes = the concurrency backbone. No double-sell."),
    ("Flyway migrations", "Versioned, authoritative schema; app runs ddl-auto=validate (never auto-mutates DB)."),
    ("JWT auth (ADMIN / CUSTOMER)", "Stateless tokens -> horizontal scaling, no server session store."),
    ("Spring Data JPA + Hibernate", "Repositories + @Version; pessimistic lock via a simple derived query."),
    ("Zonky embedded PostgreSQL", "Real Postgres in tests (true locking) without a Docker daemon."),
    ("Bean Validation + DTOs", "Reject bad input at the edge; entities never leak out of controllers."),
    ("Maven + JUnit 5 / Mockito", "Standard build; fast unit tests plus full integration + concurrency suite."),
]
cardw = (CW - 8) / 2
cardh = 30
x0 = [MARGIN, MARGIN + cardw + 8]
sy = 44
for i, (name, why) in enumerate(stack):
    x = x0[i % 2]
    yy = sy + (i // 2) * (cardh + 4)
    pdf.set_fill_color(*CARD)
    pdf.set_draw_color(*BORDER)
    pdf.set_line_width(0.4)
    pdf.rect(x, yy, cardw, cardh, "DF")
    pdf.set_fill_color(*BLUE)
    pdf.rect(x, yy, 2.2, cardh, "F")
    pdf.set_xy(x + 6, yy + 3.5)
    pdf.set_font("Helvetica", "B", 11.5)
    pdf.set_text_color(*NAVY)
    pdf.multi_cell(cardw - 9, 5.4, s(name), 0, "L")
    pdf.set_xy(x + 6, yy + 12)
    pdf.set_font("Helvetica", "", 9.3)
    pdf.set_text_color(*DARK)
    pdf.multi_cell(cardw - 9, 4.7, s(why), 0, "L")


# =========================================================================== #
# PAGE 6 - TESTING APPROACH
# =========================================================================== #
new_page("Testing Approach", "Correctness is demonstrated by execution, not asserted")

apex_x = MARGIN + 62
base_half = 58
top_y = 46
bot_y = 150
h_total = bot_y - top_y


def band(y1, y2, half1, half2, color, label):
    cx = apex_x
    pts = [(cx - half1, y1), (cx + half1, y1), (cx + half2, y2), (cx - half2, y2)]
    pdf.set_fill_color(*color)
    pdf.set_draw_color(*WHITE)
    pdf.set_line_width(0.8)
    pdf.polygon(pts, style="DF")
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*WHITE)
    pdf.set_xy(cx - half2, (y1 + y2) / 2 - 3)
    pdf.cell(2 * half2, 6, s(label), 0, 0, "C")
    pdf.set_text_color(*DARK)


band(top_y, top_y + h_total * 0.28, 6, 22, RED, "Concurrency / E2E")
band(top_y + h_total * 0.28, top_y + h_total * 0.60, 22, 40, AMBER, "Integration")
band(top_y + h_total * 0.60, bot_y, 40, base_half, GREEN, "Unit")
pdf.set_font("Helvetica", "I", 8.5)
pdf.set_text_color(*GREY)
pdf.set_xy(MARGIN, bot_y + 3)
pdf.cell(base_half * 2 + 8, 5, s("Fewer, high-value tests at the top"), 0, 0, "C")
pdf.set_text_color(*DARK)

tx = MARGIN + 128
tw = CW - 128


def tier(y, color, title, items):
    pdf.set_fill_color(*color)
    pdf.rect(tx, y, 4, 4, "F")
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(*color)
    pdf.set_xy(tx + 7, y - 1.5)
    pdf.cell(tw - 7, 6, s(title), 0, 0, "L")
    yy = y + 7
    for it in items:
        yy = bullet(tx + 2, yy, tw - 2, it, size=9.5, gap=5.6)
    return yy + 3


yy = tier(48, RED, "Concurrency race (flagship)", [
    "SeatBookingConcurrencyTest: 20 threads, 1 seat.",
    "Asserts exactly ONE winner, seat ends BOOKED.",
    "Proves the no-double-sell invariant under load.",
])
yy = tier(yy, AMBER, "Integration (@IntegrationTest + Zonky)", [
    "Real embedded PostgreSQL - true locking semantics.",
    "Lifecycle, hold-expiry, RBAC, discount preview, single-tier rule.",
])
yy = tier(yy, GREEN, "Unit (Mockito, no Spring)", [
    "Pricing, discount, and refund pure logic.",
    "Fast feedback on business rules.",
])
pdf.set_fill_color(*LIGHT)
pdf.set_draw_color(*BLUE)
pdf.rect(tx, 158, tw, 20, "DF")
pdf.set_xy(tx + 3, 160)
pdf.set_font("Helvetica", "B", 10)
pdf.set_text_color(*NAVY)
pdf.cell(0, 5, s("One command:  mvn test"), 0, 1, "L")
pdf.set_font("Helvetica", "", 8.8)
pdf.set_text_color(*DARK)
pdf.set_xy(tx + 3, 166)
pdf.multi_cell(tw - 6, 4.5, s("Runs the whole pyramid, including the 20-thread race against a real Postgres. "
                              "Test IDs are traced in the master test-case document."), 0, "L")


# =========================================================================== #
# PAGE 7 - AI WORKFLOW
# =========================================================================== #
new_page("AI Workflow", "How an AI agent (Cursor) was used - with humans in the loop")

phases = ["Frame &\nscope", "Plan\nfirst", "Layered\nbuild", "Compile &\ntest", "Self-\nverify", "Document"]
pw = (CW - 5 * 6) / 6
fy = 44
for i, p in enumerate(phases):
    x = MARGIN + i * (pw + 6)
    parts = p.split("\n")
    box(x, fy, pw, 18, [(parts[0], 9.5, True), (parts[1] if len(parts) > 1 else "", 9.5, True)],
        fill=(223, 234, 247), border=BLUE)
    if i < 5:
        arrow(x + pw, fy + 9, x + pw + 6, fy + 9)

col_w2 = (CW - 8) / 2
lx, rx = MARGIN, MARGIN + col_w2 + 8


def group2(x, y, heading, items, hc=BLUE):
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(*hc)
    pdf.set_xy(x, y)
    pdf.cell(col_w2, 6, s(heading), 0, 0, "L")
    yy = y + 8
    for it in items:
        yy = bullet(x + 1, yy, col_w2 - 1, it, size=10, gap=6.0)
    return yy + 2


y = group2(lx, 70, "How the agent was directed", [
    "A single detailed build-prompt fixed the stack, domain, API and concurrency defense.",
    "AGENTS.md = durable guardrails the agent must respect on every change.",
    "Concurrency rules explicitly 'do not weaken'.",
    "Tight, testable acceptance criteria kept it honest.",
])
y = group2(lx, y + 1, "Verification loop", [
    "Explore -> propose -> edit -> compile -> run tests.",
    "Self-check artifacts (rendered PDFs, test output).",
    "Fixed real issues (Zonky provider, SQL null-type).",
])

y2 = group2(rx, 70, "Produced by AI", [
    "Entities, Flyway migrations, services, controllers.",
    "Security, DTOs, exception handling.",
    "Unit + integration + concurrency tests, and docs.",
])
y2 = group2(rx, y2 + 1, "Owned by humans", [
    "Architecture decisions and trade-off calls.",
    "Code review of every change; small focused commits.",
    "Correctness demonstrated by execution, not trust.",
])

by = max(y, y2, 156)
pdf.set_fill_color(*NAVY)
pdf.rect(MARGIN, by, CW, 16, "F")
pdf.set_xy(MARGIN + 4, by)
pdf.set_font("Helvetica", "B", 11.5)
pdf.set_text_color(*WHITE)
pdf.cell(0, 16, s("Principle:  AI accelerates delivery; the 20-thread race test - not the model - proves correctness."), 0, 0, "L")
pdf.set_text_color(*DARK)


# --------------------------------------------------------------------------- #
OUT = sys.argv[1] if len(sys.argv) > 1 else "docs/Movie-Booking-Presentation.pdf"
pdf.output(OUT)
print("Wrote", OUT)
