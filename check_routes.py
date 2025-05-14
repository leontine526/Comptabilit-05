
#!/usr/bin/env python
"""
Ce script vérifie toutes les routes de l'application
pour détecter d'éventuels problèmes.
"""
import os
import sys
import logging
from datetime import datetime
from flask import url_for

# Configuration du logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_routes():
    """Vérifie toutes les routes de l'application"""
    print("=== VÉRIFICATION DES ROUTES ===")
    
    try:
        # Import l'application Flask
        from app import app
        
        # Configuration pour éviter les erreurs lors de la génération des URLs
        app.config['SERVER_NAME'] = 'localhost:5000'
        
        with app.app_context():
            # Récupération de toutes les routes
            routes = []
            for rule in app.url_map.iter_rules():
                # Ignorer les routes statiques
                if rule.endpoint == 'static':
                    continue
                    
                # Récupérer l'information sur la route
                route_info = {
                    'endpoint': rule.endpoint,
                    'methods': sorted(list(rule.methods)),
                    'path': str(rule),
                    'has_params': bool(rule.arguments),
                    'arguments': list(rule.arguments)
                }
                routes.append(route_info)
            
            # Afficher les routes
            print(f"Nombre total de routes: {len(routes)}")
            
            # Vérifier les routes à risque (celles qui pourraient causer des erreurs)
            risky_routes = []
            for route in routes:
                # Routes avec des paramètres sont à risque si elles n'ont pas de gestion d'erreur
                if route['has_params']:
                    risky_routes.append({
                        'route': route,
                        'reason': f"Cette route utilise des paramètres: {route['arguments']}. Vérifiez qu'elle gère correctement les cas où ces paramètres sont invalides."
                    })
                
                # Routes utilisant le même chemin avec des méthodes différentes
                if route['methods'] != ['GET']:
                    other_routes = [r for r in routes if r['path'] == route['path'] and r != route]
                    if other_routes:
                        risky_routes.append({
                            'route': route,
                            'reason': f"Cette route partage le même chemin avec d'autres routes: {[r['endpoint'] for r in other_routes]}"
                        })
            
            # Afficher les routes à risque
            if risky_routes:
                print("\n=== ROUTES À RISQUE ===")
                for i, risky_route in enumerate(risky_routes, 1):
                    route = risky_route['route']
                    print(f"\n{i}. Endpoint: {route['endpoint']}")
                    print(f"   Path: {route['path']}")
                    print(f"   Methods: {', '.join(route['methods'])}")
                    print(f"   Raison: {risky_route['reason']}")
            else:
                print("\nAucune route à risque détectée.")
                
            # Vérifier les routes qui pourraient causer des erreurs de base de données
            db_routes = []
            for route in routes:
                # Recherche d'endpoints connus pour utiliser la base de données
                db_related_keywords = ['workgroup', 'exercise', 'account', 'transaction', 
                                      'document', 'user', 'profile', 'notes', 'message']
                if any(keyword in route['endpoint'].lower() for keyword in db_related_keywords):
                    db_routes.append(route)
            
            if db_routes:
                print("\n=== ROUTES UTILISANT LA BASE DE DONNÉES ===")
                print(f"Nombre de routes DB: {len(db_routes)}")
                print("Ces routes doivent être protégées contre les erreurs de base de données.")
                
            return True
    except Exception as e:
        logger.error(f"Erreur lors de la vérification des routes: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== VÉRIFICATION DES ROUTES DE L'APPLICATION ===")
    check_routes()
