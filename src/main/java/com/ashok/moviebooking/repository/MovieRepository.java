package com.ashok.moviebooking.repository;

import com.ashok.moviebooking.domain.Movie;
import org.springframework.data.jpa.repository.JpaRepository;

public interface MovieRepository extends JpaRepository<Movie, Long> {
}
