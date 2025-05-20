
// Script pour améliorer l'expérience responsive

document.addEventListener('DOMContentLoaded', function() {
  const navbarCollapse = document.querySelector('.navbar-collapse');
  const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
  
  // Fermer le menu sur mobile quand un lien est cliqué
  navLinks.forEach(link => {
    link.addEventListener('click', () => {
      if (window.innerWidth < 992 && navbarCollapse.classList.contains('show')) {
        document.querySelector('.navbar-toggler').click();
      }
    });
  });
  
  // Ajuster la hauteur des cartes dans une rangée pour qu'elles soient égales
  function equalizeCardHeights() {
    // Ne pas exécuter sur mobile
    if (window.innerWidth < 768) return;
    
    const cardRows = document.querySelectorAll('.row');
    
    cardRows.forEach(row => {
      const cards = row.querySelectorAll('.card');
      if (cards.length <= 1) return;
      
      // Réinitialiser les hauteurs
      cards.forEach(card => card.style.height = 'auto');
      
      // Trouver la hauteur maximale
      let maxHeight = 0;
      cards.forEach(card => {
        maxHeight = Math.max(maxHeight, card.offsetHeight);
      });
      
      // Appliquer la hauteur max à toutes les cartes
      cards.forEach(card => card.style.height = maxHeight + 'px');
    });
  }
  
  // Exécuter après le chargement et au redimensionnement
  equalizeCardHeights();
  window.addEventListener('resize', equalizeCardHeights);
  
  // Détecter l'orientation de l'appareil
  window.addEventListener('orientationchange', function() {
    // Petit délai pour permettre au navigateur de s'ajuster
    setTimeout(equalizeCardHeights, 300);
  });
});
