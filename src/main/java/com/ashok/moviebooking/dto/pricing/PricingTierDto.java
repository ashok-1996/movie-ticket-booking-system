package com.ashok.moviebooking.dto.pricing;

import com.ashok.moviebooking.domain.SeatClass;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

import java.math.BigDecimal;

public class PricingTierDto {

    public record Request(
            @NotBlank String name,
            @NotNull SeatClass seatClass,
            @NotNull @DecimalMin("0.0") BigDecimal multiplier) {
    }

    public record Response(Long id, String name, SeatClass seatClass, BigDecimal multiplier) {
    }
}
