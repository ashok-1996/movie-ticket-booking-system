package com.ashok.moviebooking.domain;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

/**
 * Represents the allocation of a show seat to a booking. A partial unique index
 * on show_seat_id WHERE active = true is the database-enforced physical backstop
 * against double-allocation: since a ShowSeat is unique per (show, seat), this
 * is equivalent to UNIQUE(show_id, seat_id) for active allocations. When a seat
 * is released (hold expiry, cancellation, refund) the row is kept for history
 * but flagged inactive so the seat can be re-booked.
 */
@Entity
@Table(name = "booking_seat")
@Getter
@Setter
public class BookingSeat {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "booking_id", nullable = false)
    private Booking booking;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "show_seat_id", nullable = false)
    private ShowSeat showSeat;

    @Column(nullable = false)
    private boolean active = true;
}
