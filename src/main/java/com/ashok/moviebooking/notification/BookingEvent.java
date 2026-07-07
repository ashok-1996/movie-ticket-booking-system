package com.ashok.moviebooking.notification;

/** Domain event published after a booking state change, consumed asynchronously. */
public record BookingEvent(Long bookingId, Long userId, Type type) {

    public enum Type {
        CONFIRMED,
        CANCELLED
    }
}
