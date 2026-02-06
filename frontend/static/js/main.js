/* Main JavaScript */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips and popovers
    initializeComponents();
});

function initializeComponents() {
    // Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-close alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-dismissible)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

// Utility function to format currency
function formatCurrency(value) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(value);
}

// Utility function to format date
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

// Utility function to show loading state
function showLoading(element) {
    element.innerHTML = '<div class="spinner"></div> Loading...';
    element.disabled = true;
}

// Utility function to hide loading state
function hideLoading(element, text) {
    element.innerHTML = text;
    element.disabled = false;
}

// Confirm delete action
function confirmDelete() {
    return confirm('Are you sure you want to delete this item?');
}
