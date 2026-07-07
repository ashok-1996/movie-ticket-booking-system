package com.ashok.moviebooking.controller;

import com.ashok.moviebooking.dto.show.ShowDto;
import com.ashok.moviebooking.service.ShowService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/admin/shows")
@PreAuthorize("hasRole('ADMIN')")
public class AdminShowController {

    private final ShowService showService;

    public AdminShowController(ShowService showService) {
        this.showService = showService;
    }

    @PostMapping
    public ResponseEntity<ShowDto.Response> createShow(@Valid @RequestBody ShowDto.Request req) {
        return ResponseEntity.status(HttpStatus.CREATED).body(showService.createShow(req));
    }
}
