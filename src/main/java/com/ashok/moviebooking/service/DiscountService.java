package com.ashok.moviebooking.service;

import com.ashok.moviebooking.common.ApiException;
import com.ashok.moviebooking.common.ErrorCode;
import com.ashok.moviebooking.domain.DiscountCode;
import com.ashok.moviebooking.domain.DiscountType;
import com.ashok.moviebooking.dto.discount.DiscountCodeDto;
import com.ashok.moviebooking.repository.DiscountCodeRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.Instant;
import java.util.Comparator;
import java.util.List;

@Service
public class DiscountService {

    private final DiscountCodeRepository repository;

    public DiscountService(DiscountCodeRepository repository) {
        this.repository = repository;
    }

    @Transactional
    public DiscountCodeDto.Response create(DiscountCodeDto.Request req) {
        repository.findByCodeIgnoreCase(req.code()).ifPresent(c -> {
            throw new ApiException(ErrorCode.CONFLICT, "Discount code already exists: " + req.code());
        });
        DiscountCode code = new DiscountCode();
        apply(code, req);
        return toResponse(repository.save(code));
    }

    @Transactional(readOnly = true)
    public List<DiscountCodeDto.Response> list() {
        return repository.findAll().stream().map(this::toResponse).toList();
    }

    /**
     * Validates a discount code against the order amount and time window and
     * returns the discount amount (never more than the order amount).
     */
    @Transactional(readOnly = true)
    public BigDecimal computeDiscount(String code, BigDecimal amount, Instant now) {
        if (code == null || code.isBlank()) {
            return BigDecimal.ZERO;
        }
        DiscountCode dc = repository.findByCodeIgnoreCase(code)
                .orElseThrow(() -> new ApiException(ErrorCode.INVALID_DISCOUNT, "Unknown discount code"));
        if (!dc.isActive()) {
            throw new ApiException(ErrorCode.INVALID_DISCOUNT, "Discount code is not active");
        }
        if (dc.getValidFrom() != null && now.isBefore(dc.getValidFrom())) {
            throw new ApiException(ErrorCode.INVALID_DISCOUNT, "Discount code not yet valid");
        }
        if (dc.getValidTo() != null && now.isAfter(dc.getValidTo())) {
            throw new ApiException(ErrorCode.INVALID_DISCOUNT, "Discount code has expired");
        }
        if (dc.getMinAmount() != null && amount.compareTo(dc.getMinAmount()) < 0) {
            throw new ApiException(ErrorCode.INVALID_DISCOUNT,
                    "Order amount below minimum for this discount");
        }
        return rawDiscount(dc, amount);
    }

    /**
     * Lists every active discount that a customer could actually apply to the
     * given order amount right now (validity window + minimum met), each with
     * the discount it would produce. Sorted best-saving first so the UI can
     * surface the most attractive coupon. Read-only; changes nothing.
     */
    @Transactional(readOnly = true)
    public List<Quote> applicableFor(BigDecimal amount, Instant now) {
        return repository.findByActiveTrue().stream()
                .filter(dc -> withinWindow(dc, now) && meetsMinimum(dc, amount))
                .map(dc -> new Quote(dc.getCode(), dc.getType(), dc.getValue(), rawDiscount(dc, amount)))
                .filter(q -> q.discountAmount().signum() > 0)
                .sorted(Comparator.comparing(Quote::discountAmount).reversed())
                .toList();
    }

    private boolean withinWindow(DiscountCode dc, Instant now) {
        if (dc.getValidFrom() != null && now.isBefore(dc.getValidFrom())) {
            return false;
        }
        return dc.getValidTo() == null || !now.isAfter(dc.getValidTo());
    }

    private boolean meetsMinimum(DiscountCode dc, BigDecimal amount) {
        return dc.getMinAmount() == null || amount.compareTo(dc.getMinAmount()) >= 0;
    }

    private BigDecimal rawDiscount(DiscountCode dc, BigDecimal amount) {
        BigDecimal discount;
        if (dc.getType() == DiscountType.PERCENT) {
            discount = amount.multiply(dc.getValue()).divide(BigDecimal.valueOf(100), 2, RoundingMode.HALF_UP);
        } else {
            discount = dc.getValue();
        }
        if (dc.getMaxDiscount() != null && discount.compareTo(dc.getMaxDiscount()) > 0) {
            discount = dc.getMaxDiscount();
        }
        if (discount.compareTo(amount) > 0) {
            discount = amount;
        }
        return discount.setScale(2, RoundingMode.HALF_UP);
    }

    public record Quote(String code, DiscountType type, BigDecimal value, BigDecimal discountAmount) {
    }

    private void apply(DiscountCode code, DiscountCodeDto.Request req) {
        code.setCode(req.code());
        code.setType(req.type());
        code.setValue(req.value());
        code.setMaxDiscount(req.maxDiscount());
        code.setMinAmount(req.minAmount());
        code.setValidFrom(req.validFrom());
        code.setValidTo(req.validTo());
        code.setActive(req.active() == null || req.active());
    }

    private DiscountCodeDto.Response toResponse(DiscountCode c) {
        return new DiscountCodeDto.Response(c.getId(), c.getCode(), c.getType(), c.getValue(),
                c.getMaxDiscount(), c.getMinAmount(), c.getValidFrom(), c.getValidTo(), c.isActive());
    }
}
