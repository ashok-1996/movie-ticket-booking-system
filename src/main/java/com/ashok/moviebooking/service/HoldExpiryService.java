package com.ashok.moviebooking.service;

import com.ashok.moviebooking.domain.Booking;
import com.ashok.moviebooking.domain.BookingSeat;
import com.ashok.moviebooking.domain.BookingStatus;
import com.ashok.moviebooking.domain.ShowSeat;
import com.ashok.moviebooking.domain.ShowSeatStatus;
import com.ashok.moviebooking.repository.BookingRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;

@Service
public class HoldExpiryService {

    private final BookingRepository bookingRepository;
    private final AuditService auditService;

    public HoldExpiryService(BookingRepository bookingRepository, AuditService auditService) {
        this.bookingRepository = bookingRepository;
        this.auditService = auditService;
    }

    /**
     * Expires a single stale hold in its own transaction so that one failure
     * (for example a lost optimistic-lock race against a concurrent confirm)
     * does not roll back the whole sweep batch.
     */
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void expireBooking(Long bookingId) {
        Booking booking = bookingRepository.findById(bookingId).orElse(null);
        if (booking == null || booking.getStatus() != BookingStatus.PENDING) {
            return;
        }
        if (booking.getHoldExpiresAt() == null || booking.getHoldExpiresAt().isAfter(Instant.now())) {
            return;
        }
        for (BookingSeat bs : booking.getSeats()) {
            if (bs.isActive()) {
                ShowSeat seat = bs.getShowSeat();
                seat.setStatus(ShowSeatStatus.AVAILABLE);
                seat.setHeldUntil(null);
                seat.setHeldByUserId(null);
                bs.setActive(false);
            }
        }
        booking.setStatus(BookingStatus.EXPIRED);
        auditService.record("Booking", booking.getId(), "HOLD_EXPIRED_SWEEP", null, booking.getUser().getId());
    }
}
