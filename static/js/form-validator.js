
/**
 * Validation avancée des formulaires côté client
 * Permet de valider les formulaires avant envoi et d'afficher des messages d'erreur
 */
document.addEventListener('DOMContentLoaded', function() {
    // Initialiser la validation pour tous les formulaires
    const forms = document.querySelectorAll('form[data-validate="true"]');
    forms.forEach(initFormValidation);
    
    // Validation input par input sur tous les formulaires
    document.querySelectorAll('input, textarea, select').forEach(input => {
        // Validation à la perte de focus
        input.addEventListener('blur', function() {
            validateInput(this);
        });
        
        // Validation dynamique sur certains champs (email, nombre, etc.)
        if (input.type === 'email' || input.type === 'number' || 
            input.dataset.validatePattern || input.required) {
            input.addEventListener('input', function() {
                // Valider seulement si l'utilisateur a déjà interagi avec le champ
                if (this.classList.contains('was-validated') || this.dataset.validated) {
                    validateInput(this);
                }
            });
        }
    });
    
    // Vérification des mots de passe identiques
    document.querySelectorAll('input[type="password"][data-match]').forEach(pwdInput => {
        pwdInput.addEventListener('input', function() {
            const targetId = this.dataset.match;
            const targetInput = document.getElementById(targetId);
            if (targetInput && targetInput.value) {
                if (this.value !== targetInput.value) {
                    this.setCustomValidity('Les mots de passe ne correspondent pas');
                    showInputError(this, 'Les mots de passe ne correspondent pas');
                } else {
                    this.setCustomValidity('');
                    clearInputError(this);
                }
            }
        });
    });
});

/**
 * Initialise la validation pour un formulaire
 */
function initFormValidation(form) {
    // Empêcher la soumission par défaut et valider
    form.addEventListener('submit', function(event) {
        // Marquer tous les champs comme validés
        form.querySelectorAll('input, textarea, select').forEach(input => {
            input.dataset.validated = true;
            validateInput(input);
        });
        
        if (!form.checkValidity()) {
            event.preventDefault();
            event.stopPropagation();
            
            // Trouver le premier champ avec une erreur et faire défiler jusqu'à lui
            const firstInvalidField = form.querySelector(':invalid');
            if (firstInvalidField) {
                firstInvalidField.focus();
                firstInvalidField.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
            
            // Afficher un message global d'erreur
            const errorSummary = form.querySelector('.error-summary') || 
                                 document.createElement('div');
            errorSummary.className = 'alert alert-danger error-summary mt-3';
            errorSummary.innerHTML = '<strong>Veuillez corriger les erreurs suivantes :</strong><ul></ul>';
            
            const errorList = errorSummary.querySelector('ul');
            form.querySelectorAll(':invalid').forEach(invalidField => {
                const label = form.querySelector(`label[for="${invalidField.id}"]`) || 
                              { textContent: invalidField.name || 'Champ' };
                const errorItem = document.createElement('li');
                errorItem.textContent = `${label.textContent}: ${invalidField.validationMessage || 'Valeur invalide'}`;
                errorList.appendChild(errorItem);
            });
            
            if (!form.querySelector('.error-summary')) {
                form.prepend(errorSummary);
            }
        } else {
            // Nettoyer les erreurs si tout est valide
            const errorSummary = form.querySelector('.error-summary');
            if (errorSummary) {
                errorSummary.remove();
            }
            
            // Désactiver le bouton de soumission pour éviter les soumissions multiples
            const submitButton = form.querySelector('button[type="submit"], input[type="submit"]');
            if (submitButton && !form.dataset.noDisable) {
                submitButton.disabled = true;
                const originalText = submitButton.innerHTML;
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Traitement en cours...';
                
                // Réactiver le bouton après un délai si la soumission échoue
                setTimeout(() => {
                    submitButton.disabled = false;
                    submitButton.innerHTML = originalText;
                }, 10000);
            }
        }
        
        form.classList.add('was-validated');
    });
    
    // Validation spécifique pour les fichiers
    form.querySelectorAll('input[type="file"]').forEach(fileInput => {
        fileInput.addEventListener('change', function() {
            validateFileInput(this);
        });
    });
}

/**
 * Valide un champ de saisie individuel
 */
function validateInput(input) {
    // Ignorer les champs désactivés ou en lecture seule
    if (input.disabled || input.readOnly) return;
    
    // Marquer le champ comme ayant été interagi
    input.dataset.validated = true;
    
    // Nettoyer les erreurs précédentes
    clearInputError(input);
    
    // Validation de base HTML5
    let isValid = input.checkValidity();
    
    // Validation personnalisée selon le type
    if (isValid) {
        // Validation email
        if (input.type === 'email' && input.value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            isValid = emailRegex.test(input.value);
            if (!isValid) {
                input.setCustomValidity('Veuillez entrer une adresse email valide');
                showInputError(input, 'Format d\'email invalide');
            }
        }
        
        // Validation des motifs personnalisés
        if (input.dataset.validatePattern && input.value) {
            const pattern = new RegExp(input.dataset.validatePattern);
            isValid = pattern.test(input.value);
            if (!isValid) {
                input.setCustomValidity(input.dataset.validateMessage || 'Format invalide');
                showInputError(input, input.dataset.validateMessage || 'Format invalide');
            }
        }
        
        // Validation des mots de passe
        if (input.type === 'password' && input.dataset.validateStrength && input.value) {
            const strength = checkPasswordStrength(input.value);
            isValid = strength >= (parseInt(input.dataset.validateStrength) || 2);
            if (!isValid) {
                input.setCustomValidity('Le mot de passe est trop faible');
                showInputError(input, 'Le mot de passe doit contenir au moins 8 caractères, dont des majuscules, minuscules, chiffres et caractères spéciaux.');
            }
        }
    } else {
        // Afficher le message d'erreur standard HTML5
        showInputError(input, input.validationMessage);
    }
    
    // Mettre à jour les classes visuelles
    if (isValid) {
        input.classList.add('is-valid');
        input.classList.remove('is-invalid');
    } else {
        input.classList.remove('is-valid');
        input.classList.add('is-invalid');
    }
    
    return isValid;
}

/**
 * Valide un champ de fichier
 */
function validateFileInput(input) {
    // Nettoyer les erreurs précédentes
    clearInputError(input);
    
    // Validation de base
    let isValid = input.checkValidity();
    
    // Validation de l'extension si spécifiée
    if (isValid && input.files.length > 0) {
        const file = input.files[0];
        
        // Valider la taille du fichier
        if (input.dataset.maxSize) {
            const maxSize = parseInt(input.dataset.maxSize) * 1024; // en Ko
            if (file.size > maxSize) {
                isValid = false;
                input.setCustomValidity(`Le fichier est trop volumineux (max: ${input.dataset.maxSize} Ko)`);
                showInputError(input, `Le fichier est trop volumineux (max: ${input.dataset.maxSize} Ko)`);
            }
        }
        
        // Valider les extensions
        if (isValid && input.dataset.allowedExtensions) {
            const allowedExtensions = input.dataset.allowedExtensions.split(',').map(ext => ext.trim().toLowerCase());
            const fileExtension = file.name.split('.').pop().toLowerCase();
            if (!allowedExtensions.includes(fileExtension)) {
                isValid = false;
                input.setCustomValidity(`Extension de fichier non autorisée. Extensions acceptées: ${input.dataset.allowedExtensions}`);
                showInputError(input, `Extension non autorisée. Accepté: ${input.dataset.allowedExtensions}`);
            }
        }
    }
    
    // Mettre à jour les classes visuelles
    if (isValid) {
        input.classList.add('is-valid');
        input.classList.remove('is-invalid');
        
        // Afficher le nom du fichier sélectionné
        const fileLabel = input.nextElementSibling;
        if (fileLabel && fileLabel.classList.contains('custom-file-label')) {
            fileLabel.textContent = input.files.length > 0 ? input.files[0].name : 'Choisir un fichier';
        }
    } else {
        input.classList.remove('is-valid');
        input.classList.add('is-invalid');
    }
    
    return isValid;
}

/**
 * Vérifie la force d'un mot de passe
 * Retourne une valeur de 0 (très faible) à 4 (très fort)
 */
function checkPasswordStrength(password) {
    let strength = 0;
    
    // Longueur minimale
    if (password.length >= 8) strength += 1;
    
    // Contient des lettres minuscules
    if (/[a-z]/.test(password)) strength += 1;
    
    // Contient des lettres majuscules et des chiffres
    if (/[A-Z]/.test(password) && /[0-9]/.test(password)) strength += 1;
    
    // Contient des caractères spéciaux
    if (/[^a-zA-Z0-9]/.test(password)) strength += 1;
    
    return strength;
}

/**
 * Affiche un message d'erreur pour un champ
 */
function showInputError(input, message) {
    // Créer un élément de feedback s'il n'existe pas déjà
    let feedback = input.nextElementSibling;
    if (!feedback || !feedback.classList.contains('invalid-feedback')) {
        feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        input.parentNode.insertBefore(feedback, input.nextSibling);
    }
    
    feedback.textContent = message;
}

/**
 * Efface les erreurs d'un champ
 */
function clearInputError(input) {
    input.setCustomValidity(''); // Réinitialiser la validation HTML5
    
    // Supprimer le feedback s'il existe
    const feedback = input.nextElementSibling;
    if (feedback && feedback.classList.contains('invalid-feedback')) {
        feedback.textContent = '';
    }
}
