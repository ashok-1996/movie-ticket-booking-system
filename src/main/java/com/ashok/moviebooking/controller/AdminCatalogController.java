package com.ashok.moviebooking.controller;

import com.ashok.moviebooking.dto.catalog.*;
import com.ashok.moviebooking.service.CatalogService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/admin")
@PreAuthorize("hasRole('ADMIN')")
public class AdminCatalogController {

    private final CatalogService catalogService;

    public AdminCatalogController(CatalogService catalogService) {
        this.catalogService = catalogService;
    }

    @PostMapping("/cities")
    public ResponseEntity<CityDto.Response> createCity(@Valid @RequestBody CityDto.Request req) {
        return ResponseEntity.status(HttpStatus.CREATED).body(catalogService.createCity(req));
    }

    @GetMapping("/cities")
    public List<CityDto.Response> listCities() {
        return catalogService.listCities();
    }

    @PostMapping("/theaters")
    public ResponseEntity<TheaterDto.Response> createTheater(@Valid @RequestBody TheaterDto.Request req) {
        return ResponseEntity.status(HttpStatus.CREATED).body(catalogService.createTheater(req));
    }

    @GetMapping("/theaters")
    public List<TheaterDto.Response> listTheaters(@RequestParam(required = false) Long cityId) {
        return catalogService.listTheaters(cityId);
    }

    @PostMapping("/screens")
    public ResponseEntity<ScreenDto.Response> createScreen(@Valid @RequestBody ScreenDto.Request req) {
        return ResponseEntity.status(HttpStatus.CREATED).body(catalogService.createScreen(req));
    }

    @PostMapping("/screens/{screenId}/seats")
    public ResponseEntity<List<SeatDto.Response>> createSeatLayout(@PathVariable Long screenId,
                                                                   @Valid @RequestBody SeatDto.LayoutRequest req) {
        return ResponseEntity.status(HttpStatus.CREATED).body(catalogService.createSeatLayout(screenId, req));
    }

    @GetMapping("/screens/{screenId}/seats")
    public List<SeatDto.Response> listSeats(@PathVariable Long screenId) {
        return catalogService.listSeats(screenId);
    }

    @PostMapping("/movies")
    public ResponseEntity<MovieDto.Response> createMovie(@Valid @RequestBody MovieDto.Request req) {
        return ResponseEntity.status(HttpStatus.CREATED).body(catalogService.createMovie(req));
    }

    @GetMapping("/movies")
    public List<MovieDto.Response> listMovies() {
        return catalogService.listMovies();
    }
}
