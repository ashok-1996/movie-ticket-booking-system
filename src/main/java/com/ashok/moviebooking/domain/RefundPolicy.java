package com.ashok.moviebooking.domain;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

import java.math.BigDecimal;

/**
 * A tiered, time-based refund policy. If a booking is cancelled at least
 * {@code fullRefundHoursBefore} hours before show start, a full refund is
 * issued. If cancelled at least {@code partialRefundHoursBefore} hours before,
 * {@code partialRefundPercent} of the amount is refunded. Otherwise no refund.
 */
@Entity
@Table(name = "refund_policy")
@Getter
@Setter
public class RefundPolicy {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    @Column(name = "full_refund_hours_before", nullable = false)
    private int fullRefundHoursBefore;

    @Column(name = "partial_refund_hours_before", nullable = false)
    private int partialRefundHoursBefore;

    @Column(name = "partial_refund_percent", nullable = false, precision = 5, scale = 2)
    private BigDecimal partialRefundPercent;

    @Column(nullable = false)
    private boolean active = true;
}
