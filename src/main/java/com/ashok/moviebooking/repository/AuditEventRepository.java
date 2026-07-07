package com.ashok.moviebooking.repository;

import com.ashok.moviebooking.domain.AuditEvent;
import org.springframework.data.jpa.repository.JpaRepository;

public interface AuditEventRepository extends JpaRepository<AuditEvent, Long> {
}
