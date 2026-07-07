package com.ashok.moviebooking.dto.booking;

import jakarta.validation.constraints.NotEmpty;

import java.util.List;

public record HoldRequest(@NotEmpty List<Long> showSeatIds) {
}
