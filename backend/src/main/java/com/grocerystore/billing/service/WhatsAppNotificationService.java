package com.grocerystore.billing.service;

import com.grocerystore.billing.entity.Bill;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

/**
 * WhatsApp Notification Service (Demo Mode)
 * Simulates sending WhatsApp notifications by logging them.
 */
@Service
@Slf4j
public class WhatsAppNotificationService {

        private static final String APP_WHATSAPP_NUMBER = "9673311365";

    /**
     * Simulates sending a bill confirmation via WhatsApp.
     * In production, integrate with Twilio or a similar provider.
     */
    public void sendBillConfirmation(Bill bill) {
        String phone = (bill.getCustomer() != null && bill.getCustomer().getPhone() != null)
                ? bill.getCustomer().getPhone() : "N/A";
        String customerName = (bill.getCustomer() != null && bill.getCustomer().getName() != null)
                ? bill.getCustomer().getName() : "Customer";

        log.info("═══════════════════════════════════════════════════════════════");
        log.info("📱 WHATSAPP MESSAGE (DEMO MODE - NOT ACTUALLY SENT)");
        log.info("═══════════════════════════════════════════════════════════════");
        log.info("From: whatsapp:+91{}", APP_WHATSAPP_NUMBER);
        log.info("To: whatsapp:+91{}", phone);
        log.info("Customer: {}", customerName);
        log.info("Bill Number: {}", bill.getBillNumber());
        log.info("Amount: Rs. {}", bill.getTotalAmount());
        log.info("Message: Thanks {}! Your bill {} has been generated. Total: Rs. {}.",
                customerName, bill.getBillNumber(), bill.getTotalAmount());
        log.info("═══════════════════════════════════════════════════════════════");
    }
}
