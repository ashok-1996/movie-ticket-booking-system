package com.ashok.moviebooking.dto.catalog;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

public class ScreenDto {

    public record Request(@NotBlank String name, @NotNull Long theaterId) {
    }

    public record Response(Long id, String name, Long theaterId, String theaterName) {
    }
}
