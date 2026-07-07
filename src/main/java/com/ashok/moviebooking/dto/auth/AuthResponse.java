package com.ashok.moviebooking.dto.auth;

public record AuthResponse(String token, String email, String role, String fullName) {
}
