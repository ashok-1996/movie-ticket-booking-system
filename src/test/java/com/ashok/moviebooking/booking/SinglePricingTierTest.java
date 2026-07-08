package com.ashok.moviebooking.booking;

import com.ashok.moviebooking.common.ApiException;
import com.ashok.moviebooking.common.ErrorCode;
import com.ashok.moviebooking.domain.BookingStatus;
import com.ashok.moviebooking.domain.Role;
import com.ashok.moviebooking.domain.SeatClass;
import com.ashok.moviebooking.domain.User;
import com.ashok.moviebooking.dto.booking.BookingResponse;
import com.ashok.moviebooking.dto.show.ShowDto;
import com.ashok.moviebooking.service.BookingService;
import com.ashok.moviebooking.service.ShowService;
import com.ashok.moviebooking.support.IntegrationTest;
import com.ashok.moviebooking.support.TestDataFactory;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

@IntegrationTest
class SinglePricingTierTest {

    @Autowired
    private BookingService bookingService;
    @Autowired
    private ShowService showService;
    @Autowired
    private TestDataFactory dataFactory;

    @Test
    void holdSpanningMultiplePricingTiersIsRejected() {
        ShowDto.Response show = dataFactory.createShowWithMixedClasses(3, 3);
        List<ShowDto.SeatView> seats = showService.getSeatMap(show.id());
        Long regularSeat = pick(seats, SeatClass.REGULAR);
        Long premiumSeat = pick(seats, SeatClass.PREMIUM);
        User user = dataFactory.createUser("tier-" + System.nanoTime() + "@test.com", Role.CUSTOMER);

        assertThatThrownBy(() -> bookingService.hold(show.id(), List.of(regularSeat, premiumSeat), user.getId()))
                .isInstanceOf(ApiException.class)
                .extracting(e -> ((ApiException) e).getCode())
                .isEqualTo(ErrorCode.VALIDATION_ERROR);
    }

    @Test
    void holdWithinASinglePricingTierSucceeds() {
        ShowDto.Response show = dataFactory.createShowWithMixedClasses(3, 3);
        List<ShowDto.SeatView> seats = showService.getSeatMap(show.id());
        List<Long> twoPremium = seats.stream()
                .filter(s -> s.seatClass() == SeatClass.PREMIUM)
                .map(ShowDto.SeatView::showSeatId)
                .limit(2)
                .toList();
        User user = dataFactory.createUser("tier2-" + System.nanoTime() + "@test.com", Role.CUSTOMER);

        BookingResponse hold = bookingService.hold(show.id(), twoPremium, user.getId());
        assertThat(hold.status()).isEqualTo(BookingStatus.PENDING);
        assertThat(hold.seats()).hasSize(2);
    }

    private Long pick(List<ShowDto.SeatView> seats, SeatClass cls) {
        return seats.stream().filter(s -> s.seatClass() == cls)
                .map(ShowDto.SeatView::showSeatId).findFirst().orElseThrow();
    }
}
