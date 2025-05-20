
/**
 * Module de gestion des événements en temps réel amélioré
 * Gère les WebSockets avec reconnexion automatique et mise en cache
 */
class RealtimeManager {
    constructor(options = {}) {
        this.options = Object.assign({
            reconnectAttempts: 5,
            reconnectDelay: 2000,
            exponentialBackoff: true,
            debug: false,
            heartbeatInterval: 30000,
            cacheSize: 50,
            useLocal: true
        }, options);
        
        this.socket = null;
        this.connected = false;
        this.reconnectAttempt = 0;
        this.eventHandlers = {};
        this.messageCache = [];
        this.pendingMessages = [];
        this.heartbeatTimer = null;
        
        // Vérifier la prise en charge
        this.hasSocketSupport = 'io' in window;
        this.hasLocalStorageSupport = 'localStorage' in window;
        
        // État de la connexion réseau
        this.onlineStatus = navigator.onLine;
        window.addEventListener('online', () => this.handleNetworkChange(true));
        window.addEventListener('offline', () => this.handleNetworkChange(false));
        
        // Initialiser le stockage local si disponible
        if (this.hasLocalStorageSupport && this.options.useLocal) {
            try {
                this.loadCachedMessages();
            } catch (e) {
                console.error('Erreur lors du chargement des messages en cache:', e);
                localStorage.removeItem('realtimeMessageCache');
            }
        }
    }
    
    /**
     * Initialise la connexion WebSocket
     */
    connect() {
        if (!this.hasSocketSupport) {
            console.warn('WebSocket non supporté par ce navigateur');
            return false;
        }
        
        try {
            this.socket = io();
            
            // Gestionnaires d'événements
            this.socket.on('connect', () => this.handleConnect());
            this.socket.on('disconnect', () => this.handleDisconnect());
            this.socket.on('error', (error) => this.handleError(error));
            this.socket.on('reconnect_failed', () => this.handleReconnectFailed());
            
            // Gestionnaire générique pour tous les événements
            this.socket.onAny((eventName, ...args) => {
                this.handleEvent(eventName, ...args);
            });
            
            return true;
        } catch (e) {
            console.error('Erreur lors de l\'initialisation WebSocket:', e);
            return false;
        }
    }
    
    /**
     * Gère la connexion établie
     */
    handleConnect() {
        this.connected = true;
        this.reconnectAttempt = 0;
        
        // Démarrer le heartbeat
        this.startHeartbeat();
        
        // Traiter les messages en attente
        this.processPendingMessages();
        
        // Notifier l'interface
        this.log('WebSocket connecté');
        document.body.classList.remove('websocket-disconnected');
        document.body.classList.add('websocket-connected');
        
        // Déclencher l'événement personnalisé
        window.dispatchEvent(new CustomEvent('websocket-connected'));
    }
    
    /**
     * Gère la déconnexion
     */
    handleDisconnect() {
        this.connected = false;
        this.stopHeartbeat();
        
        this.log('WebSocket déconnecté');
        document.body.classList.remove('websocket-connected');
        document.body.classList.add('websocket-disconnected');
        
        // Tenter une reconnexion si en ligne
        if (this.onlineStatus && this.reconnectAttempt < this.options.reconnectAttempts) {
            this.scheduleReconnect();
        }
        
        // Déclencher l'événement personnalisé
        window.dispatchEvent(new CustomEvent('websocket-disconnected'));
    }
    
    /**
     * Gère les erreurs WebSocket
     */
    handleError(error) {
        this.log('Erreur WebSocket:', error, 'error');
        
        // Afficher une notification si c'est une erreur critique
        if (error && error.code >= 500) {
            this.showNotification('Erreur de communication avec le serveur', 'error');
        }
        
        // Déclencher l'événement personnalisé
        window.dispatchEvent(new CustomEvent('websocket-error', { detail: error }));
    }
    
    /**
     * Gère l'échec de reconnexion
     */
    handleReconnectFailed() {
        this.log('Échec de reconnexion après plusieurs tentatives', 'warn');
        this.showNotification('Impossible de se connecter au serveur. Veuillez rafraîchir la page.', 'error', true);
    }
    
    /**
     * Programme une tentative de reconnexion
     */
    scheduleReconnect() {
        this.reconnectAttempt++;
        
        // Calculer le délai avec backoff exponentiel si activé
        let delay = this.options.reconnectDelay;
        if (this.options.exponentialBackoff) {
            delay = delay * Math.pow(2, this.reconnectAttempt - 1);
        }
        
        this.log(`Tentative de reconnexion ${this.reconnectAttempt}/${this.options.reconnectAttempts} dans ${delay}ms`);
        
        setTimeout(() => {
            if (!this.connected) {
                this.connect();
            }
        }, delay);
    }
    
    /**
     * Gère les changements d'état du réseau
     */
    handleNetworkChange(isOnline) {
        this.onlineStatus = isOnline;
        
        if (isOnline) {
            this.log('Connexion réseau rétablie');
            
            // Tenter de se reconnecter
            if (!this.connected) {
                this.reconnectAttempt = 0;
                this.connect();
            }
        } else {
            this.log('Connexion réseau perdue', 'warn');
            
            // Mettre à jour l'interface
            document.body.classList.remove('websocket-connected');
            document.body.classList.add('websocket-disconnected');
            
            // Arrêter le heartbeat
            this.stopHeartbeat();
        }
    }
    
    /**
     * Gère les événements reçus
     */
    handleEvent(eventName, ...args) {
        // Ne pas traiter les événements système
        if (eventName === 'connect' || eventName === 'disconnect' || eventName === 'error') {
            return;
        }
        
        this.log(`Événement reçu: ${eventName}`, 'debug');
        
        // Mettre en cache si nécessaire
        if (this.shouldCacheEvent(eventName)) {
            this.cacheMessage(eventName, args);
        }
        
        // Déclencher les gestionnaires pour cet événement
        if (this.eventHandlers[eventName]) {
            this.eventHandlers[eventName].forEach(handler => {
                try {
                    handler(...args);
                } catch (e) {
                    console.error(`Erreur dans le gestionnaire pour ${eventName}:`, e);
                }
            });
        }
    }
    
    /**
     * Détermine si un événement doit être mis en cache
     */
    shouldCacheEvent(eventName) {
        // Liste des événements à mettre en cache
        const cacheableEvents = [
            'user_status_change',
            'new_notification',
            'new_message',
            'new_post',
            'reaction_update'
        ];
        
        return cacheableEvents.includes(eventName);
    }
    
    /**
     * Met un message en cache
     */
    cacheMessage(eventName, data) {
        const message = {
            id: Date.now() + Math.random().toString(36).substr(2, 5),
            event: eventName,
            data: data,
            timestamp: Date.now()
        };
        
        // Ajouter au cache en mémoire
        this.messageCache.push(message);
        
        // Limiter la taille du cache
        if (this.messageCache.length > this.options.cacheSize) {
            this.messageCache.shift();
        }
        
        // Sauvegarder dans localStorage si disponible
        if (this.hasLocalStorageSupport && this.options.useLocal) {
            try {
                localStorage.setItem('realtimeMessageCache', JSON.stringify(this.messageCache));
            } catch (e) {
                console.error('Erreur lors de la sauvegarde du cache:', e);
            }
        }
    }
    
    /**
     * Charge les messages en cache depuis localStorage
     */
    loadCachedMessages() {
        if (this.hasLocalStorageSupport && this.options.useLocal) {
            const cachedData = localStorage.getItem('realtimeMessageCache');
            if (cachedData) {
                this.messageCache = JSON.parse(cachedData);
                
                // Nettoyer les messages trop anciens (plus de 1 jour)
                const oneDayAgo = Date.now() - (24 * 60 * 60 * 1000);
                this.messageCache = this.messageCache.filter(msg => msg.timestamp > oneDayAgo);
                
                // Limiter à la taille maximale
                if (this.messageCache.length > this.options.cacheSize) {
                    this.messageCache = this.messageCache.slice(-this.options.cacheSize);
                }
                
                this.log(`${this.messageCache.length} messages chargés depuis le cache local`);
            }
        }
    }
    
    /**
     * Ajoute un gestionnaire pour un événement
     */
    on(eventName, callback) {
        if (!this.eventHandlers[eventName]) {
            this.eventHandlers[eventName] = [];
        }
        
        this.eventHandlers[eventName].push(callback);
        
        // Appliquer immédiatement les messages en cache pour cet événement
        this.messageCache.forEach(message => {
            if (message.event === eventName) {
                try {
                    callback(...message.data);
                } catch (e) {
                    console.error(`Erreur lors de l'application du cache pour ${eventName}:`, e);
                }
            }
        });
    }
    
    /**
     * Envoie un événement au serveur
     */
    emit(eventName, data) {
        if (!this.connected) {
            // Mettre en file d'attente si déconnecté
            this.pendingMessages.push({ event: eventName, data: data });
            this.log(`Message mis en file d'attente: ${eventName}`, 'warn');
            return false;
        }
        
        try {
            this.socket.emit(eventName, data);
            return true;
        } catch (e) {
            console.error(`Erreur lors de l'émission de ${eventName}:`, e);
            return false;
        }
    }
    
    /**
     * Traite les messages en attente après reconnexion
     */
    processPendingMessages() {
        if (this.pendingMessages.length === 0) return;
        
        this.log(`Traitement de ${this.pendingMessages.length} messages en attente`);
        
        // Copier la file pour éviter des problèmes si de nouveaux messages sont ajoutés
        const pendingCopy = [...this.pendingMessages];
        this.pendingMessages = [];
        
        pendingCopy.forEach(msg => {
            this.emit(msg.event, msg.data);
        });
    }
    
    /**
     * Démarre le heartbeat pour maintenir la connexion
     */
    startHeartbeat() {
        this.stopHeartbeat();
        
        this.heartbeatTimer = setInterval(() => {
            if (this.connected) {
                this.socket.emit('heartbeat', { timestamp: Date.now() });
            }
        }, this.options.heartbeatInterval);
    }
    
    /**
     * Arrête le heartbeat
     */
    stopHeartbeat() {
        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer);
            this.heartbeatTimer = null;
        }
    }
    
    /**
     * Affiche une notification à l'utilisateur
     */
    showNotification(message, type = 'info', persistent = false) {
        // Créer l'élément de notification s'il n'existe pas
        let container = document.querySelector('.realtime-notifications');
        if (!container) {
            container = document.createElement('div');
            container.className = 'realtime-notifications';
            
            // Styles CSS pour les notifications
            const style = document.createElement('style');
            style.textContent = `
                .realtime-notifications {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    z-index: 9999;
                    max-width: 350px;
                }
                
                .realtime-notification {
                    padding: 12px 15px;
                    margin-bottom: 10px;
                    border-radius: 4px;
                    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                    animation: slideIn 0.3s ease;
                    display: flex;
                    align-items: center;
                }
                
                .realtime-notification.info {
                    background-color: #e3f2fd;
                    border-left: 4px solid #2196F3;
                }
                
                .realtime-notification.success {
                    background-color: #e8f5e9;
                    border-left: 4px solid #4CAF50;
                }
                
                .realtime-notification.warning {
                    background-color: #fff8e1;
                    border-left: 4px solid #FFC107;
                }
                
                .realtime-notification.error {
                    background-color: #ffebee;
                    border-left: 4px solid #F44336;
                }
                
                .realtime-notification-close {
                    margin-left: 10px;
                    background: transparent;
                    border: none;
                    color: #888;
                    cursor: pointer;
                }
                
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                
                @keyframes slideOut {
                    from { transform: translateX(0); opacity: 1; }
                    to { transform: translateX(100%); opacity: 0; }
                }
                
                .realtime-notification.closing {
                    animation: slideOut 0.3s ease forwards;
                }
            `;
            document.head.appendChild(style);
            
            document.body.appendChild(container);
        }
        
        // Créer la notification
        const notification = document.createElement('div');
        notification.className = `realtime-notification ${type}`;
        
        // Contenu de la notification
        notification.innerHTML = `
            <div>${message}</div>
            <button class="realtime-notification-close">&times;</button>
        `;
        
        // Ajouter au conteneur
        container.appendChild(notification);
        
        // Bouton de fermeture
        const closeButton = notification.querySelector('.realtime-notification-close');
        closeButton.addEventListener('click', () => {
            this.closeNotification(notification);
        });
        
        // Auto-fermeture si non persistante
        if (!persistent) {
            setTimeout(() => {
                if (notification.parentNode) {
                    this.closeNotification(notification);
                }
            }, 5000);
        }
    }
    
    /**
     * Ferme une notification avec animation
     */
    closeNotification(notification) {
        notification.classList.add('closing');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }
    
    /**
     * Fonction de journalisation
     */
    log(message, level = 'info', ...args) {
        if (!this.options.debug && level === 'debug') return;
        
        const prefix = '[Realtime]';
        
        switch (level) {
            case 'debug':
                console.debug(prefix, message, ...args);
                break;
            case 'warn':
                console.warn(prefix, message, ...args);
                break;
            case 'error':
                console.error(prefix, message, ...args);
                break;
            default:
                console.log(prefix, message, ...args);
        }
    }
}

// Initialisation quand le DOM est chargé
document.addEventListener('DOMContentLoaded', function() {
    // Créer et initialiser le gestionnaire de temps réel
    window.realtimeManager = new RealtimeManager({
        debug: document.body.classList.contains('debug-mode'),
        useLocal: true
    });
    
    window.realtimeManager.connect();
    
    // Gestionnaires pour les événements courants
    window.realtimeManager.on('user_status_change', function(data) {
        updateUserStatus(data);
    });
    
    window.realtimeManager.on('new_notification', function(data) {
        updateNotificationCounter(data);
        showNotificationPopup(data);
    });
    
    window.realtimeManager.on('new_message', function(data) {
        updateConversation(data);
    });
    
    window.realtimeManager.on('reaction_update', function(data) {
        updateReactionCounter(data);
    });
});

// Fonctions de mise à jour de l'UI
function updateUserStatus(data) {
    // Mettre à jour les indicateurs de statut utilisateur
    document.querySelectorAll(`.user-status[data-user-id="${data.user_id}"]`).forEach(element => {
        element.classList.toggle('online', data.is_online);
        element.title = data.is_online ? 'En ligne' : 'Hors ligne';
    });
}

function updateNotificationCounter(data) {
    // Mettre à jour le compteur de notifications
    const counter = document.querySelector('.notification-counter');
    if (counter) {
        const currentCount = parseInt(counter.textContent) || 0;
        counter.textContent = currentCount + 1;
        counter.classList.remove('d-none');
    }
}

function showNotificationPopup(data) {
    // Créer une notification toast
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    // Contenu du toast
    toast.innerHTML = `
        <div class="toast-header">
            <strong class="me-auto">${data.title || 'Notification'}</strong>
            <small>${new Date().toLocaleTimeString()}</small>
            <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Fermer"></button>
        </div>
        <div class="toast-body">
            ${data.content || ''}
        </div>
    `;
    
    // Ajouter au conteneur de toasts
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    toastContainer.appendChild(toast);
    
    // Afficher avec Bootstrap
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Jouer un son de notification
    playNotificationSound();
}

function updateConversation(data) {
    // Mettre à jour la conversation active
    const conversationContainer = document.querySelector(`.conversation[data-user-id="${data.sender_id}"]`);
    if (conversationContainer) {
        // Ajouter le nouveau message
        const messagesContainer = conversationContainer.querySelector('.messages-container');
        if (messagesContainer) {
            const messageHtml = `
                <div class="message ${data.sender_id === currentUserId ? 'outgoing' : 'incoming'}">
                    <div class="message-content">
                        <p>${data.message}</p>
                        <small class="text-muted">${data.timestamp}</small>
                    </div>
                </div>
            `;
            messagesContainer.insertAdjacentHTML('beforeend', messageHtml);
            
            // Faire défiler vers le bas
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    }
    
    // Mettre à jour la liste des conversations
    const conversationPreview = document.querySelector(`.conversation-preview[data-user-id="${data.sender_id}"]`);
    if (conversationPreview) {
        // Mettre à jour l'aperçu du dernier message
        const lastMessageElement = conversationPreview.querySelector('.last-message');
        if (lastMessageElement) {
            lastMessageElement.textContent = data.message;
        }
        
        // Mettre à jour le compteur de messages non lus
        const unreadCounter = conversationPreview.querySelector('.unread-counter');
        if (unreadCounter) {
            const currentCount = parseInt(unreadCounter.textContent) || 0;
            unreadCounter.textContent = currentCount + 1;
            unreadCounter.classList.remove('d-none');
        }
        
        // Déplacer cette conversation en haut de la liste
        const conversationsList = conversationPreview.parentNode;
        conversationsList.prepend(conversationPreview);
    }
    
    // Jouer un son de notification
    playNotificationSound();
}

function updateReactionCounter(data) {
    // Mettre à jour le compteur de réactions
    const targetElement = data.comment_id 
        ? document.querySelector(`.reaction-button[data-comment-id="${data.comment_id}"]`)
        : document.querySelector(`.reaction-button[data-post-id="${data.post_id}"]`);
    
    if (targetElement) {
        const counterElement = targetElement.querySelector('.reaction-count');
        if (counterElement) {
            counterElement.textContent = data.count;
        }
        
        // Mettre à jour l'état du bouton
        if (data.user_id === currentUserId) {
            if (data.action === 'add') {
                targetElement.classList.add('active');
                targetElement.setAttribute('data-liked', 'true');
            } else if (data.action === 'remove') {
                targetElement.classList.remove('active');
                targetElement.setAttribute('data-liked', 'false');
            }
        }
    }
}

function playNotificationSound() {
    // Jouer un son de notification
    const sound = document.getElementById('notification-sound');
    if (sound) {
        sound.currentTime = 0;
        sound.play().catch(e => {
            // Ignorer les erreurs dues aux restrictions de lecture automatique
        });
    }
}

// Exposer le gestionnaire
window.RealtimeManager = RealtimeManager;
