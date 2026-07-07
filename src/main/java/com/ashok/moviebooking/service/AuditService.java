package com.ashok.moviebooking.service;

import com.ashok.moviebooking.domain.AuditEvent;
import com.ashok.moviebooking.repository.AuditEventRepository;
import org.springframework.stereotype.Service;

@Service
public class AuditService {

    private final AuditEventRepository auditEventRepository;

    public AuditService(AuditEventRepository auditEventRepository) {
        this.auditEventRepository = auditEventRepository;
    }

    public void record(String entityType, Long entityId, String action, String details, Long userId) {
        AuditEvent event = new AuditEvent();
        event.setEntityType(entityType);
        event.setEntityId(entityId);
        event.setAction(action);
        event.setDetails(details);
        event.setUserId(userId);
        auditEventRepository.save(event);
    }
}
