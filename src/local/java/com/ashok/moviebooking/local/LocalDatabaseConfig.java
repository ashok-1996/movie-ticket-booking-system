package com.ashok.moviebooking.local;

import io.zonky.test.db.postgres.embedded.EmbeddedPostgres;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;
import org.springframework.context.annotation.Profile;

import javax.sql.DataSource;
import java.io.IOException;

/**
 * Dev-only datasource for running the app without Docker or a local PostgreSQL
 * install. Boots the same real PostgreSQL binaries the integration tests use
 * (Zonky embedded), entirely in-process and offline. Active only under the
 * {@code local} Spring profile and compiled only under the Maven {@code local}
 * profile, so it never touches the production build.
 */
@Configuration
@Profile("local")
public class LocalDatabaseConfig {

    @Bean(destroyMethod = "close")
    public EmbeddedPostgres embeddedPostgres() throws IOException {
        return EmbeddedPostgres.builder().start();
    }

    @Bean
    @Primary
    public DataSource dataSource(EmbeddedPostgres embeddedPostgres) {
        return embeddedPostgres.getPostgresDatabase();
    }
}
