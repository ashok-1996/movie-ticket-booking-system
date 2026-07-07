package com.ashok.moviebooking.service;

import com.ashok.moviebooking.common.ApiException;
import com.ashok.moviebooking.domain.RefundPolicy;
import com.ashok.moviebooking.dto.refund.RefundPolicyDto;
import com.ashok.moviebooking.repository.RefundPolicyRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.Duration;
import java.time.Instant;
import java.util.List;

@Service
public class RefundPolicyService {

    private final RefundPolicyRepository repository;

    public RefundPolicyService(RefundPolicyRepository repository) {
        this.repository = repository;
    }

    @Transactional
    public RefundPolicyDto.Response create(RefundPolicyDto.Request req) {
        RefundPolicy policy = new RefundPolicy();
        apply(policy, req);
        return toResponse(repository.save(policy));
    }

    @Transactional
    public RefundPolicyDto.Response update(Long id, RefundPolicyDto.Request req) {
        RefundPolicy policy = repository.findById(id).orElseThrow(() -> ApiException.notFound("Refund policy"));
        apply(policy, req);
        return toResponse(repository.save(policy));
    }

    @Transactional(readOnly = true)
    public List<RefundPolicyDto.Response> list() {
        return repository.findAll().stream().map(this::toResponse).toList();
    }

    /**
     * Computes the refund amount for a cancellation based on the active policy
     * and how far ahead of show start the cancellation happens.
     */
    @Transactional(readOnly = true)
    public BigDecimal computeRefund(BigDecimal paidAmount, Instant showStart, Instant cancelTime) {
        RefundPolicy policy = repository.findFirstByActiveTrueOrderByIdAsc().orElse(null);
        if (policy == null) {
            return BigDecimal.ZERO;
        }
        long hoursBefore = Duration.between(cancelTime, showStart).toHours();
        BigDecimal percent;
        if (hoursBefore >= policy.getFullRefundHoursBefore()) {
            percent = BigDecimal.valueOf(100);
        } else if (hoursBefore >= policy.getPartialRefundHoursBefore()) {
            percent = policy.getPartialRefundPercent();
        } else {
            percent = BigDecimal.ZERO;
        }
        return paidAmount.multiply(percent).divide(BigDecimal.valueOf(100), 2, RoundingMode.HALF_UP);
    }

    private void apply(RefundPolicy policy, RefundPolicyDto.Request req) {
        policy.setName(req.name());
        policy.setFullRefundHoursBefore(req.fullRefundHoursBefore());
        policy.setPartialRefundHoursBefore(req.partialRefundHoursBefore());
        policy.setPartialRefundPercent(req.partialRefundPercent());
        policy.setActive(req.active() == null || req.active());
    }

    private RefundPolicyDto.Response toResponse(RefundPolicy p) {
        return new RefundPolicyDto.Response(p.getId(), p.getName(), p.getFullRefundHoursBefore(),
                p.getPartialRefundHoursBefore(), p.getPartialRefundPercent(), p.isActive());
    }
}
