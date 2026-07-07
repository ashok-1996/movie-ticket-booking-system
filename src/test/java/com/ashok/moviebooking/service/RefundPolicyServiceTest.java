package com.ashok.moviebooking.service;

import com.ashok.moviebooking.domain.RefundPolicy;
import com.ashok.moviebooking.repository.RefundPolicyRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

import java.math.BigDecimal;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

class RefundPolicyServiceTest {

    private RefundPolicyRepository repository;
    private RefundPolicyService service;

    @BeforeEach
    void setUp() {
        repository = mock(RefundPolicyRepository.class);
        service = new RefundPolicyService(repository);

        RefundPolicy policy = new RefundPolicy();
        policy.setName("Standard");
        policy.setFullRefundHoursBefore(24);
        policy.setPartialRefundHoursBefore(4);
        policy.setPartialRefundPercent(new BigDecimal("50"));
        policy.setActive(true);
        when(repository.findFirstByActiveTrueOrderByIdAsc()).thenReturn(Optional.of(policy));
    }

    @ParameterizedTest(name = "cancel {0}h before -> refund {1}")
    @CsvSource({
            "48, 500.00",  // full refund
            "24, 500.00",  // exactly at full-refund boundary
            "10, 250.00",  // partial (50%)
            "4,  250.00",  // exactly at partial boundary
            "1,  0.00"     // no refund
    })
    void computesRefundByCancellationWindow(long hoursBefore, String expectedRefund) {
        Instant now = Instant.now();
        Instant showStart = now.plus(hoursBefore, ChronoUnit.HOURS);
        BigDecimal refund = service.computeRefund(new BigDecimal("500.00"), showStart, now);
        assertThat(refund).isEqualByComparingTo(expectedRefund);
    }
}
