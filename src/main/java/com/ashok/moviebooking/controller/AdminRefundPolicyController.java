package com.ashok.moviebooking.controller;

import com.ashok.moviebooking.dto.refund.RefundPolicyDto;
import com.ashok.moviebooking.service.RefundPolicyService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/admin/refund-policies")
@PreAuthorize("hasRole('ADMIN')")
public class AdminRefundPolicyController {

    private final RefundPolicyService refundPolicyService;

    public AdminRefundPolicyController(RefundPolicyService refundPolicyService) {
        this.refundPolicyService = refundPolicyService;
    }

    @PostMapping
    public ResponseEntity<RefundPolicyDto.Response> create(@Valid @RequestBody RefundPolicyDto.Request req) {
        return ResponseEntity.status(HttpStatus.CREATED).body(refundPolicyService.create(req));
    }

    @PutMapping("/{id}")
    public RefundPolicyDto.Response update(@PathVariable Long id, @Valid @RequestBody RefundPolicyDto.Request req) {
        return refundPolicyService.update(id, req);
    }

    @GetMapping
    public List<RefundPolicyDto.Response> list() {
        return refundPolicyService.list();
    }
}
