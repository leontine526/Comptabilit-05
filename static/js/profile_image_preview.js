
// Script pour prévisualiser l'image de profil avant upload et permettre la capture sur mobile
document.addEventListener('DOMContentLoaded', function() {
    const profilePictureInput = document.getElementById('profile_picture');
    const previewContainer = document.getElementById('profile-image-preview');
    const mobileCameraBtn = document.getElementById('mobile-camera-btn');
    
    if (profilePictureInput && previewContainer) {
        // S'assurer que le conteneur de prévisualisation est visible
        previewContainer.style.display = 'block';
        
        profilePictureInput.addEventListener('change', function() {
            previewContainer.innerHTML = '';
            
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    const img = document.createElement('img');
                    img.src = e.target.result;
                    img.style.maxWidth = '150px';
                    img.style.maxHeight = '150px';
                    img.className = 'rounded-circle border';
                    
                    // Ajouter un message de confirmation
                    const confirmationMsg = document.createElement('div');
                    confirmationMsg.textContent = 'Image sélectionnée!';
                    confirmationMsg.className = 'text-success mt-2';
                    
                    previewContainer.appendChild(img);
                    previewContainer.appendChild(confirmationMsg);
                };
                
                reader.onerror = function() {
                    // En cas d'erreur de lecture du fichier
                    const errorMsg = document.createElement('div');
                    errorMsg.textContent = "Erreur lors du chargement de l'image";
                    errorMsg.className = 'text-danger mt-2';
                    previewContainer.appendChild(errorMsg);
                };
                
                reader.readAsDataURL(this.files[0]);
            }
        });
    }
    
    // Support pour la capture de photos sur mobile
    if (mobileCameraBtn && profilePictureInput) {
        mobileCameraBtn.addEventListener('click', function() {
            try {
                // Créer un input temporaire avec capture="camera" pour les appareils mobiles
                const tempInput = document.createElement('input');
                tempInput.type = 'file';
                tempInput.accept = 'image/*';
                tempInput.capture = 'camera';
                
                tempInput.addEventListener('change', function() {
                    if (this.files && this.files[0]) {
                        try {
                            // Transférer le fichier sélectionné à l'input original
                            if (typeof DataTransfer === 'function') {
                                const dataTransfer = new DataTransfer();
                                dataTransfer.items.add(this.files[0]);
                                profilePictureInput.files = dataTransfer.files;
                            } else {
                                // Fallback pour les navigateurs qui ne supportent pas DataTransfer
                                profilePictureInput.files = this.files;
                            }
                            
                            // Déclencher l'événement change pour afficher l'aperçu
                            const event = new Event('change', { bubbles: true });
                            profilePictureInput.dispatchEvent(event);
                        } catch (e) {
                            console.error("Erreur lors du transfert de l'image:", e);
                            
                            // Afficher une erreur dans le conteneur de prévisualisation
                            if (previewContainer) {
                                previewContainer.innerHTML = '<div class="alert alert-danger">Erreur lors du traitement de l\'image.</div>';
                            }
                        }
                    }
                });
                
                // Déclencher le click sur l'input temporaire
                tempInput.click();
            } catch (e) {
                console.error("Erreur lors de l'ouverture de la caméra:", e);
            }
        });
    }
    
    // Ajouter un message d'info sous l'input file
    if (profilePictureInput) {
        const helpText = document.createElement('small');
        helpText.className = 'form-text text-muted mt-1';
        helpText.textContent = 'Formats acceptés: JPG, PNG, JPEG. Taille max: 5MB';
        profilePictureInput.parentNode.appendChild(helpText);
    }
});
