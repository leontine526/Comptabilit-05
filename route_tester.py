
#!/usr/bin/env python
"""
Script pour tester toutes les routes de l'application
et identifier les erreurs potentielles
"""
import os
import sys
import logging
import traceback
import requests
from datetime import datetime
from flask import Flask, url_for, current_app
from werkzeug.routing import Rule

# Configuration du logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_routes(base_url=None):
    """
    Teste toutes les routes de l'application
    pour détecter des erreurs
    """
    print("=== TEST DES ROUTES DE L'APPLICATION ===")
    
    if not base_url:
        base_url = "http://localhost:5000"
    
    # Importer l'application Flask
    try:
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
            
            # Afficher le nombre total de routes
            print(f"\nNombre total de routes: {len(routes)}")
            
            # Tester chaque route GET sans paramètres
            print("\n=== TEST DES ROUTES GET SANS PARAMÈTRES ===")
            results = []
            
            for route in routes:
                if 'GET' in route['methods'] and not route['has_params']:
                    path = route['path']
                    url = f"{base_url}{path}"
                    
                    print(f"Test de {url}...")
                    try:
                        response = requests.get(url, timeout=5)
                        status = response.status_code
                        
                        result = {
                            'endpoint': route['endpoint'],
                            'url': url,
                            'status': status,
                            'success': 200 <= status < 400,
                            'error': None
                        }
                    except Exception as e:
                        result = {
                            'endpoint': route['endpoint'],
                            'url': url,
                            'status': None,
                            'success': False,
                            'error': str(e)
                        }
                    
                    results.append(result)
                    
                    # Afficher le résultat
                    if result['success']:
                        print(f"  ✓ {result['endpoint']} - {status}")
                    else:
                        error_msg = f" - {result['error']}" if result['error'] else ""
                        print(f"  ✗ {result['endpoint']} - {status}{error_msg}")
            
            # Résumé
            success_count = sum(1 for r in results if r['success'])
            print(f"\nRésumé: {success_count}/{len(results)} routes testées avec succès")
            
            # Afficher les routes qui ont échoué
            failed_routes = [r for r in results if not r['success']]
            if failed_routes:
                print("\n=== ROUTES AVEC ERREURS ===")
                for i, route in enumerate(failed_routes, 1):
                    status = route['status'] or 'ERROR'
                    error = f" - {route['error']}" if route['error'] else ""
                    print(f"{i}. {route['endpoint']} ({status}){error}")
            
            # Routes avec paramètres (informatives seulement)
            param_routes = [r for r in routes if r['has_params']]
            if param_routes:
                print("\n=== ROUTES AVEC PARAMÈTRES (NON TESTÉES) ===")
                for i, route in enumerate(param_routes, 1):
                    print(f"{i}. {route['endpoint']} - {route['path']} - Paramètres: {', '.join(route['arguments'])}")
            
            return results
    
    except Exception as e:
        logger.error(f"Erreur lors du test des routes: {str(e)}")
        traceback.print_exc()
        return []

if __name__ == "__main__":
    try:
        print("Démarrage des tests de routes...")
        
        # Récupérer l'URL de base depuis les arguments
        base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
        
        test_routes(base_url)
        
        print("\nTests des routes terminés.")
    except Exception as e:
        print(f"Erreur lors des tests: {str(e)}")
        traceback.print_exc()
