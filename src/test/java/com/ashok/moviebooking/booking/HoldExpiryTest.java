package com.ashok.moviebooking.booking;

import com.ashok.moviebooking.domain.Booking;
import com.ashok.moviebooking.domain.BookingStatus;
import com.ashok.moviebooking.domain.Role;
import com.ashok.moviebooking.domain.ShowSeat;
import com.ashok.moviebooking.domain.ShowSeatStatus;
import com.ashok.moviebooking.domain.User;
import com.ashok.moviebooking.dto.booking.BookingResponse;
import com.ashok.moviebooking.dto.show.ShowDto;
import com.ashok.moviebooking.repository.BookingRepository;
import com.ashok.moviebooking.repository.ShowSeatRepository;
import com.ashok.moviebooking.service.BookingService;
import com.ashok.moviebooking.service.ShowService;
import com.ashok.moviebooking.support.IntegrationTest;
import com.ashok.moviebooking.support.TestDataFactory;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.test.context.TestPropertySource;

import java.time.Duration;
import java.time.Instant;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.awaitility.Awaitility.await;

@IntegrationTest
@TestPropertySource(properties = {
        "booking.hold.ttl-seconds=1",
        "booking.hold.sweep-interval-ms=300"
})
class HoldExpiryTest {

    @Autowired
    private BookingService bookingService;
    @Autowired
    private ShowService showService;
    @Autowired
    private ShowSeatRepository showSeatRepository;
    @Autowired
    private BookingRepository bookingRepository;
    @Autowired
    private TestDataFactory dataFactory;

    @Test
    void expiredHoldReleasesSeatAndExpiresBooking() {
        ShowDto.Response show = dataFactory.createShowWithSeats(1);
        Long showSeatId = showService.getSeatMap(show.id()).get(0).showSeatId();
        User user = dataFactory.createUser("expiry-" + System.nanoTime() + "@test.com", Role.CUSTOMER);

        BookingResponse hold = bookingService.hold(show.id(), List.of(showSeatId), user.getId());

        assertThat(showSeatRepository.findById(showSeatId).orElseThrow().getStatus())
                .isEqualTo(ShowSeatStatus.HELD);

        await().atMost(Duration.ofSeconds(15)).untilAsserted(() -> {
            Booking booking = bookingRepository.findById(hold.bookingId()).orElseThrow();
            ShowSeat seat = showSeatRepository.findById(showSeatId).orElseThrow();
            assertThat(booking.getStatus()).isEqualTo(BookingStatus.EXPIRED);
            assertThat(seat.getStatus()).isEqualTo(ShowSeatStatus.AVAILABLE);
        });
    }
}
