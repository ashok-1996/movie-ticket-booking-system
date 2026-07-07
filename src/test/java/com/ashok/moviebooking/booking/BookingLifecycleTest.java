package com.ashok.moviebooking.booking;

import com.ashok.moviebooking.domain.BookingStatus;
import com.ashok.moviebooking.domain.PaymentStatus;
import com.ashok.moviebooking.domain.Role;
import com.ashok.moviebooking.domain.ShowSeatStatus;
import com.ashok.moviebooking.domain.User;
import com.ashok.moviebooking.dto.booking.BookingResponse;
import com.ashok.moviebooking.dto.booking.ConfirmRequest;
import com.ashok.moviebooking.dto.show.ShowDto;
import com.ashok.moviebooking.repository.PaymentRepository;
import com.ashok.moviebooking.repository.ShowSeatRepository;
import com.ashok.moviebooking.service.BookingService;
import com.ashok.moviebooking.service.ShowService;
import com.ashok.moviebooking.support.IntegrationTest;
import com.ashok.moviebooking.support.TestDataFactory;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;

@IntegrationTest
class BookingLifecycleTest {

    @Autowired
    private BookingService bookingService;
    @Autowired
    private ShowService showService;
    @Autowired
    private ShowSeatRepository showSeatRepository;
    @Autowired
    private PaymentRepository paymentRepository;
    @Autowired
    private TestDataFactory dataFactory;

    @Test
    void confirmThenCancelIssuesFullRefundAndReleasesSeat() {
        ShowDto.Response show = dataFactory.createShowWithSeats(3);
        List<ShowDto.SeatView> seatMap = showService.getSeatMap(show.id());
        Long seatId = seatMap.get(0).showSeatId();
        User user = dataFactory.createUser("life-" + System.nanoTime() + "@test.com", Role.CUSTOMER);

        BookingResponse hold = bookingService.hold(show.id(), List.of(seatId), user.getId());
        assertThat(hold.status()).isEqualTo(BookingStatus.PENDING);
        assertThat(hold.totalAmount()).isEqualByComparingTo("100.00");

        BookingResponse confirmed = bookingService.confirm(hold.bookingId(), new ConfirmRequest(null, "CARD"), user.getId());
        assertThat(confirmed.status()).isEqualTo(BookingStatus.CONFIRMED);
        assertThat(confirmed.finalAmount()).isEqualByComparingTo("100.00");
        assertThat(showSeatRepository.findById(seatId).orElseThrow().getStatus()).isEqualTo(ShowSeatStatus.BOOKED);
        assertThat(paymentRepository.findByBookingId(confirmed.bookingId()).orElseThrow().getStatus())
                .isEqualTo(PaymentStatus.SUCCESS);

        // Show starts 10 days out -> full refund per standard policy (>= 24h).
        BookingResponse cancelled = bookingService.cancel(confirmed.bookingId(), user.getId());
        assertThat(cancelled.status()).isEqualTo(BookingStatus.REFUNDED);
        assertThat(cancelled.refundAmount()).isEqualByComparingTo("100.00");
        assertThat(showSeatRepository.findById(seatId).orElseThrow().getStatus()).isEqualTo(ShowSeatStatus.AVAILABLE);
        assertThat(paymentRepository.findByBookingId(confirmed.bookingId()).orElseThrow().getStatus())
                .isEqualTo(PaymentStatus.REFUNDED);

        // Released seat can be re-held (partial unique index allows re-allocation).
        User user2 = dataFactory.createUser("life2-" + System.nanoTime() + "@test.com", Role.CUSTOMER);
        BookingResponse rehold = bookingService.hold(show.id(), List.of(seatId), user2.getId());
        assertThat(rehold.status()).isEqualTo(BookingStatus.PENDING);
    }
}
