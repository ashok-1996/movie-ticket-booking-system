package com.ashok.moviebooking.service;

import com.ashok.moviebooking.common.ApiException;
import com.ashok.moviebooking.domain.*;
import com.ashok.moviebooking.dto.show.ShowDto;
import com.ashok.moviebooking.repository.*;
import jakarta.persistence.criteria.Predicate;
import org.springframework.data.domain.Sort;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.List;

@Service
public class ShowService {

    private final ShowRepository showRepository;
    private final MovieRepository movieRepository;
    private final ScreenRepository screenRepository;
    private final SeatRepository seatRepository;
    private final ShowSeatRepository showSeatRepository;
    private final PricingService pricingService;

    public ShowService(ShowRepository showRepository, MovieRepository movieRepository,
                       ScreenRepository screenRepository, SeatRepository seatRepository,
                       ShowSeatRepository showSeatRepository, PricingService pricingService) {
        this.showRepository = showRepository;
        this.movieRepository = movieRepository;
        this.screenRepository = screenRepository;
        this.seatRepository = seatRepository;
        this.showSeatRepository = showSeatRepository;
        this.pricingService = pricingService;
    }

    /**
     * Creates a show and materializes a ShowSeat (with resolved price) for every
     * physical seat in the screen. End time is derived from the movie duration.
     */
    @Transactional
    public ShowDto.Response createShow(ShowDto.Request req) {
        Movie movie = movieRepository.findById(req.movieId())
                .orElseThrow(() -> ApiException.notFound("Movie"));
        Screen screen = screenRepository.findById(req.screenId())
                .orElseThrow(() -> ApiException.notFound("Screen"));

        Show show = new Show();
        show.setMovie(movie);
        show.setScreen(screen);
        show.setStartTime(req.startTime());
        show.setEndTime(req.startTime().plus(movie.getDurationMinutes(), ChronoUnit.MINUTES));
        show.setBasePrice(req.basePrice());
        Show saved = showRepository.save(show);

        List<Seat> seats = seatRepository.findByScreenIdOrderByRowLabelAscSeatNumberAsc(screen.getId());
        for (Seat seat : seats) {
            ShowSeat showSeat = new ShowSeat();
            showSeat.setShow(saved);
            showSeat.setSeat(seat);
            showSeat.setStatus(ShowSeatStatus.AVAILABLE);
            showSeat.setPrice(pricingService.computeSeatPrice(req.basePrice(), seat.getSeatClass(), req.startTime()));
            showSeatRepository.save(showSeat);
        }
        return toResponse(saved);
    }

    @Transactional(readOnly = true)
    public List<ShowDto.Response> search(Long cityId, Long movieId, Instant from, Instant to) {
        Specification<Show> spec = (root, query, cb) -> {
            List<Predicate> predicates = new ArrayList<>();
            if (cityId != null) {
                predicates.add(cb.equal(root.get("screen").get("theater").get("city").get("id"), cityId));
            }
            if (movieId != null) {
                predicates.add(cb.equal(root.get("movie").get("id"), movieId));
            }
            if (from != null) {
                predicates.add(cb.greaterThanOrEqualTo(root.get("startTime"), from));
            }
            if (to != null) {
                predicates.add(cb.lessThan(root.get("startTime"), to));
            }
            return cb.and(predicates.toArray(new Predicate[0]));
        };
        return showRepository.findAll(spec, Sort.by(Sort.Direction.ASC, "startTime")).stream()
                .map(this::toResponse).toList();
    }

    @Transactional(readOnly = true)
    public ShowDto.Response get(Long showId) {
        return toResponse(showRepository.findById(showId).orElseThrow(() -> ApiException.notFound("Show")));
    }

    @Transactional(readOnly = true)
    public List<ShowDto.SeatView> getSeatMap(Long showId) {
        if (!showRepository.existsById(showId)) {
            throw ApiException.notFound("Show");
        }
        return showSeatRepository.findByShowIdOrderBySeatIdAsc(showId).stream()
                .map(ss -> new ShowDto.SeatView(
                        ss.getId(),
                        ss.getSeat().getRowLabel(),
                        ss.getSeat().getSeatNumber(),
                        ss.getSeat().getSeatClass(),
                        ss.getStatus(),
                        ss.getPrice()))
                .toList();
    }

    private ShowDto.Response toResponse(Show s) {
        Screen screen = s.getScreen();
        Theater theater = screen.getTheater();
        return new ShowDto.Response(
                s.getId(),
                s.getMovie().getId(),
                s.getMovie().getTitle(),
                screen.getId(),
                screen.getName(),
                theater.getName(),
                theater.getCity().getName(),
                s.getStartTime(),
                s.getEndTime(),
                s.getBasePrice());
    }
}
