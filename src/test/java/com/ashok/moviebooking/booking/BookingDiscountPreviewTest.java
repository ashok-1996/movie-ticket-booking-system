package com.ashok.moviebooking.booking;

import com.ashok.moviebooking.common.ApiException;
import com.ashok.moviebooking.common.ErrorCode;
import com.ashok.moviebooking.domain.DiscountType;
import com.ashok.moviebooking.domain.Role;
import com.ashok.moviebooking.domain.User;
import com.ashok.moviebooking.dto.booking.BookingResponse;
import com.ashok.moviebooking.dto.booking.ConfirmRequest;
import com.ashok.moviebooking.dto.booking.DiscountOptionsResponse;
import com.ashok.moviebooking.dto.discount.DiscountCodeDto;
import com.ashok.moviebooking.dto.show.ShowDto;
import com.ashok.moviebooking.service.BookingService;
import com.ashok.moviebooking.service.DiscountService;
import com.ashok.moviebooking.service.ShowService;
import com.ashok.moviebooking.support.IntegrationTest;
import com.ashok.moviebooking.support.TestDataFactory;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;

import java.math.BigDecimal;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

@IntegrationTest
class BookingDiscountPreviewTest {

    @Autowired
    private BookingService bookingService;
    @Autowired
    private ShowService showService;
    @Autowired
    private DiscountService discountService;
    @Autowired
    private TestDataFactory dataFactory;

    @Test
    void previewListsOnlyApplicableCouponsWithComputedPrice() {
        // Order total = 4 x 100.00 = 400.00
        ShowDto.Response show = dataFactory.createShowWithSeats(4);
        List<Long> seatIds = showService.getSeatMap(show.id()).stream().map(ShowDto.SeatView::showSeatId).toList();
        User user = dataFactory.createUser("disc-" + System.nanoTime() + "@test.com", Role.CUSTOMER);

        // Eligible: 20% capped at 100, min 300 -> 80.00 off, final 320.00
        discountService.create(new DiscountCodeDto.Request(
                "SAVE20", DiscountType.PERCENT, new BigDecimal("20"),
                new BigDecimal("100"), new BigDecimal("300"), null, null, true));
        // Not eligible: minimum 1000 exceeds the 400.00 order
        discountService.create(new DiscountCodeDto.Request(
                "BIGSPENDER", DiscountType.FLAT, new BigDecimal("150"),
                null, new BigDecimal("1000"), null, null, true));

        BookingResponse hold = bookingService.hold(show.id(), seatIds, user.getId());

        DiscountOptionsResponse preview = bookingService.availableDiscounts(hold.bookingId(), user.getId());

        assertThat(preview.totalAmount()).isEqualByComparingTo("400.00");
        assertThat(preview.options()).hasSize(1);
        DiscountOptionsResponse.Option option = preview.options().get(0);
        assertThat(option.code()).isEqualTo("SAVE20");
        assertThat(option.discountAmount()).isEqualByComparingTo("80.00");
        assertThat(option.finalAmount()).isEqualByComparingTo("320.00");
    }

    @Test
    void previewIsRejectedOnceBookingIsNoLongerPending() {
        ShowDto.Response show = dataFactory.createShowWithSeats(2);
        List<Long> seatIds = showService.getSeatMap(show.id()).stream().map(ShowDto.SeatView::showSeatId).toList();
        User user = dataFactory.createUser("disc2-" + System.nanoTime() + "@test.com", Role.CUSTOMER);

        BookingResponse hold = bookingService.hold(show.id(), seatIds, user.getId());
        bookingService.confirm(hold.bookingId(), new ConfirmRequest(null, "CARD"), user.getId());

        assertThatThrownBy(() -> bookingService.availableDiscounts(hold.bookingId(), user.getId()))
                .isInstanceOf(ApiException.class)
                .extracting(e -> ((ApiException) e).getCode())
                .isEqualTo(ErrorCode.CONFLICT);
    }
}
