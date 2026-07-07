package com.ashok.moviebooking.web;

import com.ashok.moviebooking.domain.Role;
import com.ashok.moviebooking.domain.User;
import com.ashok.moviebooking.dto.auth.RegisterRequest;
import com.ashok.moviebooking.dto.catalog.CityDto;
import com.ashok.moviebooking.security.JwtService;
import com.ashok.moviebooking.support.IntegrationTest;
import com.ashok.moviebooking.support.TestDataFactory;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@IntegrationTest
@AutoConfigureMockMvc
class RbacAndValidationTest {

    @Autowired
    private MockMvc mockMvc;
    @Autowired
    private ObjectMapper objectMapper;
    @Autowired
    private JwtService jwtService;
    @Autowired
    private TestDataFactory dataFactory;

    @Test
    void registrationRejectsInvalidEmail() throws Exception {
        RegisterRequest bad = new RegisterRequest("not-an-email", "short", "");
        mockMvc.perform(post("/auth/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(bad)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.code").value("VALIDATION_ERROR"))
                .andExpect(jsonPath("$.fieldErrors").isArray());
    }

    @Test
    void adminEndpointRequiresAuthentication() throws Exception {
        mockMvc.perform(get("/admin/cities"))
                .andExpect(status().isUnauthorized())
                .andExpect(jsonPath("$.code").value("UNAUTHORIZED"));
    }

    @Test
    void adminEndpointForbiddenForCustomer() throws Exception {
        User customer = dataFactory.createUser("cust-" + System.nanoTime() + "@test.com", Role.CUSTOMER);
        String token = jwtService.generateToken(customer);
        mockMvc.perform(get("/admin/cities").header("Authorization", "Bearer " + token))
                .andExpect(status().isForbidden())
                .andExpect(jsonPath("$.code").value("FORBIDDEN"));
    }

    @Test
    void adminCanCreateCity() throws Exception {
        User admin = dataFactory.createUser("admin-" + System.nanoTime() + "@test.com", Role.ADMIN);
        String token = jwtService.generateToken(admin);
        CityDto.Request req = new CityDto.Request("Mumbai-" + System.nanoTime(), "Maharashtra");
        mockMvc.perform(post("/admin/cities")
                        .header("Authorization", "Bearer " + token)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(req)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.id").isNumber());
    }

    @Test
    void publicCanBrowseShows() throws Exception {
        mockMvc.perform(get("/shows"))
                .andExpect(status().isOk());
    }
}
