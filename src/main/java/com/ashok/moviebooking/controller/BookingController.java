package com.ashok.moviebooking.controller;

import com.ashok.moviebooking.dto.booking.BookingResponse;
import com.ashok.moviebooking.dto.booking.ConfirmRequest;
import com.ashok.moviebooking.dto.booking.DiscountOptionsResponse;
import com.ashok.moviebooking.dto.booking.HoldRequest;
import com.ashok.moviebooking.security.CurrentUser;
import com.ashok.moviebooking.service.BookingService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@PreAuthorize("hasRole('CUSTOMER')")
public class BookingController {

    private final BookingService bookingService;

    public BookingController(BookingService bookingService) {
        this.bookingService = bookingService;
    }

    @PostMapping("/shows/{showId}/holds")
    public ResponseEntity<BookingResponse> hold(@PathVariable Long showId,
                                                @Valid @RequestBody HoldRequest req) {
        BookingResponse response = bookingService.hold(showId, req.showSeatIds(), CurrentUser.id());
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    @GetMapping("/bookings/{bookingId}/discounts")
    public DiscountOptionsResponse availableDiscounts(@PathVariable Long bookingId) {
        return bookingService.availableDiscounts(bookingId, CurrentUser.id());
    }

    @PostMapping("/bookings/{bookingId}/confirm")
    public BookingResponse confirm(@PathVariable Long bookingId, @RequestBody(required = false) ConfirmRequest req) {
        return bookingService.confirm(bookingId, req, CurrentUser.id());
    }

    @PostMapping("/bookings/{bookingId}/cancel")
    public BookingResponse cancel(@PathVariable Long bookingId) {
        return bookingService.cancel(bookingId, CurrentUser.id());
    }

    @GetMapping("/bookings/me")
    public List<BookingResponse> myBookings() {
        return bookingService.myBookings(CurrentUser.id());
    }

    @GetMapping("/bookings/{bookingId}")
    public BookingResponse getBooking(@PathVariable Long bookingId) {
        return bookingService.getBooking(bookingId, CurrentUser.id());
    }
}
