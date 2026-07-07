package com.ashok.moviebooking.repository;

import com.ashok.moviebooking.domain.ShowSeat;
import jakarta.persistence.LockModeType;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Lock;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.Collection;
import java.util.List;

public interface ShowSeatRepository extends JpaRepository<ShowSeat, Long> {

    List<ShowSeat> findByShowIdOrderBySeatIdAsc(Long showId);

    /**
     * Acquires a PESSIMISTIC_WRITE lock (SELECT ... FOR UPDATE) on the requested
     * show seats, ordered deterministically by id to avoid deadlocks when
     * multiple transactions lock overlapping seat sets. This serializes
     * concurrent holds/bookings on the same seat.
     */
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("select ss from ShowSeat ss where ss.id in :ids order by ss.id asc")
    List<ShowSeat> lockByIds(@Param("ids") Collection<Long> ids);
}
