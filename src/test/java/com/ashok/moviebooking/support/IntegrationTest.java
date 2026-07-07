package com.ashok.moviebooking.support;

import io.zonky.test.db.AutoConfigureEmbeddedDatabase;
import org.springframework.boot.test.context.SpringBootTest;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

import static io.zonky.test.db.AutoConfigureEmbeddedDatabase.DatabaseProvider.ZONKY;

/**
 * Runs integration tests against a real, embedded PostgreSQL (via Zonky, no
 * Docker daemon required) so pessimistic locking and the partial unique index
 * behave exactly as in production.
 */
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@SpringBootTest
@AutoConfigureEmbeddedDatabase(provider = ZONKY)
public @interface IntegrationTest {
}
