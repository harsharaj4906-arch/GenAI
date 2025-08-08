// Main JavaScript file for the Retail Q&A application

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    initializeApp();
});

function initializeApp() {
    // Set up event listeners
    setupEventListeners();
    
    // Initialize tooltips if any
    initializeTooltips();
    
    console.log('Retail Q&A App initialized successfully');
}

function setupEventListeners() {
    // Handle form submission
    const questionForm = document.getElementById('questionForm');
    if (questionForm) {
        questionForm.addEventListener('submit', handleFormSubmit);
    }
    
    // Handle example question buttons
    const exampleButtons = document.querySelectorAll('.example-question');
    exampleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const question = this.getAttribute('data-question');
            document.getElementById('question').value = question;
            
            // Smooth scroll to question textarea
            document.getElementById('question').scrollIntoView({
                behavior: 'smooth',
                block: 'center'
            });
            
            // Focus on the textarea
            setTimeout(() => {
                document.getElementById('question').focus();
            }, 500);
        });
    });
    
    // Handle textarea auto-resize
    const questionTextarea = document.getElementById('question');
    if (questionTextarea) {
        questionTextarea.addEventListener('input', autoResizeTextarea);
    }
}

function handleFormSubmit(event) {
    const question = document.getElementById('question').value.trim();
    
    if (!question) {
        event.preventDefault();
        showAlert('Please enter a question before submitting.', 'warning');
        return false;
    }
    
    // Show loading state
    showLoadingState();
    
    // Let the form submit normally (server-side processing)
    return true;
}

function showLoadingState() {
    const submitBtn = document.getElementById('submitBtn');
    const loadingSpinner = document.getElementById('loadingSpinner');
    
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
    }
    
    if (loadingSpinner) {
        loadingSpinner.style.display = 'block';
    }
}

function hideLoadingState() {
    const submitBtn = document.getElementById('submitBtn');
    const loadingSpinner = document.getElementById('loadingSpinner');
    
    if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-paper-plane me-2"></i>Ask AI Assistant';
    }
    
    if (loadingSpinner) {
        loadingSpinner.style.display = 'none';
    }
}

function autoResizeTextarea() {
    const textarea = this;
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
}

function copyAnswer() {
    const answerContent = document.querySelector('.answer-content div.mt-2');
    if (answerContent) {
        // Create a temporary textarea to copy the text content
        const tempTextarea = document.createElement('textarea');
        tempTextarea.value = answerContent.innerText;
        document.body.appendChild(tempTextarea);
        tempTextarea.select();
        
        try {
            document.execCommand('copy');
            showAlert('Answer copied to clipboard!', 'success');
        } catch (err) {
            console.error('Failed to copy text: ', err);
            showAlert('Failed to copy answer. Please try selecting and copying manually.', 'warning');
        }
        
        document.body.removeChild(tempTextarea);
    }
}

function clearAnswer() {
    // Clear the question textarea
    const questionTextarea = document.getElementById('question');
    if (questionTextarea) {
        questionTextarea.value = '';
        questionTextarea.focus();
    }
    
    // Scroll to top smoothly
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
    
    // Optionally redirect to clear the answer from the page
    setTimeout(() => {
        window.location.href = '/';
    }, 500);
}

function showAlert(message, type = 'info') {
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.setAttribute('role', 'alert');
    
    alertDiv.innerHTML = `
        <i class="fas fa-info-circle me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Insert at the top of the container
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv && alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

function initializeTooltips() {
    // Initialize Bootstrap tooltips if any exist
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// API helper functions for future AJAX implementation
async function askQuestionAPI(question) {
    try {
        const response = await fetch('/api/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question: question })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error asking question:', error);
        throw error;
    }
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function formatAnswer(answer) {
    // Basic formatting for better readability
    return answer
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br>')
        .replace(/^/, '<p>')
        .replace(/$/, '</p>');
}

// Error handling
window.addEventListener('error', function(event) {
    console.error('Global error:', event.error);
    showAlert('An unexpected error occurred. Please refresh the page and try again.', 'danger');
});

// Handle unhandled promise rejections
window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
    showAlert('A network error occurred. Please check your connection and try again.', 'warning');
});

// Export functions for global access if needed
window.retailQA = {
    copyAnswer,
    clearAnswer,
    showAlert,
    askQuestionAPI
};
