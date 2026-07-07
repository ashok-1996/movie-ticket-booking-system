package com.ashok.moviebooking.service;

import com.ashok.moviebooking.common.ApiException;
import com.ashok.moviebooking.common.ErrorCode;
import com.ashok.moviebooking.domain.*;
import com.ashok.moviebooking.dto.catalog.*;
import com.ashok.moviebooking.repository.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class CatalogService {

    private final CityRepository cityRepository;
    private final TheaterRepository theaterRepository;
    private final ScreenRepository screenRepository;
    private final SeatRepository seatRepository;
    private final MovieRepository movieRepository;

    public CatalogService(CityRepository cityRepository, TheaterRepository theaterRepository,
                          ScreenRepository screenRepository, SeatRepository seatRepository,
                          MovieRepository movieRepository) {
        this.cityRepository = cityRepository;
        this.theaterRepository = theaterRepository;
        this.screenRepository = screenRepository;
        this.seatRepository = seatRepository;
        this.movieRepository = movieRepository;
    }

    // ---- Cities ----
    @Transactional
    public CityDto.Response createCity(CityDto.Request req) {
        if (cityRepository.existsByNameIgnoreCase(req.name())) {
            throw new ApiException(ErrorCode.CONFLICT, "City already exists: " + req.name());
        }
        City city = new City();
        city.setName(req.name());
        city.setState(req.state());
        return toCity(cityRepository.save(city));
    }

    @Transactional(readOnly = true)
    public List<CityDto.Response> listCities() {
        return cityRepository.findAll().stream().map(this::toCity).toList();
    }

    // ---- Theaters ----
    @Transactional
    public TheaterDto.Response createTheater(TheaterDto.Request req) {
        City city = cityRepository.findById(req.cityId())
                .orElseThrow(() -> ApiException.notFound("City"));
        Theater theater = new Theater();
        theater.setName(req.name());
        theater.setAddress(req.address());
        theater.setCity(city);
        return toTheater(theaterRepository.save(theater));
    }

    @Transactional(readOnly = true)
    public List<TheaterDto.Response> listTheaters(Long cityId) {
        List<Theater> theaters = cityId == null ? theaterRepository.findAll() : theaterRepository.findByCityId(cityId);
        return theaters.stream().map(this::toTheater).toList();
    }

    // ---- Screens ----
    @Transactional
    public ScreenDto.Response createScreen(ScreenDto.Request req) {
        Theater theater = theaterRepository.findById(req.theaterId())
                .orElseThrow(() -> ApiException.notFound("Theater"));
        Screen screen = new Screen();
        screen.setName(req.name());
        screen.setTheater(theater);
        return toScreen(screenRepository.save(screen));
    }

    // ---- Seat layout ----
    @Transactional
    public List<SeatDto.Response> createSeatLayout(Long screenId, SeatDto.LayoutRequest req) {
        Screen screen = screenRepository.findById(screenId)
                .orElseThrow(() -> ApiException.notFound("Screen"));
        for (SeatDto.RowSpec row : req.rows()) {
            for (int n = 1; n <= row.seatCount(); n++) {
                Seat seat = new Seat();
                seat.setScreen(screen);
                seat.setRowLabel(row.rowLabel());
                seat.setSeatNumber(n);
                seat.setSeatClass(row.seatClass());
                seatRepository.save(seat);
            }
        }
        return listSeats(screenId);
    }

    @Transactional(readOnly = true)
    public List<SeatDto.Response> listSeats(Long screenId) {
        return seatRepository.findByScreenIdOrderByRowLabelAscSeatNumberAsc(screenId).stream()
                .map(s -> new SeatDto.Response(s.getId(), s.getRowLabel(), s.getSeatNumber(), s.getSeatClass()))
                .toList();
    }

    // ---- Movies ----
    @Transactional
    public MovieDto.Response createMovie(MovieDto.Request req) {
        Movie movie = new Movie();
        movie.setTitle(req.title());
        movie.setLanguage(req.language());
        movie.setGenre(req.genre());
        movie.setDurationMinutes(req.durationMinutes());
        movie.setCertification(req.certification());
        return toMovie(movieRepository.save(movie));
    }

    @Transactional(readOnly = true)
    public List<MovieDto.Response> listMovies() {
        return movieRepository.findAll().stream().map(this::toMovie).toList();
    }

    private CityDto.Response toCity(City c) {
        return new CityDto.Response(c.getId(), c.getName(), c.getState());
    }

    private TheaterDto.Response toTheater(Theater t) {
        return new TheaterDto.Response(t.getId(), t.getName(), t.getAddress(), t.getCity().getId(), t.getCity().getName());
    }

    private ScreenDto.Response toScreen(Screen s) {
        return new ScreenDto.Response(s.getId(), s.getName(), s.getTheater().getId(), s.getTheater().getName());
    }

    private MovieDto.Response toMovie(Movie m) {
        return new MovieDto.Response(m.getId(), m.getTitle(), m.getLanguage(), m.getGenre(), m.getDurationMinutes(), m.getCertification());
    }
}
