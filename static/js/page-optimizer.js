
/**
 * Script d'optimisation de chargement des pages
 * Implémente un chargement différé des images et ressources non critiques
 */
document.addEventListener('DOMContentLoaded', function() {
    // Lazy loading des images
    const lazyImages = document.querySelectorAll('img[data-src]');
    const lazyImageObserver = new IntersectionObserver(function(entries, observer) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.getAttribute('data-src');
                img.removeAttribute('data-src');
                lazyImageObserver.unobserve(img);
            }
        });
    });
    
    lazyImages.forEach(function(image) {
        lazyImageObserver.observe(image);
    });
    
    // Préchargement des pages sur hover pour navigation instantanée
    const pageLinks = document.querySelectorAll('a[data-preload]');
    pageLinks.forEach(link => {
        link.addEventListener('mouseenter', () => {
            const url = link.getAttribute('href');
            if (url && !url.startsWith('#') && !url.startsWith('javascript:')) {
                const prefetchLink = document.createElement('link');
                prefetchLink.rel = 'prefetch';
                prefetchLink.href = url;
                document.head.appendChild(prefetchLink);
            }
        });
    });
    
    // Détection de la connexion réseau
    if ('connection' in navigator) {
        const connection = navigator.connection;
        if (connection.saveData) {
            // Mode économie de données activé
            document.body.classList.add('save-data-mode');
        }
        
        // Adaptation selon la qualité de connexion
        if (connection.effectiveType === 'slow-2g' || connection.effectiveType === '2g') {
            document.body.classList.add('slow-connection');
        }
    }
    
    // Surveillance des performances
    window.addEventListener('load', function() {
        if ('performance' in window) {
            const performanceData = {
                // Navigation Timing API
                pageLoadTime: window.performance.timing.loadEventEnd - window.performance.timing.navigationStart,
                dnsTime: window.performance.timing.domainLookupEnd - window.performance.timing.domainLookupStart,
                tcpTime: window.performance.timing.connectEnd - window.performance.timing.connectStart,
                serverTime: window.performance.timing.responseEnd - window.performance.timing.requestStart,
                domProcessingTime: window.performance.timing.domComplete - window.performance.timing.domLoading,
                // Paint Timing API
                firstPaint: window.performance.getEntriesByType('paint')
                    .find(entry => entry.name === 'first-paint')?.startTime || 0,
                firstContentfulPaint: window.performance.getEntriesByType('paint')
                    .find(entry => entry.name === 'first-contentful-paint')?.startTime || 0
            };
            
            // Log des données de performance (pourrait être envoyé à un service d'analytics)
            console.debug('Performance:', performanceData);
        }
    });
});
