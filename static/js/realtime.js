/**
 * Script pour la gestion des fonctionnalités en temps réel
 */

// Références globales
let socket = null;
let currentUserId = null;
let typingTimeout = null;
let notificationSound = null;
let onlineUsers = {};
let currentChatRoom = null;

/**
 * Initialise la connexion Socket.IO et configure les gestionnaires d'événements
 * @param {number} userId - L'ID de l'utilisateur connecté
 */
function initializeSocketIO(userId) {
    // Stocke l'ID utilisateur
    currentUserId = userId;
    
    // Initialise le son de notification
    initNotificationSound();
    
    // Initialise la connexion Socket.IO
    socket = io();
    
    // Gestionnaires d'événements pour la connexion
    socket.on('connect', handleConnect);
    socket.on('disconnect', handleDisconnect);
    
    // Gestionnaires d'événements pour les utilisateurs en ligne
    socket.on('user_connected', handleUserConnected);
    socket.on('user_disconnected', handleUserDisconnected);
    socket.on('online_users', handleOnlineUsers);
    
    // Gestionnaires d'événements pour les messages
    socket.on('chat_message', handleChatMessage);
    socket.on('typing', handleTyping);
    
    // Gestionnaires d'événements pour les notifications
    socket.on('notification', handleNotification);
    
    // Gestionnaire pour les mises à jour du feed social
    socket.on('new_post', handleNewPost);
    socket.on('new_comment', handleNewComment);
    socket.on('new_reaction', handleNewReaction);
    socket.on('new_story', handleNewStory);
    socket.on('story_view', handleStoryView);
}

/**
 * Initialise le son de notification
 */
function initNotificationSound() {
    notificationSound = new Audio('/static/sounds/notification.wav');
    notificationSound.volume = 0.5;
}

/**
 * Gère l'événement de connexion Socket.IO
 */
function handleConnect() {
    console.log('Connecté au serveur Socket.IO');
    
    // Si on est dans un chat, rejoindre la salle
    const chatContainer = document.querySelector('.chat-container');
    if (chatContainer) {
        const roomId = chatContainer.getAttribute('data-room-id');
        if (roomId) {
            joinChatRoom(roomId);
        }
    }
}

/**
 * Gère l'événement de déconnexion Socket.IO
 */
function handleDisconnect() {
    console.log('Déconnecté du serveur Socket.IO');
    
    // Tentative de reconnexion
    if (socket) {
        setTimeout(() => {
            if (socket.disconnected) {
                socket.connect();
            }
        }, 2000);
    }
}

/**
 * Rejoint une salle de chat
 * @param {string} roomId - L'ID de la salle de chat à rejoindre
 */
function joinChatRoom(roomId) {
    if (socket && roomId) {
        currentChatRoom = roomId;
        socket.emit('join_room', { room: roomId });
        console.log(`Salle de chat rejointe: ${roomId}`);
    }
}

/**
 * Gère l'événement d'un utilisateur connecté
 * @param {Object} data - Les données de l'utilisateur connecté
 */
function handleUserConnected(data) {
    console.log(`Utilisateur connecté: ${data.username} (ID: ${data.user_id})`);
    
    // Met à jour la liste des utilisateurs en ligne
    onlineUsers[data.user_id] = data;
    updateOnlineUserIndicators();
    
    // Affiche une notification toast
    if (data.user_id != currentUserId) {
        showToast(`${data.username} est maintenant en ligne`, 'info');
    }
}

/**
 * Gère l'événement d'un utilisateur déconnecté
 * @param {Object} data - Les données de l'utilisateur déconnecté
 */
function handleUserDisconnected(data) {
    console.log(`Utilisateur déconnecté: ${data.username} (ID: ${data.user_id})`);
    
    // Supprime l'utilisateur de la liste
    if (onlineUsers[data.user_id]) {
        delete onlineUsers[data.user_id];
        updateOnlineUserIndicators();
    }
}

/**
 * Gère l'événement de réception de la liste des utilisateurs en ligne
 * @param {Object} data - Les données des utilisateurs en ligne
 */
function handleOnlineUsers(data) {
    console.log('Liste des utilisateurs en ligne reçue:', data.users.length);
    
    // Met à jour la liste des utilisateurs en ligne
    onlineUsers = {};
    data.users.forEach(user => {
        onlineUsers[user.user_id] = user;
    });
    
    // Met à jour les indicateurs
    updateOnlineUserIndicators();
    
    // Met à jour le compteur
    const onlineCount = document.getElementById('online-count');
    if (onlineCount) {
        onlineCount.textContent = data.users.length;
    }
    
    // Met à jour la liste des utilisateurs en ligne
    updateOnlineUsersList(data.users);
}

/**
 * Met à jour les indicateurs de statut en ligne pour tous les utilisateurs
 */
function updateOnlineUserIndicators() {
    // Sélectionne tous les indicateurs de statut
    document.querySelectorAll('.user-status-indicator').forEach(indicator => {
        const userId = indicator.getAttribute('data-user-id');
        
        // Met à jour le statut
        if (userId && onlineUsers[userId]) {
            indicator.classList.remove('text-secondary');
            indicator.classList.add('text-success');
            indicator.setAttribute('title', 'En ligne');
        } else {
            indicator.classList.remove('text-success');
            indicator.classList.add('text-secondary');
            indicator.setAttribute('title', 'Hors ligne');
        }
    });
}

/**
 * Met à jour la liste des utilisateurs en ligne dans le feed
 * @param {Array} users - La liste des utilisateurs en ligne
 */
function updateOnlineUsersList(users) {
    const usersList = document.getElementById('online-users-list');
    if (!usersList) return;
    
    // Vide la liste
    usersList.innerHTML = '';
    
    if (users.length === 0) {
        usersList.innerHTML = `
            <li class="list-group-item text-center text-muted py-3">
                Aucun utilisateur en ligne
            </li>
        `;
        return;
    }
    
    // Ajoute chaque utilisateur à la liste
    users.forEach(user => {
        const userItem = document.createElement('li');
        userItem.className = 'list-group-item online-user-item';
        userItem.innerHTML = `
            <div class="d-flex align-items-center">
                <div class="avatar me-2">
                    <span class="avatar-initial rounded-circle bg-primary">
                        ${user.username.charAt(0).toUpperCase()}
                    </span>
                </div>
                <div class="flex-grow-1">
                    <div class="d-flex justify-content-between align-items-center">
                        <span>${user.username}</span>
                        <span class="user-status-indicator text-success" data-user-id="${user.user_id}" title="En ligne">
                            <i class="bi bi-circle-fill"></i>
                        </span>
                    </div>
                </div>
            </div>
        `;
        usersList.appendChild(userItem);
    });
}

/**
 * Gère l'événement de réception d'un message de chat
 * @param {Object} data - Les données du message
 */
function handleChatMessage(data) {
    console.log(`Message reçu de ${data.username}:`, data.message);
    
    // Si nous sommes dans la page de chat
    const messagesContainer = document.getElementById('chat-messages');
    if (messagesContainer && currentChatRoom === data.room) {
        // Crée l'élément de message
        const messageElement = document.createElement('div');
        messageElement.className = `chat-message ${data.user_id == currentUserId ? 'chat-message-out' : 'chat-message-in'}`;
        
        // Format du message
        messageElement.innerHTML = `
            <div class="message-avatar">
                <div class="avatar ${data.user_id == currentUserId ? 'bg-primary' : 'bg-secondary'}">
                    <span class="avatar-initial">${data.username.charAt(0).toUpperCase()}</span>
                </div>
            </div>
            <div class="message-content">
                <div class="message-text">${data.message}</div>
                <div class="message-time">
                    <small class="text-muted">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</small>
                </div>
            </div>
        `;
        
        // Ajoute le message au conteneur
        messagesContainer.appendChild(messageElement);
        
        // Fait défiler vers le bas
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        // Joue le son de notification si le message est d'un autre utilisateur
        if (data.user_id != currentUserId) {
            playNotificationSound();
        }
    } else if (data.user_id != currentUserId) {
        // Si nous ne sommes pas dans la page de chat, affiche une notification toast
        showToast(`Nouveau message de ${data.username}`, 'info');
        playNotificationSound();
    }
}

/**
 * Gère l'événement de frappe au clavier
 * @param {Object} data - Les données de frappe
 */
function handleTyping(data) {
    // Gère l'indicateur de frappe dans le chat
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator && currentChatRoom === data.room && data.user_id != currentUserId) {
        typingIndicator.textContent = `${data.username} est en train d'écrire...`;
        typingIndicator.style.display = 'block';
        
        // Cache l'indicateur après un délai
        setTimeout(() => {
            typingIndicator.style.display = 'none';
        }, 3000);
    }
}

/**
 * Gère l'événement de réception d'une notification
 * @param {Object} data - Les données de la notification
 */
function handleNotification(data) {
    console.log('Notification reçue:', data);
    
    // Joue le son de notification
    playNotificationSound();
    
    // Affiche une notification toast
    showToast(data.title, 'info');
    
    // Met à jour le compteur de notifications
    updateNotificationCount(1);
    
    // Si nous sommes sur la page de notifications, met à jour la liste
    const notificationsContainer = document.getElementById('notifications-container');
    if (notificationsContainer) {
        // Recharge la page pour afficher la nouvelle notification
        window.location.reload();
    }
}

/**
 * Met à jour le compteur de notifications
 * @param {number} increment - Le nombre à ajouter
 */
function updateNotificationCount(increment) {
    const badge = document.querySelector('.navbar .nav-item .badge');
    if (badge) {
        const count = parseInt(badge.textContent) || 0;
        badge.textContent = count + increment;
        
        // Affiche ou masque le badge
        if (count + increment > 0) {
            badge.classList.remove('d-none');
        } else {
            badge.classList.add('d-none');
        }
    }
}

/**
 * Envoie un message de chat
 * @param {string} message - Le message à envoyer
 * @param {string} roomId - L'ID de la salle de chat
 */
function sendChatMessage(message, roomId) {
    if (socket && message.trim() && roomId) {
        socket.emit('chat_message', {
            message: message,
            room: roomId
        });
        return true;
    }
    return false;
}

/**
 * Envoie un événement de frappe au clavier
 * @param {string} roomId - L'ID de la salle de chat
 */
function sendTypingEvent(roomId) {
    if (socket && roomId) {
        // Évite d'envoyer l'événement trop souvent
        clearTimeout(typingTimeout);
        typingTimeout = setTimeout(() => {
            socket.emit('typing', { room: roomId });
        }, 300);
    }
}

/**
 * Joue le son de notification
 */
function playNotificationSound() {
    if (notificationSound) {
        notificationSound.play().catch(err => {
            console.error('Erreur lors de la lecture du son:', err);
        });
    }
}

/**
 * Affiche une notification toast
 * @param {string} message - Le message à afficher
 * @param {string} type - Le type de notification (info, success, warning, danger)
 */
function showToast(message, type = 'info') {
    // Vérifie si le conteneur existe, sinon le crée
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container';
        document.body.appendChild(toastContainer);
    }
    
    // Crée le toast
    const toastElement = document.createElement('div');
    toastElement.className = `toast social-toast bg-${type} text-white fade show`;
    toastElement.setAttribute('role', 'alert');
    toastElement.setAttribute('aria-live', 'assertive');
    toastElement.setAttribute('aria-atomic', 'true');
    
    // Contenu du toast
    toastElement.innerHTML = `
        <div class="toast-header bg-${type} text-white">
            <strong class="me-auto">Notification</strong>
            <small>à l'instant</small>
            <button type="button" class="btn-close btn-close-white ms-2" data-bs-dismiss="toast" aria-label="Fermer"></button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;
    
    // Ajoute le toast au conteneur
    toastContainer.appendChild(toastElement);
    
    // Initialise le toast avec Bootstrap
    const toast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: 5000
    });
    
    // Affiche le toast
    toast.show();
    
    // Supprime le toast du DOM après qu'il se soit caché
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}

/**
 * Gère la réception d'une nouvelle publication
 * @param {Object} data - Les données de la publication
 */
function handleNewPost(data) {
    console.log('Nouvelle publication reçue:', data);
    
    // Si nous sommes sur la page de feed, intègre la nouvelle publication
    const postsContainer = document.getElementById('posts-container');
    if (postsContainer) {
        // Recharge la page ou ajoute dynamiquement la publication
        if (data.author_id != currentUserId) {
            showToast(`Nouvelle publication de ${data.author_username}`, 'info');
            playNotificationSound();
        }
    }
}

/**
 * Gère la réception d'un nouveau commentaire
 * @param {Object} data - Les données du commentaire
 */
function handleNewComment(data) {
    console.log('Nouveau commentaire reçu:', data);
    
    // Si nous sommes sur la page de feed, met à jour le post concerné
    const commentsContainer = document.getElementById(`comments-${data.post_id}`);
    if (commentsContainer) {
        // Recharge la page ou ajoute dynamiquement le commentaire
        if (data.author_id != currentUserId) {
            showToast(`Nouveau commentaire de ${data.author_username}`, 'info');
            playNotificationSound();
        }
    }
}

/**
 * Gère la réception d'une nouvelle réaction
 * @param {Object} data - Les données de la réaction
 */
function handleNewReaction(data) {
    console.log('Nouvelle réaction reçue:', data);
    
    // Si la réaction concerne une de nos publications et n'est pas de nous
    if (data.post_author_id == currentUserId && data.user_id != currentUserId) {
        showToast(`${data.username} a réagi à votre publication`, 'info');
        playNotificationSound();
    }
    
    // Si la réaction concerne un de nos commentaires et n'est pas de nous
    if (data.comment_author_id == currentUserId && data.user_id != currentUserId) {
        showToast(`${data.username} a réagi à votre commentaire`, 'info');
        playNotificationSound();
    }
}

/**
 * Gère la réception d'une nouvelle story
 * @param {Object} data - Les données de la story
 */
function handleNewStory(data) {
    console.log('Nouvelle story reçue:', data);
    
    // Si nous sommes sur la page de stories, met à jour la liste
    const storiesContainer = document.querySelector('.stories-container');
    if (storiesContainer) {
        // Recharge la page ou ajoute dynamiquement la story
        if (data.author.id != currentUserId) {
            showToast(`Nouvelle story de ${data.author.username}`, 'info');
            playNotificationSound();
        }
    }
}

/**
 * Crée une publication
 * @param {string} content - Le contenu de la publication
 * @param {string} workgroupId - L'ID du groupe de travail (optionnel)
 * @param {string} imageUrl - L'URL de l'image (optionnel)
 * @param {string} fileUrl - L'URL du fichier (optionnel)
 */
function createPost(content, workgroupId = null, imageUrl = null, fileUrl = null) {
    const data = { content };
    
    if (workgroupId) data.workgroup_id = workgroupId;
    if (imageUrl) data.image_url = imageUrl;
    if (fileUrl) data.file_url = fileUrl;
    
    fetch('/api/posts/create', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Publication créée avec succès', 'success');
            
            // Recharge la page pour afficher la nouvelle publication
            setTimeout(() => window.location.reload(), 1000);
        } else {
            showToast('Erreur lors de la création de la publication: ' + data.message, 'danger');
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        showToast('Erreur de connexion lors de la création de la publication', 'danger');
    });
}

/**
 * Ajoute un commentaire à une publication
 * @param {number} postId - L'ID de la publication
 * @param {number} replyToId - L'ID du commentaire auquel on répond (optionnel)
 */
function addComment(postId, replyToId = null) {
    const inputElement = document.getElementById(`comment-input-${postId}`);
    const content = inputElement.value.trim();
    
    if (content) {
        const data = {
            post_id: postId,
            content
        };
        
        if (replyToId) {
            data.parent_id = replyToId;
        }
        
        fetch('/api/comments/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Réinitialise l'input
                inputElement.value = '';
                inputElement.placeholder = 'Écrire un commentaire...';
                inputElement.removeAttribute('data-reply-to');
                
                // Recharge la page pour afficher le nouveau commentaire
                window.location.reload();
            } else {
                showToast('Erreur lors de l\'ajout du commentaire: ' + data.message, 'danger');
            }
        })
        .catch(error => {
            console.error('Erreur:', error);
            showToast('Erreur de connexion lors de l\'ajout du commentaire', 'danger');
        });
    }
}

/**
 * Met le focus sur la zone de commentaire
 * @param {number} postId - L'ID de la publication
 */
function focusCommentBox(postId) {
    const inputElement = document.getElementById(`comment-input-${postId}`);
    if (inputElement) {
        inputElement.focus();
    }
}

/**
 * Gère la notification qu'un utilisateur a vu une story
 * @param {Object} data - Les données de la vue de story
 */
function handleStoryView(data) {
    console.log('Story vue par:', data);
    
    // Si nous sommes sur la page de stories et que c'est notre story
    const storyViewers = document.querySelector(`#story-viewers-${data.story_id}`);
    if (storyViewers) {
        // Ajoute le nouveau spectateur à la liste
        const viewerItem = document.createElement('div');
        viewerItem.className = 'story-viewer-item';
        viewerItem.innerHTML = `
            <div class="d-flex align-items-center mb-2">
                <div class="avatar me-2">
                    <span class="avatar-initial rounded-circle bg-secondary">
                        ${data.viewer.username.charAt(0).toUpperCase()}
                    </span>
                </div>
                <div class="flex-grow-1">
                    <div class="d-flex justify-content-between align-items-center">
                        <span>${data.viewer.username}</span>
                        <small class="text-muted">${data.viewed_at}</small>
                    </div>
                </div>
            </div>
        `;
        storyViewers.appendChild(viewerItem);
        
        // Met à jour le compteur de vues
        const viewCount = document.querySelector(`#story-view-count-${data.story_id}`);
        if (viewCount) {
            viewCount.textContent = parseInt(viewCount.textContent || '0') + 1;
        }
    }
}