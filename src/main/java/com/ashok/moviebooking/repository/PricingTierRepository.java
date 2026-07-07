package com.ashok.moviebooking.repository;

import com.ashok.moviebooking.domain.PricingTier;
import com.ashok.moviebooking.domain.SeatClass;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface PricingTierRepository extends JpaRepository<PricingTier, Long> {
    Optional<PricingTier> findBySeatClass(SeatClass seatClass);
}
