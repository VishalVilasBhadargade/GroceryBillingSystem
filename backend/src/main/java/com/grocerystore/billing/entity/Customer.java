package com.grocerystore.billing.entity;

import jakarta.persistence.*;
import lombok.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * Customer Entity
 * Represents customers with loyalty program
 */
@Entity
@Table(name = "customers", indexes = {
    @Index(name = "idx_customers_phone", columnList = "phone"),
    @Index(name = "idx_customers_email", columnList = "email"),
    @Index(name = "idx_customers_name", columnList = "first_name, last_name")
})
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Customer {
    // Add convenience setters for compatibility with service/DTO mapping
    public void setName(String name) {
        // Assume full name is split into first and last name by first space
        if (name != null) {
            String[] parts = name.trim().split(" ", 2);
            this.firstName = parts[0];
            this.lastName = parts.length > 1 ? parts[1] : "";
        }
    }

    public void setZipCode(String zipCode) {
        this.postalCode = zipCode;
    }

    public String getName() {
        return (firstName != null ? firstName : "") + (lastName != null && !lastName.isEmpty() ? " " + lastName : "");
    }

    public String getZipCode() {
        return postalCode;
    }

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer customerId;

    @Column(nullable = false, unique = true, length = 20)
    private String phone;

    @Column(unique = true, length = 100)
    private String email;

    @Column(nullable = false, length = 100)
    private String firstName;

    @Column(nullable = false, length = 100)
    private String lastName;

    @Column(length = 255)
    private String address;

    @Column(length = 100)
    private String city;

    @Column(length = 50)
    private String state;

    @Column(length = 20)
    private String postalCode;

    @Column(length = 100)
    private String country;

    @Column(nullable = false)
    private Integer loyaltyPoints;

    @Column(nullable = false, precision = 12, scale = 2)
    private BigDecimal totalSpent;

    @Column(nullable = false, updatable = false)
    private LocalDateTime memberSince;

    @Column(nullable = false)
    private Boolean isActive;

    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(nullable = false)
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
        memberSince = LocalDateTime.now();
        isActive = true;
        loyaltyPoints = 0;
        totalSpent = BigDecimal.ZERO;
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}
