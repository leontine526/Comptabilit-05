/**
 * Script pour la gestion des formulaires d'exercices
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Script de formulaire d\'exercice initialisé.');

    const form = document.getElementById('exercise-form');
    if (form) {
        // Gestion des dates
        const startDateInput = form.querySelector('input[type="date"][name*="start"]');
        const endDateInput = form.querySelector('input[type="date"][name*="end"]');

        if (startDateInput && endDateInput) {
            function validateDates() {
                if (startDateInput.value && endDateInput.value) {
                    const startDate = new Date(startDateInput.value);
                    const endDate = new Date(endDateInput.value);

                    if (endDate < startDate) {
                        endDateInput.classList.add('is-invalid');

                        // Ajouter un message d'erreur
                        let errorMsg = endDateInput.nextElementSibling;
                        if (!errorMsg || !errorMsg.classList.contains('invalid-feedback')) {
                            errorMsg = document.createElement('div');
                            errorMsg.className = 'invalid-feedback';
                            endDateInput.parentNode.insertBefore(errorMsg, endDateInput.nextSibling);
                        }
                        errorMsg.textContent = 'La date de fin doit être postérieure à la date de début.';

                        return false;
                    } else {
                        endDateInput.classList.remove('is-invalid');

                        // Supprimer le message d'erreur
                        const errorMsg = endDateInput.nextElementSibling;
                        if (errorMsg && errorMsg.classList.contains('invalid-feedback')) {
                            errorMsg.remove();
                        }

                        return true;
                    }
                }
                return true;
            }

            startDateInput.addEventListener('change', validateDates);
            endDateInput.addEventListener('change', validateDates);
        }

        // Validation du formulaire
        form.addEventListener('submit', function(e) {
            let isValid = true;

            // Validation des dates
            if (startDateInput && endDateInput) {
                isValid = validateDates() && isValid;
            }

            // Validation de l'énoncé
            const enonceField = form.querySelector('textarea[name="enonce"]');
            if (enonceField) {
                if (enonceField.value.trim() === '') {
                    enonceField.classList.add('is-invalid');

                    let errorMsg = enonceField.nextElementSibling;
                    if (!errorMsg || !errorMsg.classList.contains('invalid-feedback')) {
                        errorMsg = document.createElement('div');
                        errorMsg.className = 'invalid-feedback';
                        enonceField.parentNode.insertBefore(errorMsg, enonceField.nextSibling);
                    }
                    errorMsg.textContent = 'L\'énoncé est obligatoire.';

                    isValid = false;
                } else {
                    enonceField.classList.remove('is-invalid');

                    const errorMsg = enonceField.nextElementSibling;
                    if (errorMsg && errorMsg.classList.contains('invalid-feedback')) {
                        errorMsg.remove();
                    }
                }
            }

            if (!isValid) {
                e.preventDefault();
                return false;
            }

            return true;
        });
    }
});