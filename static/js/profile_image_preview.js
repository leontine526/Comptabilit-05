
// Script pour prévisualiser l'image de profil avant upload et permettre la capture sur mobile
document.addEventListener('DOMContentLoaded', function() {
    const profilePictureInput = document.getElementById('profile_picture');
    const previewContainer = document.getElementById('profile-image-preview');
    const mobileCameraBtn = document.getElementById('mobile-camera-btn');
    
    if (profilePictureInput && previewContainer) {
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
                    
                    previewContainer.appendChild(img);
                }
                
                reader.readAsDataURL(this.files[0]);
            }
        });
    }
    
    // Support pour la capture de photos sur mobile
    if (mobileCameraBtn && profilePictureInput) {
        mobileCameraBtn.addEventListener('click', function() {
            // Créer un input temporaire avec capture="camera" pour les appareils mobiles
            const tempInput = document.createElement('input');
            tempInput.type = 'file';
            tempInput.accept = 'image/*';
            tempInput.capture = 'camera';
            
            tempInput.addEventListener('change', function() {
                if (this.files && this.files[0]) {
                    // Transférer le fichier sélectionné à l'input original
                    const dataTransfer = new DataTransfer();
                    dataTransfer.items.add(this.files[0]);
                    profilePictureInput.files = dataTransfer.files;
                    
                    // Déclencher l'événement change pour afficher l'aperçu
                    const event = new Event('change', { bubbles: true });
                    profilePictureInput.dispatchEvent(event);
                }
            });
            
            // Déclencher le click sur l'input temporaire
            tempInput.click();
        });
    }
});
