package com.ashok.moviebooking.dto.show;

import com.ashok.moviebooking.domain.SeatClass;
import com.ashok.moviebooking.domain.ShowSeatStatus;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;

import java.math.BigDecimal;
import java.time.Instant;

public class ShowDto {

    public record Request(
            @NotNull Long movieId,
            @NotNull Long screenId,
            @NotNull Instant startTime,
            @NotNull @Positive BigDecimal basePrice) {
    }

    public record Response(
            Long id,
            Long movieId,
            String movieTitle,
            Long screenId,
            String screenName,
            String theaterName,
            String cityName,
            Instant startTime,
            Instant endTime,
            BigDecimal basePrice) {
    }

    public record SeatView(
            Long showSeatId,
            String rowLabel,
            Integer seatNumber,
            SeatClass seatClass,
            ShowSeatStatus status,
            BigDecimal price) {
    }
}
