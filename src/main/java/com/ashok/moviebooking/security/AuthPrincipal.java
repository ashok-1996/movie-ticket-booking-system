package com.ashok.moviebooking.security;

/** Lightweight authenticated principal carried in the SecurityContext. */
public record AuthPrincipal(Long userId, String email, String role) {
}
