
// Script pour le formulaire d'exercice avec énoncé complet uniquement
document.addEventListener('DOMContentLoaded', function() {
    // Validation du formulaire d'énoncé
    const form = document.getElementById('operation-form');
    if (form) {
        form.addEventListener('submit', function(event) {
            const enonceField = document.getElementById('enonce');
            if (!enonceField.value.trim()) {
                event.preventDefault();
                enonceField.classList.add('is-invalid');
                alert('Veuillez saisir un énoncé pour résoudre l\'exercice.');
            } else {
                enonceField.classList.remove('is-invalid');
            }
        });
    }
});


/**
 * Script pour la validation du formulaire d'exercice
 */
document.addEventListener('DOMContentLoaded', function() {
    // Sélectionner les éléments du formulaire
    const form = document.getElementById('exerciseForm');
    if (!form) return; // Sortir si le formulaire n'existe pas sur cette page
    
    const nameInput = document.querySelector('input[name="name"]');
    const startDateInput = document.querySelector('input[name="start_date"]');
    const endDateInput = document.querySelector('input[name="end_date"]');
    const submitBtn = document.getElementById('submitBtn');
    
    // Ajouter des valeurs par défaut pour les dates
    if (startDateInput && !startDateInput.value) {
        const today = new Date();
        const firstDay = new Date(today.getFullYear(), 0, 1); // 1er janvier de l'année courante
        startDateInput.value = firstDay.toISOString().split('T')[0];
    }
    
    if (endDateInput && !endDateInput.value) {
        const today = new Date();
        const lastDay = new Date(today.getFullYear(), 11, 31); // 31 décembre de l'année courante
        endDateInput.value = lastDay.toISOString().split('T')[0];
    }
    
    // Fonction de validation du formulaire
    function validateForm() {
        let isValid = true;
        
        // Validation du nom
        if (!nameInput.value.trim()) {
            nameInput.classList.add('is-invalid');
            isValid = false;
        } else {
            nameInput.classList.remove('is-invalid');
        }
        
        // Validation des dates
        if (!startDateInput.value) {
            startDateInput.classList.add('is-invalid');
            isValid = false;
        } else {
            startDateInput.classList.remove('is-invalid');
        }
        
        if (!endDateInput.value) {
            endDateInput.classList.add('is-invalid');
            isValid = false;
        } else {
            endDateInput.classList.remove('is-invalid');
        }
        
        // Validation date de fin > date de début
        if (startDateInput.value && endDateInput.value) {
            const startDate = new Date(startDateInput.value);
            const endDate = new Date(endDateInput.value);
            
            if (endDate < startDate) {
                endDateInput.classList.add('is-invalid');
                const errorMsg = endDateInput.nextElementSibling;
                if (errorMsg && errorMsg.classList.contains('invalid-feedback')) {
                    errorMsg.textContent = 'La date de fin doit être postérieure à la date de début';
                } else {
                    const newErrorMsg = document.createElement('div');
                    newErrorMsg.classList.add('invalid-feedback');
                    newErrorMsg.textContent = 'La date de fin doit être postérieure à la date de début';
                    endDateInput.parentNode.insertBefore(newErrorMsg, endDateInput.nextElementSibling);
                }
                isValid = false;
            }
        }
        
        return isValid;
    }
    
    // Gestionnaire d'événement pour la soumission du formulaire
    form.addEventListener('submit', function(e) {
        if (!validateForm()) {
            e.preventDefault();
        } else {
            // Désactiver le bouton pour éviter les soumissions multiples
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Enregistrement...';
        }
    });
    
    // Validation en temps réel pour les dates
    if (startDateInput && endDateInput) {
        [startDateInput, endDateInput].forEach(input => {
            input.addEventListener('change', function() {
                if (startDateInput.value && endDateInput.value) {
                    const startDate = new Date(startDateInput.value);
                    const endDate = new Date(endDateInput.value);
                    
                    if (endDate < startDate) {
                        endDateInput.classList.add('is-invalid');
                        const errorMsg = endDateInput.nextElementSibling;
                        if (errorMsg && errorMsg.classList.contains('invalid-feedback')) {
                            errorMsg.textContent = 'La date de fin doit être postérieure à la date de début';
                        } else {
                            const newErrorMsg = document.createElement('div');
                            newErrorMsg.classList.add('invalid-feedback');
                            newErrorMsg.textContent = 'La date de fin doit être postérieure à la date de début';
                            endDateInput.parentNode.insertBefore(newErrorMsg, endDateInput.nextElementSibling);
                        }
                    } else {
                        endDateInput.classList.remove('is-invalid');
                        const errorMsg = endDateInput.nextElementSibling;
                        if (errorMsg && errorMsg.classList.contains('invalid-feedback')) {
                            errorMsg.remove();
                        }
                    }
                }
            });
        });
    }
});
// Script pour le formulaire de résolution d'exercice avec énoncé uniquement
document.addEventListener('DOMContentLoaded', function() {
    // Vérifier si on est sur la page de résolution d'exercice
    const operationForm = document.getElementById('operation-form');
    if (!operationForm) return;

    // Validation du formulaire d'énoncé
    operationForm.addEventListener('submit', function(e) {
        const enonceField = document.getElementById('enonce');
        if (!enonceField.value.trim()) {
            e.preventDefault();
            enonceField.classList.add('is-invalid');
            alert('Veuillez saisir un énoncé pour résoudre l\'exercice.');
            return false;
        } else {
            enonceField.classList.remove('is-invalid');
            return true;
        }
    });
});
