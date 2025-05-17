
// Script pour prévisualiser l'image de profil avant upload
document.addEventListener('DOMContentLoaded', function() {
    const profilePictureInput = document.getElementById('profile_picture');
    const previewContainer = document.getElementById('profile-image-preview');
    
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
});
