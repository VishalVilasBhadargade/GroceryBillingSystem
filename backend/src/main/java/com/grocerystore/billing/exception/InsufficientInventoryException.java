package com.grocerystore.billing.exception;

/**
 * Exception thrown when insufficient inventory is available
 */
public class InsufficientInventoryException extends RuntimeException {
    public InsufficientInventoryException(String message) {
        super(message);
    }

    public InsufficientInventoryException(String message, Throwable cause) {
        super(message, cause);
    }
}
