package com.ashok.moviebooking.repository;

import com.ashok.moviebooking.domain.RefundPolicy;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface RefundPolicyRepository extends JpaRepository<RefundPolicy, Long> {
    Optional<RefundPolicy> findFirstByActiveTrueOrderByIdAsc();
}
