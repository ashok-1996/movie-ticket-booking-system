package com.ashok.moviebooking.controller;

import com.ashok.moviebooking.dto.pricing.PricingTierDto;
import com.ashok.moviebooking.service.PricingTierService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/admin/pricing-tiers")
@PreAuthorize("hasRole('ADMIN')")
public class AdminPricingController {

    private final PricingTierService pricingTierService;

    public AdminPricingController(PricingTierService pricingTierService) {
        this.pricingTierService = pricingTierService;
    }

    @PostMapping
    public ResponseEntity<PricingTierDto.Response> upsert(@Valid @RequestBody PricingTierDto.Request req) {
        return ResponseEntity.status(HttpStatus.CREATED).body(pricingTierService.upsert(req));
    }

    @PutMapping("/{id}")
    public PricingTierDto.Response update(@PathVariable Long id, @Valid @RequestBody PricingTierDto.Request req) {
        return pricingTierService.update(id, req);
    }

    @GetMapping
    public List<PricingTierDto.Response> list() {
        return pricingTierService.list();
    }
}
