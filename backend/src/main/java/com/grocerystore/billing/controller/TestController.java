package com.grocerystore.billing.controller;

import com.grocerystore.billing.entity.Bill;
import com.grocerystore.billing.entity.Bill.BillStatus;
import com.grocerystore.billing.entity.Customer;
import com.grocerystore.billing.entity.User;
import com.grocerystore.billing.entity.User.UserRole;
import com.grocerystore.billing.service.WhatsAppNotificationService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/test")
@RequiredArgsConstructor
@Slf4j
public class TestController {

    private final WhatsAppNotificationService whatsAppNotificationService;

    @PostMapping("/whatsapp")
    public ResponseEntity<Map<String, Object>> testWhatsApp(
            @RequestParam(defaultValue = "9876543210") String phone,
            @RequestParam(defaultValue = "John Doe") String customerName) {
        
        log.info("Testing WhatsApp notification for phone: {}, customer: {}", phone, customerName);
        
        // Log simulated WhatsApp message directly
        log.info("═══════════════════════════════════════════════════════════════");
        log.info("📱 WHATSAPP MESSAGE (DEMO MODE - NOT ACTUALLY SENT)");
        log.info("═══════════════════════════════════════════════════════════════");
        log.info("To: whatsapp:+91{}", phone);
        log.info("Customer: {}", customerName);
        log.info("Bill Number: TEST-BILL-001");
        log.info("Amount: Rs. 500.00");
        log.info("Message: Thanks {}! Your bill TEST-BILL-001 has been generated. Total: Rs. 500.00.", customerName);
        log.info("═══════════════════════════════════════════════════════════════");

        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("message", "WhatsApp test message logged successfully!");
        response.put("customerPhone", phone);
        response.put("customerName", customerName);
        response.put("billNumber", "TEST-BILL-001");
        response.put("amount", "500.00");
        response.put("demoMode", true);
        response.put("note", "Check backend logs to see the WhatsApp message simulation.");

        return ResponseEntity.ok(response);
    }

    @GetMapping("/ping")
    public ResponseEntity<String> ping() {
        return ResponseEntity.ok("Test endpoint is working!");
    }
}
