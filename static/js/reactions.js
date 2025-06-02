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
        console.error('Erreur lors de l\'envoi de la réaction:', error);
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
        console.error('Erreur lors de l\'envoi de la réaction:', error);
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
    // Gestionnaire pour les boutons de réaction
    const reactionButtons = document.querySelectorAll('.reaction-button');

    // Types de réactions disponibles
    const reactionTypes = [
        { type: 'like', icon: 'fas fa-thumbs-up', label: 'J\'aime' },
        { type: 'love', icon: 'fas fa-heart', label: 'J\'adore' },
        { type: 'haha', icon: 'fas fa-laugh', label: 'Haha' },
        { type: 'wow', icon: 'fas fa-surprise', label: 'Wow' },
        { type: 'sad', icon: 'fas fa-sad-tear', label: 'Triste' },
        { type: 'angry', icon: 'fas fa-angry', label: 'Grrr' }
    ];

    // Générer le menu de réactions
    function createReactionMenu(button) {
        const menu = document.createElement('div');
        menu.classList.add('reaction-menu');

        reactionTypes.forEach(reaction => {
            const reactionItem = document.createElement('button');
            reactionItem.classList.add('reaction-item');
            reactionItem.setAttribute('data-type', reaction.type);
            reactionItem.innerHTML = `<i class="${reaction.icon}"></i>`;
            reactionItem.title = reaction.label;

            reactionItem.addEventListener('click', function(e) {
                e.stopPropagation();
                const type = this.getAttribute('data-type');
                sendReaction(button, type);
                menu.remove();
            });

            menu.appendChild(reactionItem);
        });

        return menu;
    }

    // Afficher le menu de réactions
    reactionButtons.forEach(button => {
        button.addEventListener('mouseenter', function(e) {
            // Vérifier si le menu existe déjà
            if (!document.querySelector('.reaction-menu')) {
                const menu = createReactionMenu(this);
                document.body.appendChild(menu);

                // Positionner le menu au-dessus du bouton
                const rect = this.getBoundingClientRect();
                menu.style.position = 'absolute';
                menu.style.left = `${rect.left}px`;
                menu.style.top = `${rect.top - menu.offsetHeight - 10}px`;

                // Fermer le menu après un délai si on quitte le menu
                menu.addEventListener('mouseleave', function() {
                    setTimeout(() => {
                        if (!menu.matches(':hover') && !button.matches(':hover')) {
                            menu.remove();
                        }
                    }, 500);
                });
            }
        });

        // Gestion du clic simple (réaction par défaut: like)
        button.addEventListener('click', function(e) {
            e.preventDefault();
            sendReaction(this, 'like');
        });
    });

    // Envoyer la réaction au serveur
    function sendReaction(button, reactionType) {
        const postId = button.dataset.postId;
        const commentId = button.dataset.commentId;

        fetch('/api/reactions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({
                post_id: postId,
                comment_id: commentId,
                reaction_type: reactionType
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Mise à jour de l'interface
                updateReactionUI(button, data);
            }
        })
        .catch(error => console.error('Erreur:', error));
    }

    // Mettre à jour l'interface après une réaction
    function updateReactionUI(button, data) {
        // Supprimer toutes les classes de réaction
        reactionTypes.forEach(reaction => {
            button.classList.remove(reaction.type);
        });

        // Ajouter la classe pour le type de réaction actuel
        if (data.action !== 'removed') {
            button.classList.add(data.reactions.current_type || 'like');

/**
 * Affiche une fenêtre modale avec les détails des réactions
 * @param {number} postId - ID de la publication
 */
function showReactions(postId) {
    // Récupère les réactions depuis l'API
    fetch(`/api/posts/${postId}/reactions`)
        .then(response => response.json())
        .then(data => {
            // Créer une modal Bootstrap temporaire
            const modalHtml = `
                <div class="modal fade" id="reactionsModal" tabindex="-1" aria-hidden="true">
                    <div class="modal-dialog modal-dialog-centered">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">Réactions</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body">
                                <ul class="list-group list-group-flush">
                                    ${data.reactions.map(reaction => `
                                        <li class="list-group-item d-flex align-items-center">
                                            <div class="me-3">
                                                <i class="bi ${REACTION_TYPES[reaction.type].icon}" style="color: ${REACTION_TYPES[reaction.type].color}"></i>
                                            </div>
                                            <div>
                                                <div class="fw-bold">${reaction.username}</div>
                                                <small class="text-muted">${reaction.created_at}</small>
                                            </div>
                                        </li>
                                    `).join('')}
                                </ul>
                                ${data.reactions.length === 0 ? '<p class="text-center my-3">Aucune réaction pour le moment</p>' : ''}
                            </div>
                        </div>
                    </div>
                </div>
            `;

            // Ajoute la modal au body
            const modalElement = document.createElement('div');
            modalElement.innerHTML = modalHtml;
            document.body.appendChild(modalElement.firstElementChild);

            // Affiche la modal
            const modal = new bootstrap.Modal(document.getElementById('reactionsModal'));
            modal.show();

            // Supprime la modal quand elle est fermée
            document.getElementById('reactionsModal').addEventListener('hidden.bs.modal', function () {
                this.remove();
            });
        })
        .catch(error => {
            console.error('Erreur lors de la récupération des réactions:', error);
        });
}


            // Mettre à jour l'icône
            const currentReaction = reactionTypes.find(r => r.type === (data.reactions.current_type || 'like'));
            if (currentReaction) {
                const icon = button.querySelector('i');
                if (icon) {
                    icon.className = currentReaction.icon;
                }
            }
        } else {
            // Réinitialiser à l'icône par défaut
            const icon = button.querySelector('i');
            if (icon) {
                icon.className = 'fas fa-thumbs-up';
            }
        }

        // Mettre à jour le compteur
        const counter = button.querySelector('.reaction-count');
        if (counter) {
            counter.textContent = data.reactions.count;
        }

        // Afficher un résumé des réactions
        const summary = button.closest('.post-actions, .comment-actions').querySelector('.reactions-summary');
        if (summary && data.reactions.details) {
            let summaryHTML = '';
            for (const [type, count] of Object.entries(data.reactions.details)) {
                if (count > 0) {
                    const reaction = reactionTypes.find(r => r.type === type);
                    if (reaction) {
                        summaryHTML += `<span class="reaction-badge" title="${count} ${reaction.label}"><i class="${reaction.icon}"></i> ${count}</span>`;
                    }
                }
            }
            summary.innerHTML = summaryHTML;
        }
    }

    // Fermer le menu si on clique ailleurs
    document.addEventListener('click', function() {
        const menu = document.querySelector('.reaction-menu');
        if (menu) {
            menu.remove();
        }
    });
});
// Gestion des réactions (likes, commentaires, partages)
document.addEventListener('DOMContentLoaded', function() {
    // Initialiser les gestionnaires d'événements pour les boutons de réaction
    setupReactionButtons();

    // Gestion des erreurs de réactions
    window.addEventListener('reaction-error', function(e) {
        console.error('Erreur de réaction:', e.detail.message);
        // Réinitialiser l'UI si nécessaire
        if (e.detail.elementId) {
            const element = document.getElementById(e.detail.elementId);
            if (element) {
                element.classList.remove('active', 'liked', 'processing');
                if (e.detail.originalState) {
                    // Rétablir l'état original
                    Object.keys(e.detail.originalState).forEach(key => {
                        element.dataset[key] = e.detail.originalState[key];
                    });
                }
            }
        }

        // Notifier l'utilisateur de manière non intrusive
        showToast('Une erreur est survenue. Veuillez réessayer.', 'error');
    });

    // Système de partage amélioré
    setupSharingSystem();
});

// Afficher un toast de notification
function showToast(message, type = 'info') {
    // Créer l'élément toast s'il n'existe pas
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }

    // Créer le toast
    const toastId = 'toast-' + Date.now();
    const toastHtml = `
        <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header bg-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'info'} text-white">
                <strong class="me-auto">${type === 'error' ? 'Erreur' : type === 'success' ? 'Succès' : 'Information'}</strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;

    // Ajouter le toast au conteneur
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);

    // Initialiser et afficher le toast
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, { delay: 3000 });
    toast.show();

    // Nettoyer le toast après fermeture
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}

// Configuration avancée des boutons de réaction
function setupReactionButtons() {
    // Gestionnaire pour les boutons "J'aime"
    document.querySelectorAll('.btn-like, .reaction-button').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();

            // Vérifier si le bouton est déjà en cours de traitement
            if (this.classList.contains('processing')) {
                return;
            }

            // Marquer comme en traitement
            this.classList.add('processing');

            // Sauvegarder l'état original pour rollback en cas d'erreur
            const originalState = {
                count: this.dataset.count || '0',
                liked: this.dataset.liked || 'false'
            };

            // Optimistic UI update
            const isLiked = this.dataset.liked === 'true';
            const likeCountElement = this.querySelector('.like-count') || this.nextElementSibling;
            let likeCount = parseInt(this.dataset.count || likeCountElement.textContent || '0');

            if (isLiked) {
                likeCount = Math.max(0, likeCount - 1);
                this.classList.remove('liked', 'active');
                this.dataset.liked = 'false';
            } else {
                likeCount++;
                this.classList.add('liked', 'active');
                this.dataset.liked = 'true';
            }

            if (likeCountElement) {
                likeCountElement.textContent = likeCount;
            }
            this.dataset.count = likeCount.toString();

            // Préparer les données
            const postId = this.dataset.postId;
            const commentId = this.dataset.commentId;
            const reactionType = this.dataset.reactionType || 'like';

            // Envoyer la requête au serveur
            fetch('/api/reactions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({
                    post_id: postId,
                    comment_id: commentId,
                    reaction_type: reactionType
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Erreur de réponse du serveur');
                }
                return response.json();
            })
            .then(data => {
                // Mise à jour UI avec les données réelles du serveur
                if (likeCountElement) {
                    likeCountElement.textContent = data.reactions.count;
                }
                this.dataset.count = data.reactions.count.toString();

                // Retirer le marqueur de traitement
                this.classList.remove('processing');
            })
            .catch(error => {
                console.error('Erreur lors de la réaction:', error);

                // Rollback des changements UI
                if (likeCountElement) {
                    likeCountElement.textContent = originalState.count;
                }
                this.classList.remove('processing', 'liked', 'active');
                if (originalState.liked === 'true') {
                    this.classList.add('liked', 'active');
                }
                this.dataset.liked = originalState.liked;
                this.dataset.count = originalState.count;

                // Notifier l'utilisateur
                showToast('Une erreur est survenue lors de la réaction', 'error');

                // Émettre un événement pour la gestion globale des erreurs
                window.dispatchEvent(new CustomEvent('reaction-error', {
                    detail: {
                        message: error.message,
                        elementId: this.id,
                        originalState: originalState
                    }
                }));
            });
        });
    });

    // Gestionnaire de commentaires
    document.querySelectorAll('.comment-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();

            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Envoi...';
            }

            const formData = new FormData(this);
            const content = formData.get('content');
            const postId = formData.get('post_id');
            const commentId = formData.get('parent_id'); // Si c'est une réponse

            // Vérifier que le contenu n'est pas vide
            if (!content || content.trim() === '') {
                if (submitButton) {
                    submitButton.disabled = false;
                    submitButton.innerHTML = 'Commenter';
                }
                showToast('Le commentaire ne peut pas être vide', 'error');
                return;
            }

            // Envoyer au serveur
            fetch('/api/comments/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({
                    content: content,
                    post_id: postId,
                    parent_id: commentId || null
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Erreur lors de l\'envoi du commentaire');
                }
                return response.json();
            })
            .then(data => {
                // Réinitialiser le formulaire
                this.reset();
                if (submitButton) {
                    submitButton.disabled = false;
                    submitButton.innerHTML = 'Commenter';
                }

                // Recharger les commentaires ou ajouter le nouveau commentaire au DOM
                ```text
                reloadComments(postId);

                // Notification
                showToast('Commentaire ajouté avec succès', 'success');
            })
            .catch(error => {
                console.error('Erreur lors de l\'envoi du commentaire:', error);
                if (submitButton) {
                    submitButton.disabled = false;
                    submitButton.innerHTML = 'Commenter';
                }
                showToast('Une erreur est survenue lors de l\'envoi du commentaire', 'error');
            });
        });
    });
}

// Recharger les commentaires d'un post
function reloadComments(postId) {
    const commentsContainer = document.querySelector(`.comments-container[data-post-id="${postId}"]`);
    if (!commentsContainer) return;

    // Afficher un indicateur de chargement
    commentsContainer.innerHTML = '<div class="text-center my-3"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Chargement...</span></div></div>';

    // Récupérer les commentaires
    fetch(`/api/posts/${postId}/comments`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Erreur lors du chargement des commentaires');
            }
            return response.json();
        })
        .then(data => {
            // Vider le conteneur
            commentsContainer.innerHTML = '';

            if (data.comments && data.comments.length > 0) {
                // Ajouter chaque commentaire
                data.comments.forEach(comment => {
                    const commentHtml = createCommentHTML(comment);
                    commentsContainer.insertAdjacentHTML('beforeend', commentHtml);
                });

                // Réinitialiser les gestionnaires d'événements
                setupReactionButtons();
            } else {
                // Aucun commentaire
                commentsContainer.innerHTML = '<p class="text-center text-muted my-3">Aucun commentaire pour le moment. Soyez le premier à commenter !</p>';
            }
        })
        .catch(error => {
            console.error('Erreur lors du chargement des commentaires:', error);
            commentsContainer.innerHTML = '<p class="text-center text-danger my-3">Impossible de charger les commentaires. Veuillez réessayer.</p>';
        });
}

// Créer le HTML d'un commentaire
function createCommentHTML(comment) {
    const isLiked = comment.is_liked_by_user ? 'liked active' : '';
    const likeCount = comment.like_count || 0;

    // Générer les réponses si présentes
    let repliesHtml = '';
    if (comment.replies && comment.replies.length > 0) {
        repliesHtml = '<div class="replies ms-4 mt-2">';
        comment.replies.forEach(reply => {
            repliesHtml += createCommentHTML(reply);
        });
        repliesHtml += '</div>';
    }

    return `
        <div class="comment mb-3" data-comment-id="${comment.id}">
            <div class="d-flex">
                <img src="${comment.user.profile_picture || '/static/images/default-avatar.png'}" class="rounded-circle me-2" width="40" height="40" alt="${comment.user.username}">
                <div class="comment-content w-100">
                    <div class="bg-light p-2 rounded">
                        <div class="d-flex justify-content-between align-items-center">
                            <h6 class="mb-0">${comment.user.username}</h6>
                            <small class="text-muted">${comment.created_at_formatted}</small>
                        </div>
                        <p class="mb-0">${comment.content}</p>
                    </div>
                    <div class="comment-actions mt-1 d-flex">
                        <button class="btn btn-sm btn-link text-decoration-none reaction-button ${isLiked}" 
                                data-comment-id="${comment.id}" 
                                data-liked="${comment.is_liked_by_user ? 'true' : 'false'}" 
                                data-count="${likeCount}">
                            <i class="fas fa-thumbs-up"></i> <span class="like-count">${likeCount}</span>
                        </button>
                        <button class="btn btn-sm btn-link text-decoration-none reply-button" 
                                data-comment-id="${comment.id}">
                            <i class="fas fa-reply"></i> Répondre
                        </button>
                    </div>
                    <div class="reply-form-container d-none mt-2" data-for-comment="${comment.id}">
                        <form class="comment-form">
                            <input type="hidden" name="post_id" value="${comment.post_id}">
                            <input type="hidden" name="parent_id" value="${comment.id}">
                            <div class="input-group">
                                <input type="text" class="form-control form-control-sm" name="content" placeholder="Votre réponse...">
                                <button class="btn btn-sm btn-primary" type="submit">Répondre</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
            ${repliesHtml}
        </div>
    `;
}

// Récupérer le jeton CSRF
function getCSRFToken() {
    const tokenElement = document.querySelector('meta[name="csrf-token"]');
    return tokenElement ? tokenElement.getAttribute('content') : '';
}

// Système de partage amélioré
function setupSharingSystem() {
    document.querySelectorAll('.btn-share').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();

            const postId = this.dataset.postId;
            const shareUrl = this.dataset.shareUrl || window.location.href;
            const shareTitle = this.dataset.shareTitle || document.title;

            // Vérifier si l'API Web Share est disponible
            if (navigator.share) {
                navigator.share({
                    title: shareTitle,
                    url: shareUrl
                }).catch(error => {
                    console.error('Erreur lors du partage:', error);
                    showShareDialog(postId, shareUrl, shareTitle);
                });
            } else {
                showShareDialog(postId, shareUrl, shareTitle);
            }
        });
    });
}

// Afficher un dialogue de partage personnalisé
function showShareDialog(postId, shareUrl, shareTitle) {
    // Créer le dialogue de partage s'il n'existe pas
    let shareDialog = document.getElementById('shareDialog');
    if (!shareDialog) {
        const dialogHtml = `
            <div class="modal fade" id="shareDialog" tabindex="-1" aria-labelledby="shareDialogLabel" aria-hidden="true">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="shareDialogLabel">Partager ce contenu</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Fermer"></button>
                        </div>
                        <div class="modal-body">
                            <div class="d-flex justify-content-center mb-3">
                                <a href="#" class="btn btn-outline-primary mx-1 share-facebook" data-bs-dismiss="modal">
                                    <i class="fab fa-facebook-f"></i>
                                </a>
                                <a href="#" class="btn btn-outline-info mx-1 share-twitter" data-bs-dismiss="modal">
                                    <i class="fab fa-twitter"></i>
                                </a>
                                <a href="#" class="btn btn-outline-success mx-1 share-whatsapp" data-bs-dismiss="modal">
                                    <i class="fab fa-whatsapp"></i>
                                </a>
                                <a href="#" class="btn btn-outline-secondary mx-1 share-email" data-bs-dismiss="modal">
                                    <i class="fas fa-envelope"></i>
                                </a>
                            </div>
                            <div class="input-group mb-3">
                                <input type="text" class="form-control share-url" readonly>
                                <button class="btn btn-outline-secondary copy-url" type="button">Copier</button>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="sharePublishCheckbox">
                                <label class="form-check-label" for="sharePublishCheckbox">
                                    Publier également sur mon profil
                                </label>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fermer</button>
                            <button type="button" class="btn btn-primary publish-share" data-bs-dismiss="modal">Partager</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', dialogHtml);
        shareDialog = document.getElementById('shareDialog');

        // Initialiser le dialogue
        const modal = new bootstrap.Modal(shareDialog);

        // Gestionnaires d'événements pour les boutons de partage
        shareDialog.querySelector('.share-facebook').addEventListener('click', function() {
            window.open(`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(this.dataset.url)}`, '_blank');
        });

        shareDialog.querySelector('.share-twitter').addEventListener('click', function() {
            window.open(`https://twitter.com/intent/tweet?url=${encodeURIComponent(this.dataset.url)}&text=${encodeURIComponent(this.dataset.title)}`, '_blank');
        });

        shareDialog.querySelector('.share-whatsapp').addEventListener('click', function() {
            window.open(`https://api.whatsapp.com/send?text=${encodeURIComponent(this.dataset.title + ' ' + this.dataset.url)}`, '_blank');
        });

        shareDialog.querySelector('.share-email').addEventListener('click', function() {
            window.location.href = `mailto:?subject=${encodeURIComponent(this.dataset.title)}&body=${encodeURIComponent(this.dataset.url)}`;
        });

        // Gestionnaire pour le bouton de copie
        shareDialog.querySelector('.copy-url').addEventListener('click', function() {
            const urlInput = shareDialog.querySelector('.share-url');
            urlInput.select();
            document.execCommand('copy');
            this.textContent = 'Copié !';
            setTimeout(() => {
                this.textContent = 'Copier';
            }, 2000);
        });

        // Gestionnaire pour le bouton de publication
        shareDialog.querySelector('.publish-share').addEventListener('click', function() {
            const publishToProfile = shareDialog.querySelector('#sharePublishCheckbox').checked;
            const postId = this.dataset.postId;

            if (publishToProfile && postId) {
                // Envoyer une requête pour partager sur le profil
                fetch('/api/posts/share', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCSRFToken()
                    },
                    body: JSON.stringify({
                        post_id: postId
                    })
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Erreur lors du partage sur le profil');
                    }
                    return response.json();
                })
                .then(data => {
                    showToast('Publication partagée sur votre profil', 'success');
                })
                .catch(error => {
                    console.error('Erreur lors du partage sur le profil:', error);
                    showToast('Une erreur est survenue lors du partage sur votre profil', 'error');
                });
            }
        });
    }

    // Mettre à jour les données
    shareDialog.querySelector('.share-url').value = shareUrl;
    shareDialog.querySelectorAll('.share-facebook, .share-twitter, .share-whatsapp, .share-email').forEach(element => {
        element.dataset.url = shareUrl;
        element.dataset.title = shareTitle;
    });
    shareDialog.querySelector('.publish-share').dataset.postId = postId;

    // Afficher le dialogue
    const modal = new bootstrap.Modal(shareDialog);
    modal.show();
}


            // Mettre à jour l'icône
            const currentReaction = reactionTypes.find(r => r.type === (data.reactions.current_type || 'like'));
            if (currentReaction) {
                const icon = button.querySelector('i');
                if (icon) {
                    icon.className = currentReaction.icon;
                }
            }
        } else {
            // Réinitialiser à l'icône par défaut
            const icon = button.querySelector('i');
            if (icon) {
                icon.className = 'fas fa-thumbs-up';
            }
        }

        // Mettre à jour le compteur
        const counter = button.querySelector('.reaction-count');
        if (counter) {
            counter.textContent = data.reactions.count;
        }

        // Afficher un résumé des réactions
        const summary = button.closest('.post-actions, .comment-actions').querySelector('.reactions-summary');
        if (summary && data.reactions.details) {
            let summaryHTML = '';
            for (const [type, count] of Object.entries(data.reactions.details)) {
                if (count > 0) {
                    const reaction = reactionTypes.find(r => r.type === type);
                    if (reaction) {
                        summaryHTML += `<span class="reaction-badge" title="${count} ${reaction.label}"><i class="${reaction.icon}"></i> ${count}</span>`;
                    }
                }
            }
            summary.innerHTML = summaryHTML;
        }
    }

    // Fermer le menu si on clique ailleurs
    document.addEventListener('click', function() {
        const menu = document.querySelector('.reaction-menu');
        if (menu) {
            menu.remove();
        }
    });
});