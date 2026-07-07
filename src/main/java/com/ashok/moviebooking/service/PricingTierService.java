package com.ashok.moviebooking.service;

import com.ashok.moviebooking.common.ApiException;
import com.ashok.moviebooking.domain.PricingTier;
import com.ashok.moviebooking.dto.pricing.PricingTierDto;
import com.ashok.moviebooking.repository.PricingTierRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class PricingTierService {

    private final PricingTierRepository repository;

    public PricingTierService(PricingTierRepository repository) {
        this.repository = repository;
    }

    @Transactional
    public PricingTierDto.Response upsert(PricingTierDto.Request req) {
        PricingTier tier = repository.findBySeatClass(req.seatClass()).orElseGet(PricingTier::new);
        tier.setName(req.name());
        tier.setSeatClass(req.seatClass());
        tier.setMultiplier(req.multiplier());
        return toResponse(repository.save(tier));
    }

    @Transactional
    public PricingTierDto.Response update(Long id, PricingTierDto.Request req) {
        PricingTier tier = repository.findById(id).orElseThrow(() -> ApiException.notFound("Pricing tier"));
        tier.setName(req.name());
        tier.setSeatClass(req.seatClass());
        tier.setMultiplier(req.multiplier());
        return toResponse(repository.save(tier));
    }

    @Transactional(readOnly = true)
    public List<PricingTierDto.Response> list() {
        return repository.findAll().stream().map(this::toResponse).toList();
    }

    private PricingTierDto.Response toResponse(PricingTier t) {
        return new PricingTierDto.Response(t.getId(), t.getName(), t.getSeatClass(), t.getMultiplier());
    }
}
