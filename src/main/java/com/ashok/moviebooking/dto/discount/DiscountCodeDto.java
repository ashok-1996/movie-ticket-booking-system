package com.ashok.moviebooking.dto.discount;

import com.ashok.moviebooking.domain.DiscountType;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;

import java.math.BigDecimal;
import java.time.Instant;

public class DiscountCodeDto {

    public record Request(
            @NotBlank String code,
            @NotNull DiscountType type,
            @NotNull @Positive BigDecimal value,
            BigDecimal maxDiscount,
            BigDecimal minAmount,
            Instant validFrom,
            Instant validTo,
            Boolean active) {
    }

    public record Response(
            Long id,
            String code,
            DiscountType type,
            BigDecimal value,
            BigDecimal maxDiscount,
            BigDecimal minAmount,
            Instant validFrom,
            Instant validTo,
            boolean active) {
    }
}
