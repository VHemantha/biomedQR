// Main JavaScript functionality for Equipment QR System

// Add interactive animations
document.addEventListener('DOMContentLoaded', function() {
    const buttons = document.querySelectorAll('.btn, .action-btn:not(:disabled), .back-btn');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            if (!this.disabled) {
                this.style.transform = 'translateY(-2px) scale(1.02)';
            }
        });
        
        button.addEventListener('mouseleave', function() {
            if (!this.disabled) {
                this.style.transform = 'translateY(0) scale(1)';
            }
        });
    });
});

// Utility function for showing status messages
function showStatus(message, type) {
    const statusDiv = document.getElementById('statusMessage');
    if (!statusDiv) return;
    
    let iconClass = '';
    
    if (type === 'loading') {
        iconClass = '<div class="spinner"></div> ';
    }
    
    statusDiv.innerHTML = `<div class="status-message status-${type}">${iconClass}${message}</div>`;
    
    if (type === 'success') {
        setTimeout(() => {
            statusDiv.innerHTML = '';
        }, 5000);
    } else if (type === 'error') {
        setTimeout(() => {
            statusDiv.innerHTML = '';
        }, 10000);
    }
}

// Export functions for use in templates
window.showStatus = showStatus;
