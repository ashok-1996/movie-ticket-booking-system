package com.ashok.moviebooking.controller;

import com.ashok.moviebooking.dto.discount.DiscountCodeDto;
import com.ashok.moviebooking.service.DiscountService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/admin/discount-codes")
@PreAuthorize("hasRole('ADMIN')")
public class AdminDiscountController {

    private final DiscountService discountService;

    public AdminDiscountController(DiscountService discountService) {
        this.discountService = discountService;
    }

    @PostMapping
    public ResponseEntity<DiscountCodeDto.Response> create(@Valid @RequestBody DiscountCodeDto.Request req) {
        return ResponseEntity.status(HttpStatus.CREATED).body(discountService.create(req));
    }

    @GetMapping
    public List<DiscountCodeDto.Response> list() {
        return discountService.list();
    }
}
