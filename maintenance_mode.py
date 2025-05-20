
"""
Module pour gérer le mode maintenance de l'application
Permet d'activer/désactiver facilement le mode maintenance
et de définir des exclusions pour certaines routes
"""
import os
import json
import time
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for

# Chemins et noms de fichiers
MAINTENANCE_FILE = 'maintenance.json'
DEFAULT_CONFIG = {
    'enabled': False,
    'start_time': None,
    'end_time': None,
    'message': 'Notre application est en cours de maintenance. Nous serons de retour bientôt.',
    'excluded_paths': ['/health', '/api/health'],
    'excluded_ips': []
}

def load_maintenance_config():
    """Charge la configuration de maintenance depuis le fichier"""
    if os.path.exists(MAINTENANCE_FILE):
        try:
            with open(MAINTENANCE_FILE, 'r') as f:
                config = json.load(f)
                # S'assurer que toutes les clés nécessaires sont présentes
                for key in DEFAULT_CONFIG:
                    if key not in config:
                        config[key] = DEFAULT_CONFIG[key]
                return config
        except Exception as e:
            print(f"Erreur lors du chargement de la configuration de maintenance: {str(e)}")
    return DEFAULT_CONFIG.copy()

def save_maintenance_config(config):
    """Sauvegarde la configuration de maintenance dans le fichier"""
    try:
        with open(MAINTENANCE_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Erreur lors de la sauvegarde de la configuration de maintenance: {str(e)}")
        return False

def enable_maintenance(message=None, duration_minutes=None, excluded_paths=None, excluded_ips=None):
    """Active le mode maintenance"""
    config = load_maintenance_config()
    config['enabled'] = True
    config['start_time'] = int(time.time())
    
    if message:
        config['message'] = message
    
    if duration_minutes:
        config['end_time'] = int(time.time() + (duration_minutes * 60))
    else:
        config['end_time'] = None
    
    if excluded_paths:
        config['excluded_paths'] = excluded_paths
    
    if excluded_ips:
        config['excluded_ips'] = excluded_ips
    
    return save_maintenance_config(config)

def disable_maintenance():
    """Désactive le mode maintenance"""
    config = load_maintenance_config()
    config['enabled'] = False
    return save_maintenance_config(config)

def is_in_maintenance():
    """Vérifie si l'application est en mode maintenance"""
    config = load_maintenance_config()
    
    # Si le mode maintenance n'est pas activé, retourner False
    if not config['enabled']:
        return False
    
    # Vérifier si la période de maintenance est terminée
    if config['end_time'] and time.time() > config['end_time']:
        # Désactiver automatiquement le mode maintenance
        disable_maintenance()
        return False
    
    return True

def maintenance_mode_middleware(app):
    """Middleware pour gérer le mode maintenance"""
    @app.before_request
    def check_maintenance():
        # Ne pas vérifier pour les requêtes statiques
        if request.path.startswith('/static/'):
            return None
        
        if is_in_maintenance():
            config = load_maintenance_config()
            
            # Vérifier les chemins exclus
            if request.path in config['excluded_paths']:
                return None
            
            # Vérifier les IPs exclues
            client_ip = request.remote_addr
            if client_ip in config['excluded_ips']:
                return None
            
            # Rediriger vers la page de maintenance
            if request.path != '/maintenance':
                return render_template('maintenance.html', message=config['message'])
    
    # Créer la route pour la page de maintenance
    @app.route('/maintenance')
    def maintenance_page():
        config = load_maintenance_config()
        return render_template('maintenance.html', message=config['message'])
    
    # Route pour vérifier l'état du mode maintenance (pour les admins)
    @app.route('/api/maintenance/status')
    def maintenance_status():
        config = load_maintenance_config()
        return {
            'is_enabled': is_in_maintenance(),
            'config': config
        }
    
    # Route pour activer/désactiver le mode maintenance (pour les admins)
    @app.route('/api/maintenance/toggle', methods=['POST'])
    def toggle_maintenance():
        # Vérifier si l'utilisateur est admin (à implémenter)
        
        if request.json.get('enabled', False):
            result = enable_maintenance(
                message=request.json.get('message'),
                duration_minutes=request.json.get('duration_minutes'),
                excluded_paths=request.json.get('excluded_paths'),
                excluded_ips=request.json.get('excluded_ips')
            )
            return {'success': result, 'enabled': True}
        else:
            result = disable_maintenance()
            return {'success': result, 'enabled': False}

def init_maintenance_mode(app):
    """Initialise le mode maintenance pour l'application Flask"""
    maintenance_mode_middleware(app)
    return app
