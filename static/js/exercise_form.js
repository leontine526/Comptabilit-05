document.addEventListener('DOMContentLoaded', function() {
    // Référence au formulaire
    const exerciseForm = document.getElementById('exerciseForm');

    // S'assurer que l'élément existe avant d'ajouter un écouteur d'événement
    if (exerciseForm) {
        const nameInput = document.querySelector('input[name="name"]');
        const startDateInput = document.querySelector('input[name="start_date"]');
        const endDateInput = document.querySelector('input[name="end_date"]');
        const submitBtn = document.getElementById('submitBtn');

        exerciseForm.addEventListener('submit', function(event) {
            let isValid = true;

            // Validation des dates
            if (startDateInput && startDateInput.value && endDateInput && endDateInput.value) {
                const startDate = new Date(startDateInput.value);
                const endDate = new Date(endDateInput.value);value);

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
                } else {
                    endDateInput.classList.remove('is-invalid');
                    const errorMsg = endDateInput.nextElementSibling;
                    if (errorMsg && errorMsg.classList.contains('invalid-feedback')) {
                        errorMsg.remove();
                    }
                }
            }

            // Validation du nom
            if (nameInput && !nameInput.value.trim()) {
                nameInput.classList.add('is-invalid');
                isValid = false;
            } else if (nameInput){
                nameInput.classList.remove('is-invalid');
            }

            if (startDateInput && !startDateInput.value) {
                startDateInput.classList.add('is-invalid');
                isValid = false;
            } else if (startDateInput){
                startDateInput.classList.remove('is-invalid');
            }

            if (endDateInput && !endDateInput.value) {
                endDateInput.classList.add('is-invalid');
                isValid = false;
            } else if (endDateInput){
                endDateInput.classList.remove('is-invalid');
            }

            // Récupérer l'énoncé
            const enonce = document.getElementById('enonce').value.trim();

            // Vérifier si l'énoncé est vide
            if (!enonce) {
                event.preventDefault();
                alert('Veuillez saisir un énoncé pour résoudre l\'exercice.');
                return false;
            }

            if (!isValid) {
                event.preventDefault();
                return false;
            } else {
                 // Désactiver le bouton pour éviter les soumissions multiples
                if(submitBtn){
                    submitBtn.disabled = true;
                    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Enregistrement...';
                }

                // Si tout est valide, laisser le formulaire se soumettre normalement
                console.log('Soumission du formulaire avec énoncé:', enonce);
                return true;
            }


        });
    }

    // Prévenir le comportement par défaut des boutons qui pourraient interférer
    const buttons = document.querySelectorAll('button[type="button"]');
    buttons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
        });
    });

    console.log('Script de formulaire d\'exercice initialisé.');

     // Formulaire de résolution avec énoncé uniquement
    const operationForm = document.getElementById('operation-form');
    if (operationForm) {
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
        });ue;
            }
        });
    }
});