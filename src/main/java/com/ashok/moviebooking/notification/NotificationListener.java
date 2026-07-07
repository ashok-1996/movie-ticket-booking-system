package com.ashok.moviebooking.notification;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Component;
import org.springframework.transaction.event.TransactionPhase;
import org.springframework.transaction.event.TransactionalEventListener;

/**
 * Fans out notifications AFTER the booking transaction commits, on a bounded
 * async worker pool, so the customer's booking response is never blocked and no
 * notification is ever sent for a rolled-back booking. Delivery is mocked with
 * logging (real channels are out of scope).
 */
@Component
public class NotificationListener {

    private static final Logger log = LoggerFactory.getLogger(NotificationListener.class);

    @Async("notificationExecutor")
    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void onBookingEvent(BookingEvent event) {
        switch (event.type()) {
            case CONFIRMED -> {
                log.info("[NOTIFY] Booking {} confirmed for user {} -> sending confirmation (email/SMS/push)",
                        event.bookingId(), event.userId());
                log.info("[NOTIFY] Booking {} -> scheduling show reminder for user {}",
                        event.bookingId(), event.userId());
            }
            case CANCELLED -> log.info("[NOTIFY] Booking {} cancelled for user {} -> sending cancellation + refund notice",
                    event.bookingId(), event.userId());
        }
    }
}
