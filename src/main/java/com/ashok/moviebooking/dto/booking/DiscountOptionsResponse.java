package com.ashok.moviebooking.dto.booking;

import com.ashok.moviebooking.domain.DiscountType;

import java.math.BigDecimal;
import java.util.List;

/**
 * Coupons a customer can apply to a held (pending) booking, each showing how
 * much it would save and the resulting price, so they can decide before paying.
 */
public record DiscountOptionsResponse(
        Long bookingId,
        BigDecimal totalAmount,
        List<Option> options) {

    public record Option(
            String code,
            DiscountType type,
            BigDecimal value,
            BigDecimal discountAmount,
            BigDecimal finalAmount) {
    }
}
