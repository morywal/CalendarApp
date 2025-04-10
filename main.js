// Main JavaScript file for the AI Calendar App

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Task duration estimation
    const estimateDurationBtn = document.getElementById('estimateDurationBtn');
    if (estimateDurationBtn) {
        estimateDurationBtn.addEventListener('click', function() {
            const titleInput = document.getElementById('title');
            const descriptionInput = document.getElementById('description');
            const categoryInput = document.getElementById('category');
            const durationInput = document.getElementById('estimated_duration');
            
            if (!titleInput.value.trim()) {
                alert('Please enter a task title first.');
                return;
            }
            
            // Show loading state
            estimateDurationBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Estimating...';
            estimateDurationBtn.disabled = true;
            
            // Make API call to get duration estimate
            fetch('/tasks/api/estimate_duration', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    title: titleInput.value.trim(),
                    description: descriptionInput.value.trim(),
                    category: categoryInput.value.trim()
                }),
            })
            .then(response => response.json())
            .then(data => {
                durationInput.value = data.estimated_duration;
                // Reset button
                estimateDurationBtn.innerHTML = '<i class="fas fa-magic"></i> Suggest';
                estimateDurationBtn.disabled = false;
            })
            .catch((error) => {
                console.error('Error:', error);
                alert('Failed to get duration estimate. Please try again or enter manually.');
                // Reset button
                estimateDurationBtn.innerHTML = '<i class="fas fa-magic"></i> Suggest';
                estimateDurationBtn.disabled = false;
            });
        });
    }

    // Task status update confirmation
    const statusForms = document.querySelectorAll('form[id^="statusForm"]');
    statusForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const statusSelect = form.querySelector('select[name="status"]');
            if (statusSelect.value === 'completed') {
                const confirmComplete = confirm('Are you sure you want to mark this task as completed? You\'ll be able to provide feedback on the actual duration.');
                if (!confirmComplete) {
                    e.preventDefault();
                }
            }
        });
    });

    // Calendar view enhancements
    const calendarEl = document.getElementById('calendar');
    if (calendarEl) {
        // Add event listeners for calendar interactions
        document.querySelectorAll('.fc-event').forEach(event => {
            event.addEventListener('mouseover', function() {
                this.style.cursor = 'pointer';
            });
        });
    }

    // Mobile navigation enhancements
    const navbarToggler = document.querySelector('.navbar-toggler');
    if (navbarToggler) {
        navbarToggler.addEventListener('click', function() {
            document.querySelector('.navbar-collapse').classList.toggle('show');
        });
    }

    // Form validation enhancement
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
});
