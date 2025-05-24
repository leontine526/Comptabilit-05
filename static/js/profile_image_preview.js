// Script pour prévisualiser l'image de profil lors de l'inscription ou de la modification du profil
document.addEventListener('DOMContentLoaded', function() {
    const profileImageInput = document.querySelector('input[name="profile_picture"]');

    if (profileImageInput) {
        // Créer un conteneur pour la prévisualisation s'il n'existe pas déjà
        let previewContainer = document.querySelector('.profile-image-preview');
        if (!previewContainer) {
            previewContainer = document.createElement('div');
            previewContainer.className = 'profile-image-preview mt-3';
            profileImageInput.parentNode.appendChild(previewContainer);
        }

        // Fonction pour afficher la prévisualisation
        function handleImagePreview(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    previewContainer.innerHTML = `
                        <div class="card mb-3">
                            <div class="card-body text-center">
                                <img src="${event.target.result}" alt="Prévisualisation" class="img-fluid rounded-circle" style="max-height: 150px; max-width: 150px;">
                                <p class="mt-2 mb-0 text-muted">Prévisualisation de votre photo de profil</p>
                            </div>
                        </div>
                    `;
                };
                reader.readAsDataURL(file);
            } else {
                previewContainer.innerHTML = '';
            }
        }

        // Écouter les changements de fichier
        profileImageInput.addEventListener('change', handleImagePreview);
    }
});