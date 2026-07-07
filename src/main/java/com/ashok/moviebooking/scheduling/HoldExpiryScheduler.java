package com.ashok.moviebooking.scheduling;

import com.ashok.moviebooking.domain.Booking;
import com.ashok.moviebooking.domain.BookingStatus;
import com.ashok.moviebooking.repository.BookingRepository;
import com.ashok.moviebooking.service.HoldExpiryService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.List;

/**
 * Periodically releases seats whose time-bound hold has expired. Runs every
 * {@code booking.hold.sweep-interval-ms} milliseconds.
 */
@Component
public class HoldExpiryScheduler {

    private static final Logger log = LoggerFactory.getLogger(HoldExpiryScheduler.class);

    private final BookingRepository bookingRepository;
    private final HoldExpiryService holdExpiryService;

    public HoldExpiryScheduler(BookingRepository bookingRepository, HoldExpiryService holdExpiryService) {
        this.bookingRepository = bookingRepository;
        this.holdExpiryService = holdExpiryService;
    }

    @Scheduled(fixedDelayString = "${booking.hold.sweep-interval-ms}")
    @Transactional(readOnly = true)
    public void sweepExpiredHolds() {
        List<Booking> expired = bookingRepository.findByStatusAndHoldExpiresAtBefore(BookingStatus.PENDING, Instant.now());
        if (expired.isEmpty()) {
            return;
        }
        log.debug("Sweeping {} expired hold(s)", expired.size());
        for (Booking booking : expired) {
            try {
                holdExpiryService.expireBooking(booking.getId());
            } catch (RuntimeException ex) {
                log.warn("Failed to expire booking {}: {}", booking.getId(), ex.getMessage());
            }
        }
    }
}
