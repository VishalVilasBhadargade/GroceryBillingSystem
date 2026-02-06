package com.grocerystore.billing;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.EnableAspectJAutoProxy;
import org.springframework.scheduling.annotation.EnableScheduling;

/**
 * Main Spring Boot Application Entry Point
 * 
 * Application: Grocery Store Billing System
 * Version: 1.0.0
 * Date: January 21, 2026
 */
@SpringBootApplication
@EnableScheduling
@EnableAspectJAutoProxy
public class GroceryBillingApplication {

    public static void main(String[] args) {
        SpringApplication.run(GroceryBillingApplication.class, args);
    }
}
