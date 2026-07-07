package com.ashok.moviebooking.dto.booking;

import com.ashok.moviebooking.domain.BookingStatus;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.List;

public record BookingResponse(
        Long bookingId,
        Long showId,
        String movieTitle,
        BookingStatus status,
        List<SeatLine> seats,
        BigDecimal totalAmount,
        BigDecimal discountAmount,
        BigDecimal finalAmount,
        BigDecimal refundAmount,
        String discountCode,
        Instant holdExpiresAt,
        Instant createdAt,
        Instant confirmedAt,
        Instant cancelledAt) {

    public record SeatLine(Long showSeatId, String rowLabel, Integer seatNumber, BigDecimal price) {
    }
}
