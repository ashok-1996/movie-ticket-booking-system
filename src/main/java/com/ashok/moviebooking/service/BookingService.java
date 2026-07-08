package com.ashok.moviebooking.service;

import com.ashok.moviebooking.common.ApiException;
import com.ashok.moviebooking.common.ErrorCode;
import com.ashok.moviebooking.domain.*;
import com.ashok.moviebooking.dto.booking.BookingResponse;
import com.ashok.moviebooking.dto.booking.ConfirmRequest;
import com.ashok.moviebooking.dto.booking.DiscountOptionsResponse;
import com.ashok.moviebooking.notification.BookingEvent;
import com.ashok.moviebooking.repository.*;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.List;
import java.util.UUID;

@Service
public class BookingService {

    private final ShowSeatRepository showSeatRepository;
    private final BookingRepository bookingRepository;
    private final PaymentRepository paymentRepository;
    private final UserRepository userRepository;
    private final DiscountService discountService;
    private final RefundPolicyService refundPolicyService;
    private final AuditService auditService;
    private final ApplicationEventPublisher eventPublisher;
    private final long holdTtlSeconds;

    public BookingService(ShowSeatRepository showSeatRepository, BookingRepository bookingRepository,
                          PaymentRepository paymentRepository, UserRepository userRepository,
                          DiscountService discountService, RefundPolicyService refundPolicyService,
                          AuditService auditService, ApplicationEventPublisher eventPublisher,
                          @Value("${booking.hold.ttl-seconds}") long holdTtlSeconds) {
        this.showSeatRepository = showSeatRepository;
        this.bookingRepository = bookingRepository;
        this.paymentRepository = paymentRepository;
        this.userRepository = userRepository;
        this.discountService = discountService;
        this.refundPolicyService = refundPolicyService;
        this.auditService = auditService;
        this.eventPublisher = eventPublisher;
        this.holdTtlSeconds = holdTtlSeconds;
    }

    /**
     * Places a time-bound hold on the requested seats. Concurrency defense:
     *  (1) pessimistic write lock (SELECT ... FOR UPDATE) taken in deterministic
     *      id order serializes competing holds on the same seat;
     *  (2) the ShowSeat @Version guards lost updates;
     *  (3) the partial unique index on booking_seat is the DB backstop.
     */
    @Transactional
    public BookingResponse hold(Long showId, List<Long> showSeatIds, Long userId) {
        List<Long> ids = showSeatIds.stream().distinct().sorted().toList();
        List<ShowSeat> seats = showSeatRepository.lockByIds(ids);

        if (seats.size() != ids.size()) {
            throw ApiException.notFound("One or more seats");
        }
        // Requirement: a single booking must not mix pricing tiers (seat classes),
        // e.g. 2 REGULAR + 5 PREMIUM is rejected.
        if (seats.stream().map(ss -> ss.getSeat().getSeatClass()).distinct().count() > 1) {
            throw new ApiException(ErrorCode.VALIDATION_ERROR,
                    "All seats in one booking must belong to the same pricing tier (seat class)");
        }
        Instant now = Instant.now();
        Instant expiresAt = now.plusSeconds(holdTtlSeconds);

        User user = userRepository.getReferenceById(userId);
        Booking booking = new Booking();
        booking.setUser(user);
        booking.setStatus(BookingStatus.PENDING);
        booking.setHoldExpiresAt(expiresAt);
        booking.setCreatedAt(now);

        BigDecimal total = BigDecimal.ZERO;
        for (ShowSeat seat : seats) {
            if (!seat.getShow().getId().equals(showId)) {
                throw new ApiException(ErrorCode.VALIDATION_ERROR, "Seat does not belong to show " + showId);
            }
            if (seat.getStatus() != ShowSeatStatus.AVAILABLE) {
                throw new ApiException(ErrorCode.SEAT_UNAVAILABLE,
                        "Seat " + seat.getSeat().getRowLabel() + seat.getSeat().getSeatNumber() + " is not available");
            }
            seat.setStatus(ShowSeatStatus.HELD);
            seat.setHeldUntil(expiresAt);
            seat.setHeldByUserId(userId);

            BookingSeat bookingSeat = new BookingSeat();
            bookingSeat.setBooking(booking);
            bookingSeat.setShowSeat(seat);
            bookingSeat.setActive(true);
            booking.getSeats().add(bookingSeat);
            total = total.add(seat.getPrice());
        }
        booking.setShow(seats.get(0).getShow());
        booking.setTotalAmount(total);
        booking.setFinalAmount(total);

        Booking saved = bookingRepository.save(booking);
        auditService.record("Booking", saved.getId(), "HOLD_CREATED",
                "seats=" + ids + " expiresAt=" + expiresAt, userId);
        return toResponse(saved);
    }

    /** Confirms a held booking: applies discount, records payment, marks seats BOOKED. */
    @Transactional
    public BookingResponse confirm(Long bookingId, ConfirmRequest req, Long userId) {
        Booking booking = loadOwnedBooking(bookingId, userId);
        if (booking.getStatus() != BookingStatus.PENDING) {
            throw new ApiException(ErrorCode.CONFLICT, "Booking is not in a holdable state");
        }
        Instant now = Instant.now();
        if (booking.getHoldExpiresAt() != null && booking.getHoldExpiresAt().isBefore(now)) {
            releaseSeats(booking);
            booking.setStatus(BookingStatus.EXPIRED);
            auditService.record("Booking", booking.getId(), "EXPIRED_ON_CONFIRM", null, userId);
            throw new ApiException(ErrorCode.HOLD_EXPIRED, "Seat hold has expired; please reselect seats");
        }

        BigDecimal total = booking.getTotalAmount();
        BigDecimal discount = discountService.computeDiscount(
                req == null ? null : req.discountCode(), total, now);
        BigDecimal finalAmount = total.subtract(discount);

        for (BookingSeat bs : booking.getSeats()) {
            if (bs.isActive()) {
                ShowSeat seat = bs.getShowSeat();
                seat.setStatus(ShowSeatStatus.BOOKED);
                seat.setHeldUntil(null);
                seat.setHeldByUserId(null);
            }
        }

        Payment payment = new Payment();
        payment.setBooking(booking);
        payment.setAmount(finalAmount);
        payment.setStatus(PaymentStatus.SUCCESS);
        payment.setMethod(req != null && req.paymentMethod() != null ? req.paymentMethod() : "MOCK");
        payment.setTransactionRef(UUID.randomUUID().toString());
        payment.setPaidAt(now);
        paymentRepository.save(payment);

        booking.setDiscountAmount(discount);
        booking.setDiscountCode(req == null ? null : req.discountCode());
        booking.setFinalAmount(finalAmount);
        booking.setStatus(BookingStatus.CONFIRMED);
        booking.setConfirmedAt(now);

        auditService.record("Booking", booking.getId(), "CONFIRMED",
                "final=" + finalAmount + " discount=" + discount, userId);
        eventPublisher.publishEvent(new BookingEvent(booking.getId(), userId, BookingEvent.Type.CONFIRMED));
        return toResponse(booking);
    }

    /** Cancels a confirmed booking, releasing seats and issuing a refund per policy. */
    @Transactional
    public BookingResponse cancel(Long bookingId, Long userId) {
        Booking booking = loadOwnedBooking(bookingId, userId);
        if (booking.getStatus() != BookingStatus.CONFIRMED) {
            throw new ApiException(ErrorCode.REFUND_NOT_ALLOWED, "Only confirmed bookings can be cancelled");
        }
        Instant now = Instant.now();
        BigDecimal refund = refundPolicyService.computeRefund(booking.getFinalAmount(), booking.getShow().getStartTime(), now);

        releaseSeats(booking);

        paymentRepository.findByBookingId(booking.getId()).ifPresent(payment -> {
            if (refund.compareTo(BigDecimal.ZERO) <= 0) {
                payment.setStatus(PaymentStatus.SUCCESS);
            } else if (refund.compareTo(payment.getAmount()) >= 0) {
                payment.setStatus(PaymentStatus.REFUNDED);
            } else {
                payment.setStatus(PaymentStatus.PARTIALLY_REFUNDED);
            }
        });

        booking.setRefundAmount(refund);
        booking.setStatus(refund.compareTo(BigDecimal.ZERO) > 0 ? BookingStatus.REFUNDED : BookingStatus.CANCELLED);
        booking.setCancelledAt(now);

        auditService.record("Booking", booking.getId(), "CANCELLED", "refund=" + refund, userId);
        eventPublisher.publishEvent(new BookingEvent(booking.getId(), userId, BookingEvent.Type.CANCELLED));
        return toResponse(booking);
    }

    /**
     * Preview step: returns the coupons the owner could apply to this pending
     * booking (based on its seat prices / total), each with the resulting price.
     * Purely informational - the customer still chooses whether to confirm.
     */
    @Transactional(readOnly = true)
    public DiscountOptionsResponse availableDiscounts(Long bookingId, Long userId) {
        Booking booking = loadOwnedBooking(bookingId, userId);
        if (booking.getStatus() != BookingStatus.PENDING) {
            throw new ApiException(ErrorCode.CONFLICT, "Discounts can only be previewed for a pending booking");
        }
        BigDecimal amount = booking.getTotalAmount();
        List<DiscountOptionsResponse.Option> options = discountService.applicableFor(amount, Instant.now()).stream()
                .map(q -> new DiscountOptionsResponse.Option(
                        q.code(), q.type(), q.value(), q.discountAmount(), amount.subtract(q.discountAmount())))
                .toList();
        return new DiscountOptionsResponse(booking.getId(), amount, options);
    }

    @Transactional(readOnly = true)
    public List<BookingResponse> myBookings(Long userId) {
        return bookingRepository.findByUserIdOrderByCreatedAtDesc(userId).stream().map(this::toResponse).toList();
    }

    @Transactional(readOnly = true)
    public BookingResponse getBooking(Long bookingId, Long userId) {
        return toResponse(loadOwnedBooking(bookingId, userId));
    }

    private Booking loadOwnedBooking(Long bookingId, Long userId) {
        Booking booking = bookingRepository.findById(bookingId).orElseThrow(() -> ApiException.notFound("Booking"));
        if (!booking.getUser().getId().equals(userId)) {
            throw new ApiException(ErrorCode.FORBIDDEN, "You do not own this booking");
        }
        return booking;
    }

    private void releaseSeats(Booking booking) {
        for (BookingSeat bs : booking.getSeats()) {
            if (bs.isActive()) {
                ShowSeat seat = bs.getShowSeat();
                seat.setStatus(ShowSeatStatus.AVAILABLE);
                seat.setHeldUntil(null);
                seat.setHeldByUserId(null);
                bs.setActive(false);
            }
        }
    }

    private BookingResponse toResponse(Booking b) {
        List<BookingResponse.SeatLine> lines = b.getSeats().stream()
                .map(bs -> new BookingResponse.SeatLine(
                        bs.getShowSeat().getId(),
                        bs.getShowSeat().getSeat().getRowLabel(),
                        bs.getShowSeat().getSeat().getSeatNumber(),
                        bs.getShowSeat().getPrice()))
                .toList();
        return new BookingResponse(
                b.getId(),
                b.getShow().getId(),
                b.getShow().getMovie().getTitle(),
                b.getStatus(),
                lines,
                b.getTotalAmount(),
                b.getDiscountAmount(),
                b.getFinalAmount(),
                b.getRefundAmount(),
                b.getDiscountCode(),
                b.getHoldExpiresAt(),
                b.getCreatedAt(),
                b.getConfirmedAt(),
                b.getCancelledAt());
    }
}
