package com.ashok.moviebooking.dto.catalog;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

public class TheaterDto {

    public record Request(@NotBlank String name, @NotBlank String address, @NotNull Long cityId) {
    }

    public record Response(Long id, String name, String address, Long cityId, String cityName) {
    }
}
