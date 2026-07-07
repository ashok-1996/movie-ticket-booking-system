package com.ashok.moviebooking.dto.catalog;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

public class MovieDto {

    public record Request(
            @NotBlank String title,
            @NotBlank String language,
            @NotBlank String genre,
            @NotNull @Min(1) Integer durationMinutes,
            String certification) {
    }

    public record Response(Long id, String title, String language, String genre, Integer durationMinutes, String certification) {
    }
}
