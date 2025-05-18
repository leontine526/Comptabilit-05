
// Fonction pour gérer l'ajout d'opération
document.addEventListener('DOMContentLoaded', function() {
    // Éléments du formulaire
    const useFullExerciseCheckbox = document.getElementById('use-full-exercise');
    const fullExerciseSection = document.getElementById('full-exercise-section');
    const operationsContainer = document.getElementById('operations-container');
    const addOperationContainer = document.getElementById('add-operation-container');
    const addOperationButton = document.getElementById('add-operation');
    const operationsForm = document.getElementById('operationsForm');
    
    // Gestion du basculement entre énoncé complet et opérations individuelles
    if (useFullExerciseCheckbox) {
        useFullExerciseCheckbox.addEventListener('change', function() {
            if (this.checked) {
                // Mode énoncé complet
                fullExerciseSection.style.display = 'block';
                operationsContainer.style.display = 'none';
                addOperationContainer.style.display = 'none';
                
                // Rendre le champ énoncé obligatoire et les champs opérations non-obligatoires
                document.querySelectorAll('#operations-container input[required]').forEach(input => {
                    input.required = false;
                });
                document.getElementById('enonce').required = true;
            } else {
                // Mode opérations individuelles
                fullExerciseSection.style.display = 'none';
                operationsContainer.style.display = 'block';
                addOperationContainer.style.display = 'block';
                
                // Rendre les champs opérations obligatoires et le champ énoncé non-obligatoire
                document.querySelectorAll('#operations-container input[name="texte"], #operations-container input[name="montant_ht"], #operations-container input[name="date_op"]').forEach(input => {
                    input.required = true;
                });
                document.getElementById('enonce').required = false;
            }
        });
    }
    
    // Gestion de l'ajout d'opérations
    let operationCount = 1;
    
    if (addOperationButton) {
        addOperationButton.addEventListener('click', function() {
            operationCount++;
            
            const newOperation = document.createElement('div');
            newOperation.className = 'operation mb-4 p-3 border rounded bg-light';
            newOperation.innerHTML = `
                <div class="d-flex justify-content-between mb-3">
                    <h6>Opération ${operationCount}</h6>
                    <button type="button" class="btn btn-sm btn-outline-danger remove-operation">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="row mb-3">
                    <div class="col-md-6">
                        <label for="texte-${operationCount-1}" class="form-label">Description de l'opération</label>
                        <input type="text" class="form-control" id="texte-${operationCount-1}" name="texte" placeholder="Ex: Achat de marchandises" required>
                    </div>
                    <div class="col-md-3">
                        <label for="montant_ht-${operationCount-1}" class="form-label">Montant HT</label>
                        <input type="number" class="form-control" id="montant_ht-${operationCount-1}" name="montant_ht" placeholder="Montant" required>
                    </div>
                    <div class="col-md-3">
                        <label for="date_op-${operationCount-1}" class="form-label">Date</label>
                        <input type="date" class="form-control" id="date_op-${operationCount-1}" name="date_op" required>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-4">
                        <label for="taux_tva-${operationCount-1}" class="form-label">Taux TVA (%)</label>
                        <input type="number" class="form-control" id="taux_tva-${operationCount-1}" name="taux_tva" value="19.25" placeholder="Ex: 19.25">
                    </div>
                    <div class="col-md-4">
                        <label for="frais_accessoires-${operationCount-1}" class="form-label">Frais accessoires</label>
                        <input type="number" class="form-control" id="frais_accessoires-${operationCount-1}" name="frais_accessoires" placeholder="Si applicable">
                    </div>
                    <div class="col-md-4">
                        <label for="remise-${operationCount-1}" class="form-label">Remise (%)</label>
                        <input type="number" class="form-control" id="remise-${operationCount-1}" name="remise" placeholder="Si applicable">
                    </div>
                </div>
            `;
            
            operationsContainer.appendChild(newOperation);
            
            // Ajout des gestionnaires d'événements pour les boutons de suppression
            const removeButtons = document.querySelectorAll('.remove-operation');
            removeButtons.forEach(button => {
                button.addEventListener('click', function() {
                    this.closest('.operation').remove();
                });
            });
        });
    }
    
    // Soumettre le formulaire
    if (operationsForm) {
        operationsForm.addEventListener('submit', function(event) {
            // Validation spécifique si nécessaire
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
// Fonctions pour gérer le formulaire de résolution d'exercice
document.addEventListener('DOMContentLoaded', function() {
    // Vérifier si on est sur la page de résolution d'exercice
    const operationForm = document.getElementById('operation-form');
    if (!operationForm) return;

    // Fonctionnalité pour vérifier l'équilibre des écritures
    operationForm.addEventListener('submit', function(e) {
        const modeEnonce = document.getElementById('mode-enonce');
        
        // Si on est en mode énoncé, pas besoin de vérifier l'équilibre
        if (modeEnonce && modeEnonce.checked) return true;
        
        // Vérifier que toutes les opérations ont une description et un montant
        const descriptions = document.querySelectorAll('textarea[name="texte"]');
        const amounts = document.querySelectorAll('input[name="montant_ht"]');
        let isValid = true;
        
        descriptions.forEach((desc, index) => {
            if (!desc.value.trim()) {
                desc.classList.add('is-invalid');
                isValid = false;
            } else {
                desc.classList.remove('is-invalid');
            }
            
            if (!amounts[index].value || parseFloat(amounts[index].value) <= 0) {
                amounts[index].classList.add('is-invalid');
                isValid = false;
            } else {
                amounts[index].classList.remove('is-invalid');
            }
        });
        
        if (!isValid) {
            e.preventDefault();
            alert('Veuillez remplir correctement toutes les opérations.');
            return false;
        }
        
        return true;
    });
    
    // Mise à jour automatique des dates
    const today = new Date().toISOString().split('T')[0];
    document.querySelectorAll('input[name="date_op"]').forEach(input => {
        if (!input.value) {
            input.value = today;
        }
    });
    
    // Mise en forme des nombres
    document.querySelectorAll('input[type="number"]').forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value && !isNaN(parseFloat(this.value))) {
                this.value = parseFloat(this.value).toFixed(2);
            }
        });
    });
});
