package com.grocerystore.billing.config;

import com.grocerystore.billing.entity.User;
import com.grocerystore.billing.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

/**
 * Data Initializer
 * Creates default users on application startup
 */
@Component
@RequiredArgsConstructor
@Slf4j
public class DataInitializer implements CommandLineRunner {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    @Override
    public void run(String... args) throws Exception {
        log.info("Initializing default users...");

        // Create Admin User
        createUserIfNotExists("admin", "admin123", "Admin", "User", User.UserRole.ADMIN);

        // Create Cashier User
        createUserIfNotExists("cashier1", "cashier123", "Cashier", "One", User.UserRole.CASHIER);

        // Create Manager User
        createUserIfNotExists("manager1", "manager123", "Manager", "One", User.UserRole.MANAGER);

        // Create Inventory Manager User
        createUserIfNotExists("inventory1", "inventory123", "Inventory", "Manager", User.UserRole.INVENTORY_MANAGER);

        // Create Accountant User
        createUserIfNotExists("accountant1", "accountant123", "Accountant", "One", User.UserRole.ACCOUNTANT);

        log.info("Default users initialization completed");
    }

    private void createUserIfNotExists(String username, String password, String firstName, String lastName, User.UserRole role) {
        if (userRepository.findByUsername(username).isEmpty()) {
            User user = User.builder()
                    .username(username)
                    .passwordHash(passwordEncoder.encode(password))
                    .email(username + "@grocery.com")
                    .firstName(firstName)
                    .lastName(lastName)
                    .role(role)
                    .isActive(true)
                    .build();

            userRepository.save(user);
            log.info("Created user: {} with role: {}", username, role);
        } else {
            log.info("User already exists: {}", username);
        }
    }
}
