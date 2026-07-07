package com.ashok.moviebooking.domain;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

import java.math.BigDecimal;

/**
 * Multiplier applied to a show's base price for a given seat class.
 * Weekend pricing is applied on top via a configurable global multiplier.
 */
@Entity
@Table(name = "pricing_tier", uniqueConstraints = @UniqueConstraint(columnNames = "seat_class"))
@Getter
@Setter
public class PricingTier {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    @Enumerated(EnumType.STRING)
    @Column(name = "seat_class", nullable = false, length = 20)
    private SeatClass seatClass;

    @Column(nullable = false, precision = 6, scale = 3)
    private BigDecimal multiplier;
}
