package com.ashok.moviebooking.support;

import com.ashok.moviebooking.domain.Role;
import com.ashok.moviebooking.domain.User;
import com.ashok.moviebooking.dto.catalog.*;
import com.ashok.moviebooking.dto.show.ShowDto;
import com.ashok.moviebooking.repository.UserRepository;
import com.ashok.moviebooking.service.CatalogService;
import com.ashok.moviebooking.service.ShowService;
import com.ashok.moviebooking.domain.SeatClass;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.List;

@Component
public class TestDataFactory {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final CatalogService catalogService;
    private final ShowService showService;

    public TestDataFactory(UserRepository userRepository, PasswordEncoder passwordEncoder,
                           CatalogService catalogService, ShowService showService) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.catalogService = catalogService;
        this.showService = showService;
    }

    public User createUser(String email, Role role) {
        User user = new User();
        user.setEmail(email);
        user.setPassword(passwordEncoder.encode("password123"));
        user.setFullName(email);
        user.setRole(role);
        return userRepository.save(user);
    }

    /** Creates a show with the given number of REGULAR seats in a single row and returns it. */
    public ShowDto.Response createShowWithSeats(int seatCount) {
        CityDto.Response city = catalogService.createCity(new CityDto.Request("City-" + unique(), "State"));
        TheaterDto.Response theater = catalogService.createTheater(
                new TheaterDto.Request("Theater", "Addr", city.id()));
        ScreenDto.Response screen = catalogService.createScreen(new ScreenDto.Request("Screen", theater.id()));
        catalogService.createSeatLayout(screen.id(), new SeatDto.LayoutRequest(List.of(
                new SeatDto.RowSpec("A", seatCount, SeatClass.REGULAR))));
        MovieDto.Response movie = catalogService.createMovie(
                new MovieDto.Request("Movie", "English", "Drama", 120, "UA"));
        Instant start = Instant.now().plus(10, ChronoUnit.DAYS).truncatedTo(ChronoUnit.HOURS);
        return showService.createShow(new ShowDto.Request(movie.id(), screen.id(), start, new BigDecimal("100.00")));
    }

    /**
     * Creates a show with two seat classes: row A REGULAR and row B PREMIUM,
     * for verifying the single-pricing-tier-per-booking rule.
     */
    public ShowDto.Response createShowWithMixedClasses(int regularCount, int premiumCount) {
        CityDto.Response city = catalogService.createCity(new CityDto.Request("City-" + unique(), "State"));
        TheaterDto.Response theater = catalogService.createTheater(
                new TheaterDto.Request("Theater", "Addr", city.id()));
        ScreenDto.Response screen = catalogService.createScreen(new ScreenDto.Request("Screen", theater.id()));
        catalogService.createSeatLayout(screen.id(), new SeatDto.LayoutRequest(List.of(
                new SeatDto.RowSpec("A", regularCount, SeatClass.REGULAR),
                new SeatDto.RowSpec("B", premiumCount, SeatClass.PREMIUM))));
        MovieDto.Response movie = catalogService.createMovie(
                new MovieDto.Request("Movie", "English", "Drama", 120, "UA"));
        Instant start = Instant.now().plus(10, ChronoUnit.DAYS).truncatedTo(ChronoUnit.HOURS);
        return showService.createShow(new ShowDto.Request(movie.id(), screen.id(), start, new BigDecimal("100.00")));
    }

    private String unique() {
        return Long.toString(System.nanoTime());
    }
}
