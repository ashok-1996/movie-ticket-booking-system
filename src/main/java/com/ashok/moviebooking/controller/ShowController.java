package com.ashok.moviebooking.controller;

import com.ashok.moviebooking.dto.show.ShowDto;
import com.ashok.moviebooking.service.ShowService;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.web.bind.annotation.*;

import java.time.Instant;
import java.util.List;

@RestController
@RequestMapping("/shows")
public class ShowController {

    private final ShowService showService;

    public ShowController(ShowService showService) {
        this.showService = showService;
    }

    @GetMapping
    public List<ShowDto.Response> search(
            @RequestParam(required = false) Long cityId,
            @RequestParam(required = false) Long movieId,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant from,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant to) {
        return showService.search(cityId, movieId, from, to);
    }

    @GetMapping("/{showId}")
    public ShowDto.Response get(@PathVariable Long showId) {
        return showService.get(showId);
    }

    @GetMapping("/{showId}/seats")
    public List<ShowDto.SeatView> seatMap(@PathVariable Long showId) {
        return showService.getSeatMap(showId);
    }
}
