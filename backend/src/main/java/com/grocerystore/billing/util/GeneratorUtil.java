package com.grocerystore.billing.util;

import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.security.SecureRandom;
import java.util.Random;

/**
 * Generator Utility
 * Generates unique IDs and codes
 */
@Component
@Slf4j
public class GeneratorUtil {
    
    private static final String BARCODE_PREFIX = "GB";
    private static final String SKU_PREFIX = "SKU";
    private static final Random random = new SecureRandom();
    
    /**
     * Generate unique barcode
     */
    public String generateBarcode() {
        String barcode = BARCODE_PREFIX + System.currentTimeMillis() + random.nextInt(10000);
        log.debug("Generated barcode: {}", barcode);
        return barcode;
    }
    
    /**
     * Generate unique SKU
     */
    public String generateSKU() {
        String sku = SKU_PREFIX + System.currentTimeMillis() + random.nextInt(10000);
        log.debug("Generated SKU: {}", sku);
        return sku;
    }
    
    /**
     * Generate unique bill number
     */
    public String generateBillNumber() {
        String billNumber = "BILL" + System.currentTimeMillis();
        log.debug("Generated bill number: {}", billNumber);
        return billNumber;
    }
    
    /**
     * Generate random password
     */
    public String generatePassword(int length) {
        String characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@#$%";
        StringBuilder password = new StringBuilder();
        
        for (int i = 0; i < length; i++) {
            password.append(characters.charAt(random.nextInt(characters.length())));
        }
        
        return password.toString();
    }
}
