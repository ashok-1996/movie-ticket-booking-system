package com.ashok.moviebooking.config;

import com.ashok.moviebooking.domain.DiscountType;
import com.ashok.moviebooking.domain.Role;
import com.ashok.moviebooking.domain.SeatClass;
import com.ashok.moviebooking.domain.User;
import com.ashok.moviebooking.dto.catalog.*;
import com.ashok.moviebooking.dto.discount.DiscountCodeDto;
import com.ashok.moviebooking.dto.show.ShowDto;
import com.ashok.moviebooking.repository.UserRepository;
import com.ashok.moviebooking.service.CatalogService;
import com.ashok.moviebooking.service.DiscountService;
import com.ashok.moviebooking.service.ShowService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.List;

/** Seeds demo users and a runnable catalog on first startup. Disable with demo.seed=false. */
@Component
@ConditionalOnProperty(name = "demo.seed", havingValue = "true", matchIfMissing = true)
public class DataSeeder implements CommandLineRunner {

    private static final Logger log = LoggerFactory.getLogger(DataSeeder.class);

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final CatalogService catalogService;
    private final ShowService showService;
    private final DiscountService discountService;

    public DataSeeder(UserRepository userRepository, PasswordEncoder passwordEncoder,
                      CatalogService catalogService, ShowService showService, DiscountService discountService) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.catalogService = catalogService;
        this.showService = showService;
        this.discountService = discountService;
    }

    @Override
    public void run(String... args) {
        if (userRepository.count() > 0) {
            return;
        }
        createUser("admin@movies.test", "admin123", "Platform Admin", Role.ADMIN);
        createUser("customer@movies.test", "customer123", "Demo Customer", Role.CUSTOMER);

        CityDto.Response city = catalogService.createCity(new CityDto.Request("Bengaluru", "Karnataka"));
        TheaterDto.Response theater = catalogService.createTheater(
                new TheaterDto.Request("PVR Forum Mall", "Koramangala", city.id()));
        ScreenDto.Response screen = catalogService.createScreen(new ScreenDto.Request("Audi 1", theater.id()));
        catalogService.createSeatLayout(screen.id(), new SeatDto.LayoutRequest(List.of(
                new SeatDto.RowSpec("A", 10, SeatClass.REGULAR),
                new SeatDto.RowSpec("B", 8, SeatClass.PREMIUM),
                new SeatDto.RowSpec("C", 6, SeatClass.RECLINER))));
        MovieDto.Response movie = catalogService.createMovie(
                new MovieDto.Request("Inception", "English", "Sci-Fi", 148, "UA"));

        Instant start = Instant.now().plus(3, ChronoUnit.DAYS).truncatedTo(ChronoUnit.HOURS);
        showService.createShow(new ShowDto.Request(movie.id(), screen.id(), start, new BigDecimal("200.00")));

        discountService.create(new DiscountCodeDto.Request(
                "SAVE20", DiscountType.PERCENT, new BigDecimal("20"),
                new BigDecimal("100"), new BigDecimal("300"), null, null, true));

        log.info("Demo data seeded. Admin: admin@movies.test/admin123  Customer: customer@movies.test/customer123");
    }

    private void createUser(String email, String rawPassword, String name, Role role) {
        User user = new User();
        user.setEmail(email);
        user.setPassword(passwordEncoder.encode(rawPassword));
        user.setFullName(name);
        user.setRole(role);
        userRepository.save(user);
    }
}
