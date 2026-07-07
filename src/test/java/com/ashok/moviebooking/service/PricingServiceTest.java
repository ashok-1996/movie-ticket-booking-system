package com.ashok.moviebooking.service;

import com.ashok.moviebooking.domain.PricingTier;
import com.ashok.moviebooking.domain.SeatClass;
import com.ashok.moviebooking.repository.PricingTierRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.math.BigDecimal;
import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneOffset;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

class PricingServiceTest {

    private static final Instant WEEKDAY = LocalDate.of(2026, 7, 6).atStartOfDay(ZoneOffset.UTC).toInstant();  // Monday
    private static final Instant WEEKEND = LocalDate.of(2026, 7, 11).atStartOfDay(ZoneOffset.UTC).toInstant(); // Saturday

    private PricingTierRepository repository;
    private PricingService service;

    @BeforeEach
    void setUp() {
        repository = mock(PricingTierRepository.class);
        service = new PricingService(repository, new BigDecimal("1.25"), "UTC");
    }

    @Test
    void regularWeekdayPriceEqualsBase() {
        stub(SeatClass.REGULAR, "1.0");
        assertThat(service.computeSeatPrice(new BigDecimal("100.00"), SeatClass.REGULAR, WEEKDAY))
                .isEqualByComparingTo("100.00");
    }

    @Test
    void weekendAppliesSurcharge() {
        stub(SeatClass.REGULAR, "1.0");
        assertThat(service.computeSeatPrice(new BigDecimal("100.00"), SeatClass.REGULAR, WEEKEND))
                .isEqualByComparingTo("125.00");
    }

    @Test
    void premiumTierMultiplierApplies() {
        stub(SeatClass.PREMIUM, "1.5");
        assertThat(service.computeSeatPrice(new BigDecimal("100.00"), SeatClass.PREMIUM, WEEKDAY))
                .isEqualByComparingTo("150.00");
    }

    @Test
    void premiumWeekendCombinesMultipliers() {
        stub(SeatClass.PREMIUM, "1.5");
        assertThat(service.computeSeatPrice(new BigDecimal("100.00"), SeatClass.PREMIUM, WEEKEND))
                .isEqualByComparingTo("187.50");
    }

    @Test
    void missingTierDefaultsToBase() {
        when(repository.findBySeatClass(any())).thenReturn(Optional.empty());
        assertThat(service.computeSeatPrice(new BigDecimal("100.00"), SeatClass.RECLINER, WEEKDAY))
                .isEqualByComparingTo("100.00");
    }

    private void stub(SeatClass seatClass, String multiplier) {
        PricingTier tier = new PricingTier();
        tier.setSeatClass(seatClass);
        tier.setMultiplier(new BigDecimal(multiplier));
        when(repository.findBySeatClass(seatClass)).thenReturn(Optional.of(tier));
    }
}
