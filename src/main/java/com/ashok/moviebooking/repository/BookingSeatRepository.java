package com.ashok.moviebooking.repository;

import com.ashok.moviebooking.domain.BookingSeat;
import org.springframework.data.jpa.repository.JpaRepository;

public interface BookingSeatRepository extends JpaRepository<BookingSeat, Long> {
}
