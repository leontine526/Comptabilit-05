/**
 * Script pour gérer les réactions à la Facebook sur les publications et commentaires
 */

// Types de réactions disponibles
const REACTION_TYPES = {
    'like': { icon: 'bi-hand-thumbs-up-fill', color: '#0d6efd', text: 'J\'aime' },
    'love': { icon: 'bi-heart-fill', color: '#dc3545', text: 'J\'adore' },
    'haha': { icon: 'bi-emoji-laughing-fill', color: '#fd7e14', text: 'Haha' },
    'wow': { icon: 'bi-emoji-surprise-fill', color: '#ffc107', text: 'Wow' },
    'sad': { icon: 'bi-emoji-frown-fill', color: '#6f42c1', text: 'Triste' },
    'angry': { icon: 'bi-emoji-angry-fill', color: '#d63384', text: 'Grrr' }
};

// Conteneur pour les sélecteurs de réactions
let reactionSelectors = [];

/**
 * Initialise le sélecteur de réactions sur un élément
 * @param {string} targetSelector - Sélecteur CSS pour les boutons de réaction
 */
function initReactionSelectors(targetSelector = '.reaction-button') {
    // Supprime les sélecteurs existants
    reactionSelectors.forEach(selector => {
        if (selector && selector.parentNode) {
            selector.parentNode.removeChild(selector);
        }
    });
    reactionSelectors = [];

    // Sélectionne tous les boutons de réaction
    const reactionButtons = document.querySelectorAll(targetSelector);
    
    reactionButtons.forEach(button => {
        createReactionSelector(button);
        
        // Gestionnaires d'événements pour afficher/masquer le sélecteur
        button.addEventListener('mouseenter', showReactionSelector);
        button.addEventListener('mouseleave', hideReactionSelector);
        
        // Gestionnaire d'événement pour le clic (réaction par défaut - like)
        button.addEventListener('click', function(event) {
            event.preventDefault();
            
            const currentReaction = this.getAttribute('data-current-reaction');
            
            if (currentReaction && currentReaction !== 'like') {
                // Si déjà une réaction non-like, on utilise like
                selectReaction(this, 'like');
            } else if (currentReaction === 'like') {
                // Si déjà like, on retire la réaction
                selectReaction(this, null);
            } else {
                // Sinon, on met like
                selectReaction(this, 'like');
            }
        });
    });
}

/**
 * Crée le sélecteur de réactions pour un bouton
 * @param {HTMLElement} button - Le bouton de réaction
 */
function createReactionSelector(button) {
    // Crée le conteneur
    const selector = document.createElement('div');
    selector.className = 'reaction-selector';
    
    // Ajoute les options de réaction
    Object.keys(REACTION_TYPES).forEach(type => {
        const option = document.createElement('div');
        option.className = 'reaction-option';
        option.setAttribute('data-reaction-type', type);
        option.setAttribute('title', REACTION_TYPES[type].text);
        
        const icon = document.createElement('i');
        icon.className = `bi ${REACTION_TYPES[type].icon}`;
        icon.style.color = REACTION_TYPES[type].color;
        
        option.appendChild(icon);
        selector.appendChild(option);
        
        // Gestionnaire d'événement pour la sélection d'une réaction
        option.addEventListener('click', function(event) {
            event.preventDefault();
            event.stopPropagation();
            selectReaction(button, type);
        });
    });
    
    // Ajoute le sélecteur au DOM
    document.body.appendChild(selector);
    
    // Stocke la référence
    button.setAttribute('data-selector-id', reactionSelectors.length);
    reactionSelectors.push(selector);
}

/**
 * Affiche le sélecteur de réactions
 * @param {Event} event - L'événement de survol
 */
function showReactionSelector(event) {
    const button = event.currentTarget;
    const selectorId = button.getAttribute('data-selector-id');
    
    if (selectorId !== null) {
        const selector = reactionSelectors[selectorId];
        
        // Positionne le sélecteur
        const buttonRect = button.getBoundingClientRect();
        selector.style.left = buttonRect.left + 'px';
        selector.style.bottom = (window.innerHeight - buttonRect.top + 10) + 'px';
        
        // Affiche le sélecteur
        selector.classList.add('active');
        
        // Gestion de la sortie du sélecteur
        selector.addEventListener('mouseenter', () => {
            clearTimeout(selector.hideTimeout);
        });
        
        selector.addEventListener('mouseleave', () => {
            hideReactionSelector({ currentTarget: button });
        });
    }
}

/**
 * Cache le sélecteur de réactions
 * @param {Event} event - L'événement de fin de survol
 */
function hideReactionSelector(event) {
    const button = event.currentTarget;
    const selectorId = button.getAttribute('data-selector-id');
    
    if (selectorId !== null) {
        const selector = reactionSelectors[selectorId];
        
        // Utilise un timeout pour permettre de déplacer la souris vers le sélecteur
        selector.hideTimeout = setTimeout(() => {
            selector.classList.remove('active');
        }, 200);
    }
}

/**
 * Sélectionne une réaction
 * @param {HTMLElement} button - Le bouton de réaction
 * @param {string} reactionType - Le type de réaction (like, love, etc.)
 */
function selectReaction(button, reactionType) {
    // Cache le sélecteur
    const selectorId = button.getAttribute('data-selector-id');
    if (selectorId !== null) {
        const selector = reactionSelectors[selectorId];
        selector.classList.remove('active');
    }
    
    // Met à jour l'apparence du bouton
    updateReactionButton(button, reactionType);
    
    // Détermine si c'est une publication ou un commentaire
    const postId = button.getAttribute('data-post-id');
    const commentId = button.getAttribute('data-comment-id');
    
    // Envoie la réaction au serveur
    const data = { reaction_type: reactionType };
    if (postId) data.post_id = postId;
    if (commentId) data.comment_id = commentId;
    
    fetch('/api/toggle-reaction', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Met à jour le compteur
            updateReactionsCount(button, data.reactions);
            
            // Met à jour l'attribut de réaction actuelle
            button.setAttribute('data-current-reaction', reactionType || '');
        } else {
            console.error('Erreur lors de la réaction:', data.message);
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
    });
}

/**
 * Met à jour l'apparence du bouton de réaction
 * @param {HTMLElement} button - Le bouton de réaction
 * @param {string|null} reactionType - Le type de réaction (like, love, etc.) ou null pour réinitialiser
 */
function updateReactionButton(button, reactionType) {
    // Remet à zéro
    button.classList.remove('reacted');
    const icon = button.querySelector('i');
    icon.className = 'bi bi-hand-thumbs-up';
    icon.style.color = '';
    button.querySelector('span').textContent = 'J\'aime';
    
    // Applique la nouvelle réaction
    if (reactionType && REACTION_TYPES[reactionType]) {
        button.classList.add('reacted');
        icon.className = `bi ${REACTION_TYPES[reactionType].icon}`;
        icon.style.color = REACTION_TYPES[reactionType].color;
        button.querySelector('span').textContent = REACTION_TYPES[reactionType].text;
    }
}

/**
 * Met à jour le compteur de réactions
 * @param {HTMLElement} button - Le bouton de réaction
 * @param {Object} reactions - Les données des réactions
 */
function updateReactionsCount(button, reactions) {
    // Trouve le conteneur de détails de réaction
    let container;
    if (button.getAttribute('data-post-id')) {
        const postId = button.getAttribute('data-post-id');
        container = document.querySelector(`#post-${postId} .reaction-details`);
    } else if (button.getAttribute('data-comment-id')) {
        const commentId = button.getAttribute('data-comment-id');
        container = document.querySelector(`#comment-${commentId} .reaction-details`);
    }
    
    if (!container) return;
    
    // Récupère le nombre total de réactions
    const total = reactions.total || 0;
    
    // Mise à jour simplifiée avec juste le nombre
    if (total > 0) {
        container.textContent = total;
    } else {
        container.textContent = '';
    }
}

// Initialise les réactions au chargement du document
document.addEventListener('DOMContentLoaded', function() {
    initReactionSelectors();
});
/**
 * Script pour la gestion des réactions personnalisées
 */

// Initialisation des réactions disponibles
const availableReactions = [
    { type: 'like', icon: 'bi-hand-thumbs-up-fill', label: 'J\'aime', color: '#2078f4' },
    { type: 'love', icon: 'bi-heart-fill', label: 'J\'adore', color: '#f33e58' },
    { type: 'haha', icon: 'bi-emoji-laughing-fill', label: 'Haha', color: '#f7b125' },
    { type: 'wow', icon: 'bi-emoji-surprise-fill', label: 'Wouah', color: '#f7b125' },
    { type: 'sad', icon: 'bi-emoji-frown-fill', label: 'Triste', color: '#f7b125' },
    { type: 'angry', icon: 'bi-emoji-angry-fill', label: 'Grrr', color: '#e9710f' }
];

// Initialise les sélecteurs de réaction
function initReactionSelectors() {
    // Pour chaque bouton de réaction
    document.querySelectorAll('.reaction-button').forEach(button => {
        // Crée le sélecteur de réactions
        createReactionSelector(button);
        
        // Ajoute l'événement de clic
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Si le bouton a déjà une réaction, l'utiliser directement
            if (this.classList.contains('reacted')) {
                const postId = this.getAttribute('data-post-id');
                const commentId = this.getAttribute('data-comment-id');
                const currentReaction = this.getAttribute('data-current-reaction') || 'like';
                
                // Envoie la requête pour basculer la réaction
                toggleReaction(postId, commentId, currentReaction);
            } else {
                // Sinon, affiche le sélecteur
                const selector = this.nextElementSibling;
                if (selector && selector.classList.contains('reaction-selector')) {
                    selector.classList.toggle('active');
                }
            }
        });
        
        // Ajoute l'événement de survol
        button.addEventListener('mouseenter', function() {
            const selector = this.nextElementSibling;
            if (selector && selector.classList.contains('reaction-selector')) {
                selector.classList.add('active');
            }
        });
        
        // Cache le sélecteur lorsque la souris quitte la zone
        button.parentElement.addEventListener('mouseleave', function() {
            const selector = this.querySelector('.reaction-selector');
            if (selector) {
                selector.classList.remove('active');
            }
        });
    });
}

// Crée un sélecteur de réactions pour un bouton
function createReactionSelector(button) {
    // Vérifie si le sélecteur existe déjà
    if (button.nextElementSibling && button.nextElementSibling.classList.contains('reaction-selector')) {
        return;
    }
    
    // Crée le sélecteur
    const selector = document.createElement('div');
    selector.className = 'reaction-selector';
    
    // Ajoute les options de réaction
    availableReactions.forEach(reaction => {
        const option = document.createElement('div');
        option.className = 'reaction-option';
        option.setAttribute('data-reaction', reaction.type);
        option.setAttribute('title', reaction.label);
        option.innerHTML = `<i class="bi ${reaction.icon}" style="color: ${reaction.color}"></i>`;
        
        // Ajoute l'événement de clic
        option.addEventListener('click', function(e) {
            e.stopPropagation();
            
            const postId = button.getAttribute('data-post-id');
            const commentId = button.getAttribute('data-comment-id');
            const reactionType = this.getAttribute('data-reaction');
            
            // Envoie la requête pour basculer la réaction
            toggleReaction(postId, commentId, reactionType);
            
            // Cache le sélecteur
            selector.classList.remove('active');
        });
        
        selector.appendChild(option);
    });
    
    // Insère le sélecteur après le bouton
    button.parentNode.insertBefore(selector, button.nextSibling);
}

// Fonction pour basculer une réaction
function toggleReaction(postId, commentId, reactionType) {
    // Prépare les données de la requête
    const data = {
        reaction_type: reactionType
    };
    
    if (postId) {
        data.post_id = postId;
    } else if (commentId) {
        data.comment_id = commentId;
    } else {
        console.error('Aucun ID de post ou de commentaire fourni');
        return;
    }
    
    // Envoie la requête
    fetch('/api/reactions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Met à jour l'interface
            updateReactionUI(postId, commentId, reactionType, data.action, data.reactions);
        } else {
            console.error('Erreur lors de la réaction:', data.message);
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
    });
}

// Fonction pour mettre à jour l'interface après une réaction
function updateReactionUI(postId, commentId, reactionType, action, reactions) {
    // Récupère le bouton de réaction
    const button = postId 
        ? document.querySelector(`.reaction-button[data-post-id="${postId}"]`)
        : document.querySelector(`.reaction-button[data-comment-id="${commentId}"]`);
    
    if (!button) return;
    
    // Récupère l'icône et le texte du bouton
    const icon = button.querySelector('i');
    const label = button.querySelector('span');
    
    // Trouve la réaction dans la liste des réactions disponibles
    const reaction = availableReactions.find(r => r.type === reactionType);
    
    if (action === 'removed') {
        // Réinitialise le bouton
        button.classList.remove('reacted');
        button.removeAttribute('data-current-reaction');
        icon.className = 'bi bi-hand-thumbs-up';
        if (label) label.textContent = 'J\'aime';
    } else {
        // Met à jour le bouton avec la nouvelle réaction
        button.classList.add('reacted');
        button.setAttribute('data-current-reaction', reactionType);
        icon.className = `bi ${reaction.icon}`;
        icon.style.color = reaction.color;
        if (label) label.textContent = reaction.label;
    }
    
    // Met à jour le compteur et les détails des réactions
    updateReactionDetails(postId, commentId, reactions);
}

// Fonction pour mettre à jour les détails des réactions
function updateReactionDetails(postId, commentId, reactions) {
    // Identifie le conteneur des détails
    const detailsContainer = postId 
        ? document.querySelector(`#post-${postId} .reaction-details`)
        : document.querySelector(`#comment-${commentId} .reaction-details`);
    
    if (!detailsContainer) return;
    
    // Si pas de réactions, cache les détails
    if (reactions.count === 0) {
        detailsContainer.innerHTML = '';
        return;
    }
    
    // Crée les détails des réactions
    let detailsHTML = `<i class="bi bi-hand-thumbs-up-fill text-primary me-1"></i>${reactions.count}`;
    
    // Si on a des détails par type de réaction, les afficher
    if (reactions.details && Object.keys(reactions.details).length > 0) {
        const typesHTML = Object.entries(reactions.details)
            .map(([type, count]) => {
                const reaction = availableReactions.find(r => r.type === type);
                return `<span class="reaction-type-detail" title="${reaction.label}">
                    <i class="bi ${reaction.icon}" style="color: ${reaction.color}"></i> ${count}
                </span>`;
            })
            .join('');
        
        detailsHTML += ` <span class="reaction-types-details">${typesHTML}</span>`;
    }
    
    detailsContainer.innerHTML = detailsHTML;
}

// Initialise les réactions au chargement du document
document.addEventListener('DOMContentLoaded', function() {
    initReactionSelectors();
});
