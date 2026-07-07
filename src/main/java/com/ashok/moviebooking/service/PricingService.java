package com.ashok.moviebooking.service;

import com.ashok.moviebooking.domain.SeatClass;
import com.ashok.moviebooking.repository.PricingTierRepository;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.DayOfWeek;
import java.time.Instant;
import java.time.ZoneId;

@Service
public class PricingService {

    private final PricingTierRepository pricingTierRepository;
    private final BigDecimal weekendMultiplier;
    private final ZoneId zone;

    public PricingService(PricingTierRepository pricingTierRepository,
                          @Value("${pricing.weekend-multiplier}") BigDecimal weekendMultiplier,
                          @Value("${pricing.zone:UTC}") String zone) {
        this.pricingTierRepository = pricingTierRepository;
        this.weekendMultiplier = weekendMultiplier;
        this.zone = ZoneId.of(zone);
    }

    /**
     * price = basePrice * seatClassMultiplier * (weekend ? weekendMultiplier : 1),
     * rounded to 2 decimals. Weekend is derived from the show start time in the
     * configured business time zone.
     */
    public BigDecimal computeSeatPrice(BigDecimal basePrice, SeatClass seatClass, Instant showStart) {
        BigDecimal tierMultiplier = pricingTierRepository.findBySeatClass(seatClass)
                .map(t -> t.getMultiplier())
                .orElse(BigDecimal.ONE);
        BigDecimal price = basePrice.multiply(tierMultiplier);
        if (isWeekend(showStart)) {
            price = price.multiply(weekendMultiplier);
        }
        return price.setScale(2, RoundingMode.HALF_UP);
    }

    private boolean isWeekend(Instant instant) {
        DayOfWeek day = instant.atZone(zone).getDayOfWeek();
        return day == DayOfWeek.SATURDAY || day == DayOfWeek.SUNDAY;
    }
}
