package com.ashok.moviebooking.dto.refund;

import jakarta.validation.constraints.DecimalMax;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

import java.math.BigDecimal;

public class RefundPolicyDto {

    public record Request(
            @NotBlank String name,
            @Min(0) int fullRefundHoursBefore,
            @Min(0) int partialRefundHoursBefore,
            @NotNull @DecimalMin("0.0") @DecimalMax("100.0") BigDecimal partialRefundPercent,
            Boolean active) {
    }

    public record Response(
            Long id,
            String name,
            int fullRefundHoursBefore,
            int partialRefundHoursBefore,
            BigDecimal partialRefundPercent,
            boolean active) {
    }
}
