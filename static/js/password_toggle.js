document.addEventListener('DOMContentLoaded', function() {
    // Get all show password checkboxes
    const showPasswordCheckboxes = document.querySelectorAll('input[type="checkbox"][name="show_password"]');
    
    showPasswordCheckboxes.forEach(function(checkbox) {
        checkbox.addEventListener('change', function() {
            // Find all password fields in the form
            const form = checkbox.closest('form');
            const passwordFields = form.querySelectorAll('input[type="password"]');
            
            // Toggle type between password and text
            passwordFields.forEach(function(field) {
                if (checkbox.checked) {
                    field.type = 'text';
                } else {
                    field.type = 'password';
                }
            });
        });
    });
});