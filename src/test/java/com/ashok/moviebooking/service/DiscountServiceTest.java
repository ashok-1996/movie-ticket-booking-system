package com.ashok.moviebooking.service;

import com.ashok.moviebooking.common.ApiException;
import com.ashok.moviebooking.common.ErrorCode;
import com.ashok.moviebooking.domain.DiscountCode;
import com.ashok.moviebooking.domain.DiscountType;
import com.ashok.moviebooking.repository.DiscountCodeRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

class DiscountServiceTest {

    private DiscountCodeRepository repository;
    private DiscountService service;

    @BeforeEach
    void setUp() {
        repository = mock(DiscountCodeRepository.class);
        service = new DiscountService(repository);
    }

    @Test
    void blankCodeYieldsZeroDiscount() {
        assertThat(service.computeDiscount(null, new BigDecimal("500"), Instant.now()))
                .isEqualByComparingTo("0");
    }

    @Test
    void percentDiscountIsApplied() {
        stub(percent("P20", "20", null, null));
        assertThat(service.computeDiscount("P20", new BigDecimal("500.00"), Instant.now()))
                .isEqualByComparingTo("100.00");
    }

    @Test
    void flatDiscountIsApplied() {
        DiscountCode code = new DiscountCode();
        code.setCode("FLAT50");
        code.setType(DiscountType.FLAT);
        code.setValue(new BigDecimal("50"));
        code.setActive(true);
        stub(code);
        assertThat(service.computeDiscount("FLAT50", new BigDecimal("500"), Instant.now()))
                .isEqualByComparingTo("50.00");
    }

    @Test
    void percentDiscountIsCappedAtMaxDiscount() {
        stub(percent("BIG", "50", new BigDecimal("100"), null));
        assertThat(service.computeDiscount("BIG", new BigDecimal("1000"), Instant.now()))
                .isEqualByComparingTo("100.00");
    }

    @Test
    void discountNeverExceedsOrderAmount() {
        DiscountCode code = new DiscountCode();
        code.setCode("HUGE");
        code.setType(DiscountType.FLAT);
        code.setValue(new BigDecimal("999"));
        code.setActive(true);
        stub(code);
        assertThat(service.computeDiscount("HUGE", new BigDecimal("300"), Instant.now()))
                .isEqualByComparingTo("300.00");
    }

    @Test
    void belowMinimumAmountIsRejected() {
        stub(percent("MIN", "10", null, new BigDecimal("500")));
        assertThatThrownBy(() -> service.computeDiscount("MIN", new BigDecimal("100"), Instant.now()))
                .isInstanceOf(ApiException.class)
                .extracting(e -> ((ApiException) e).getCode())
                .isEqualTo(ErrorCode.INVALID_DISCOUNT);
    }

    @Test
    void inactiveCodeIsRejected() {
        DiscountCode code = percent("OFF", "10", null, null);
        code.setActive(false);
        stub(code);
        assertThatThrownBy(() -> service.computeDiscount("OFF", new BigDecimal("500"), Instant.now()))
                .isInstanceOf(ApiException.class);
    }

    @Test
    void unknownCodeIsRejected() {
        when(repository.findByCodeIgnoreCase("NOPE")).thenReturn(Optional.empty());
        assertThatThrownBy(() -> service.computeDiscount("NOPE", new BigDecimal("500"), Instant.now()))
                .isInstanceOf(ApiException.class);
    }

    @Test
    void applicableForReturnsEligibleCouponsSortedByBestSaving() {
        DiscountCode percentTen = percent("TEN", "10", null, null);      // 10% of 500 = 50
        DiscountCode flatHundred = new DiscountCode();
        flatHundred.setCode("FLAT100");
        flatHundred.setType(DiscountType.FLAT);
        flatHundred.setValue(new BigDecimal("100"));
        flatHundred.setActive(true);
        when(repository.findByActiveTrue()).thenReturn(List.of(percentTen, flatHundred));

        List<DiscountService.Quote> quotes = service.applicableFor(new BigDecimal("500"), Instant.now());

        assertThat(quotes).extracting(DiscountService.Quote::code).containsExactly("FLAT100", "TEN");
        assertThat(quotes.get(0).discountAmount()).isEqualByComparingTo("100.00");
        assertThat(quotes.get(1).discountAmount()).isEqualByComparingTo("50.00");
    }

    @Test
    void applicableForExcludesCouponsBelowMinimumAmount() {
        when(repository.findByActiveTrue()).thenReturn(List.of(percent("MIN", "10", null, new BigDecimal("1000"))));

        assertThat(service.applicableFor(new BigDecimal("500"), Instant.now())).isEmpty();
    }

    @Test
    void applicableForExcludesExpiredCoupons() {
        DiscountCode expired = percent("OLD", "10", null, null);
        expired.setValidTo(Instant.now().minusSeconds(3600));
        when(repository.findByActiveTrue()).thenReturn(List.of(expired));

        assertThat(service.applicableFor(new BigDecimal("500"), Instant.now())).isEmpty();
    }

    private DiscountCode percent(String code, String value, BigDecimal max, BigDecimal min) {
        DiscountCode dc = new DiscountCode();
        dc.setCode(code);
        dc.setType(DiscountType.PERCENT);
        dc.setValue(new BigDecimal(value));
        dc.setMaxDiscount(max);
        dc.setMinAmount(min);
        dc.setActive(true);
        return dc;
    }

    private void stub(DiscountCode code) {
        when(repository.findByCodeIgnoreCase(code.getCode())).thenReturn(Optional.of(code));
    }
}
