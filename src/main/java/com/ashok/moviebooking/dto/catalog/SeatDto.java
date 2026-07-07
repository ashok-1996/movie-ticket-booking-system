package com.ashok.moviebooking.dto.catalog;

import com.ashok.moviebooking.domain.SeatClass;
import jakarta.validation.Valid;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;

import java.util.List;

public class SeatDto {

    /** Bulk seat-layout creation: one entry per row. */
    public record LayoutRequest(@NotEmpty @Valid List<RowSpec> rows) {
    }

    public record RowSpec(
            @NotBlank String rowLabel,
            @Min(1) int seatCount,
            @NotNull SeatClass seatClass) {
    }

    public record Response(Long id, String rowLabel, Integer seatNumber, SeatClass seatClass) {
    }
}
