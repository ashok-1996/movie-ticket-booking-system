package com.ashok.moviebooking.dto.catalog;

import jakarta.validation.constraints.NotBlank;

public class CityDto {

    public record Request(@NotBlank String name, @NotBlank String state) {
    }

    public record Response(Long id, String name, String state) {
    }
}
