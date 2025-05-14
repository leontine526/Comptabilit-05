document.addEventListener('DOMContentLoaded', function() {
    // Animation 3D pour les cartes de fonctionnalités
    const featureCards = document.querySelectorAll('.feature-card');
    
    featureCards.forEach(card => {
        // Ajouter la classe pour l'effet 3D
        card.classList.add('feature-card-3d');
        
        // Effet de rotation sur le survol
        card.addEventListener('mousemove', function(e) {
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const angleX = (y - centerY) / 20;
            const angleY = (centerX - x) / 20;
            
            this.style.transform = `perspective(1000px) rotateX(${angleX}deg) rotateY(${angleY}deg) scale3d(1.05, 1.05, 1.05)`;
            this.style.zIndex = "1";
        });
        
        // Réinitialiser la rotation lorsque la souris quitte la carte
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale3d(1, 1, 1)';
            this.style.zIndex = "0";
        });
    });

    // Animation pour le titre principal
    const heroTitle = document.querySelector('.hero-title');
    if (heroTitle) {
        heroTitle.classList.add('hero-title-3d');
        
        // Animation de rotation lente
        function animateTitle() {
            const now = Date.now() / 1000;
            const angleX = Math.sin(now / 2) * 5;
            const angleY = Math.cos(now / 2) * 5;
            
            heroTitle.style.transform = `perspective(1000px) rotateX(${angleX}deg) rotateY(${angleY}deg)`;
            requestAnimationFrame(animateTitle);
        }
        
        animateTitle();
    }

    // Animation pour l'icône des fonctionnalités
    const featureIcons = document.querySelectorAll('.feature-icon');
    featureIcons.forEach(icon => {
        icon.classList.add('feature-icon-3d');
        
        // Animation de flottement
        function animateIcon(icon) {
            const now = Date.now() / 1000;
            const translateY = Math.sin(now * 2) * 5;
            const rotateZ = Math.sin(now) * 10;
            
            icon.style.transform = `translateY(${translateY}px) rotateZ(${rotateZ}deg)`;
            requestAnimationFrame(() => animateIcon(icon));
        }
        
        animateIcon(icon);
    });
});