// Fonction pour prévisualiser l'image de profil avant upload
document.addEventListener('DOMContentLoaded', function() {
    const profilePictureInput = document.querySelector('input[name="profile_picture"]');

    if (profilePictureInput) {
        // Créer la div de prévisualisation si elle n'existe pas déjà
        let previewContainer = document.getElementById('profile-preview-container');
        if (!previewContainer) {
            previewContainer = document.createElement('div');
            previewContainer.id = 'profile-preview-container';
            previewContainer.className = 'text-center mb-3 mt-2';
            profilePictureInput.parentNode.appendChild(previewContainer);
        }

        // Ajouter un texte d'aide
        const helpText = document.createElement('small');
        helpText.className = 'form-text text-muted mt-1';
        helpText.textContent = 'Formats acceptés: JPG, PNG, JPEG. Taille max: 5MB';
        profilePictureInput.parentNode.appendChild(helpText);

        // Prévisualiser l'image sélectionnée
        profilePictureInput.addEventListener('change', function(event) {
            const file = event.target.files[0];
            if (file) {
                // Vérifier si c'est une image
                if (!file.type.match('image.*')) {
                    alert('Veuillez sélectionner une image valide.');
                    return;
                }

                // Créer la prévisualisation
                const reader = new FileReader();
                reader.onload = function(e) {
                    previewContainer.innerHTML = '';
                    const img = document.createElement('img');
                    img.src = e.target.result;
                    img.className = 'img-thumbnail rounded-circle';
                    img.style.width = '150px';
                    img.style.height = '150px';
                    img.style.objectFit = 'cover';
                    previewContainer.appendChild(img);
                };
                reader.readAsDataURL(file);
            } else {
                previewContainer.innerHTML = '';
            }
        });
    }
});