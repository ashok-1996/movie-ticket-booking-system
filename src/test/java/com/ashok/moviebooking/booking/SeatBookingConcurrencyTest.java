package com.ashok.moviebooking.booking;

import com.ashok.moviebooking.domain.BookingStatus;
import com.ashok.moviebooking.domain.Role;
import com.ashok.moviebooking.domain.ShowSeat;
import com.ashok.moviebooking.domain.ShowSeatStatus;
import com.ashok.moviebooking.domain.User;
import com.ashok.moviebooking.dto.booking.BookingResponse;
import com.ashok.moviebooking.dto.booking.ConfirmRequest;
import com.ashok.moviebooking.dto.show.ShowDto;
import com.ashok.moviebooking.repository.BookingRepository;
import com.ashok.moviebooking.repository.ShowSeatRepository;
import com.ashok.moviebooking.service.BookingService;
import com.ashok.moviebooking.service.ShowService;
import com.ashok.moviebooking.support.IntegrationTest;
import com.ashok.moviebooking.support.TestDataFactory;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

import static org.assertj.core.api.Assertions.assertThat;

@IntegrationTest
class SeatBookingConcurrencyTest {

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

    /**
     * The money test: N threads race to book the SAME seat. Exactly one must win;
     * every other attempt must be rejected and the seat must never be sold twice.
     */
    @Test
    void onlyOneThreadCanBookTheSameSeat() throws InterruptedException {
        int threads = 20;
        ShowDto.Response show = dataFactory.createShowWithSeats(1);
        Long showId = show.id();
        Long showSeatId = showService.getSeatMap(showId).get(0).showSeatId();

        List<User> users = new ArrayList<>();
        for (int i = 0; i < threads; i++) {
            users.add(dataFactory.createUser("racer" + i + "-" + System.nanoTime() + "@test.com", Role.CUSTOMER));
        }

        ExecutorService pool = Executors.newFixedThreadPool(threads);
        CountDownLatch ready = new CountDownLatch(threads);
        CountDownLatch start = new CountDownLatch(1);
        CountDownLatch done = new CountDownLatch(threads);
        AtomicInteger confirmed = new AtomicInteger();
        AtomicInteger rejected = new AtomicInteger();

        for (int i = 0; i < threads; i++) {
            Long userId = users.get(i).getId();
            pool.submit(() -> {
                ready.countDown();
                try {
                    start.await();
                    BookingResponse hold = bookingService.hold(showId, List.of(showSeatId), userId);
                    BookingResponse booking = bookingService.confirm(hold.bookingId(), new ConfirmRequest(null, "MOCK"), userId);
                    if (booking.status() == BookingStatus.CONFIRMED) {
                        confirmed.incrementAndGet();
                    }
                } catch (RuntimeException ex) {
                    rejected.incrementAndGet();
                } finally {
                    done.countDown();
                }
                return null;
            });
        }

        ready.await(10, TimeUnit.SECONDS);
        start.countDown();
        assertThat(done.await(60, TimeUnit.SECONDS)).isTrue();
        pool.shutdownNow();

        assertThat(confirmed.get()).as("exactly one booking should succeed").isEqualTo(1);
        assertThat(rejected.get()).as("all other attempts should be rejected").isEqualTo(threads - 1);

        ShowSeat seat = showSeatRepository.findById(showSeatId).orElseThrow();
        assertThat(seat.getStatus()).isEqualTo(ShowSeatStatus.BOOKED);

        long confirmedBookings = bookingRepository.findAll().stream()
                .filter(b -> b.getStatus() == BookingStatus.CONFIRMED)
                .count();
        assertThat(confirmedBookings).as("no oversell").isEqualTo(1);
    }
}
