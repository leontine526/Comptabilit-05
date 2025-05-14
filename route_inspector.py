
import os
import sys
import logging
import inspect
import traceback
from datetime import datetime
from flask import Flask, url_for, request
from werkzeug.routing import Rule

# Configuration du logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def inspect_routes(app=None):
    """
    Analyse approfondie de toutes les routes de l'application
    pour détecter des problèmes potentiels
    """
    print("=== INSPECTION COMPLÈTE DES ROUTES ===")
    
    if app is None:
        from app import app
    
    # Configuration pour éviter les erreurs lors de la génération des URLs
    app.config['SERVER_NAME'] = 'localhost:5000'
    
    with app.app_context():
        # Récupération de toutes les routes
        routes = []
        for rule in app.url_map.iter_rules():
            # Ignorer les routes statiques et les routes de l'admin
            if rule.endpoint == 'static':
                continue
                
            # Récupérer l'information sur la route
            route_info = {
                'endpoint': rule.endpoint,
                'methods': sorted(list(rule.methods)),
                'path': str(rule),
                'has_params': bool(rule.arguments),
                'arguments': list(rule.arguments),
                'function': get_view_function(app, rule.endpoint)
            }
            routes.append(route_info)
        
        # Afficher le nombre total de routes
        print(f"\nNombre total de routes: {len(routes)}")
        
        # Analyser les routes
        issues = inspect_route_issues(routes)
        
        # Afficher les résultats de l'analyse
        print_analysis_results(issues)
        
        # Générer un rapport détaillé
        generate_detailed_report(routes, issues)
        
        return routes, issues

def get_view_function(app, endpoint):
    """Récupère la fonction de vue associée à un endpoint"""
    try:
        view_function = app.view_functions.get(endpoint)
        if view_function:
            return view_function.__name__
        return None
    except Exception as e:
        return f"Erreur: {str(e)}"

def inspect_route_issues(routes):
    """
    Analyse les routes pour détecter des problèmes potentiels
    """
    issues = {
        'missing_authorization': [],
        'db_operations': [],
        'parameter_validation': [],
        'error_handling': [],
        'duplicate_paths': [],
        'complex_routes': [],
        'security_issues': []
    }
    
    # Identifier les routes avec des chemins dupliqués
    path_methods = {}
    for route in routes:
        path = route['path']
        methods = tuple(sorted(route['methods']))
        if (path, methods) in path_methods:
            issues['duplicate_paths'].append({
                'path': path,
                'methods': methods,
                'endpoints': [route['endpoint'], path_methods[(path, methods)]]
            })
        else:
            path_methods[(path, methods)] = route['endpoint']
    
    # Analyser chaque route
    for route in routes:
        # Vérifier l'autorisation
        if not any(auth_keyword in route['endpoint'] for auth_keyword in ['login', 'register', 'public', 'static']):
            if not check_login_required(route):
                issues['missing_authorization'].append(route)
        
        # Vérifier les opérations de base de données
        if any(db_keyword in route['endpoint'] for db_keyword in ['create', 'edit', 'update', 'delete', 'save', 'remove']):
            issues['db_operations'].append(route)
        
        # Vérifier la validation des paramètres
        if route['has_params']:
            issues['parameter_validation'].append(route)
        
        # Identifier les routes complexes (avec beaucoup de paramètres)
        if len(route['arguments']) >= 3:
            issues['complex_routes'].append(route)
        
        # Identifier les problèmes de sécurité potentiels
        if any(sec_keyword in route['endpoint'] for sec_keyword in ['admin', 'delete', 'remove', 'upload']):
            issues['security_issues'].append(route)
    
    return issues

def check_login_required(route):
    """
    Vérifie si une route a un décorateur login_required
    (Approche simplifiée, peut ne pas fonctionner dans tous les cas)
    """
    # Cette fonction est simplifiée car l'inspection des décorateurs est complexe
    # En pratique, on analyserait le code source de la fonction de vue
    function_name = route.get('function', '')
    login_keywords = ['login', 'register', 'public', 'static', 'index', 'about']
    return any(keyword in route['endpoint'] for keyword in login_keywords)

def print_analysis_results(issues):
    """
    Affiche les résultats de l'analyse
    """
    print("\n=== RÉSULTATS DE L'ANALYSE ===")
    
    # Autorisation manquante
    print(f"\n1. Routes sans protection d'authentification: {len(issues['missing_authorization'])}")
    if issues['missing_authorization']:
        for i, route in enumerate(issues['missing_authorization'][:5], 1):
            print(f"   {i}. {route['endpoint']} - {route['path']}")
        if len(issues['missing_authorization']) > 5:
            print(f"   ... et {len(issues['missing_authorization']) - 5} autres routes")
    
    # Opérations de base de données
    print(f"\n2. Routes avec opérations de base de données: {len(issues['db_operations'])}")
    if issues['db_operations']:
        for i, route in enumerate(issues['db_operations'][:5], 1):
            print(f"   {i}. {route['endpoint']} - {route['path']}")
        if len(issues['db_operations']) > 5:
            print(f"   ... et {len(issues['db_operations']) - 5} autres routes")
    
    # Validation des paramètres
    print(f"\n3. Routes nécessitant une validation de paramètres: {len(issues['parameter_validation'])}")
    if issues['parameter_validation']:
        for i, route in enumerate(issues['parameter_validation'][:5], 1):
            print(f"   {i}. {route['endpoint']} - {route['path']} - Paramètres: {', '.join(route['arguments'])}")
        if len(issues['parameter_validation']) > 5:
            print(f"   ... et {len(issues['parameter_validation']) - 5} autres routes")
    
    # Chemins dupliqués
    print(f"\n4. Routes avec chemins dupliqués: {len(issues['duplicate_paths'])}")
    if issues['duplicate_paths']:
        for i, dup in enumerate(issues['duplicate_paths'], 1):
            print(f"   {i}. {dup['path']} - Méthodes: {', '.join(dup['methods'])} - Endpoints: {', '.join(dup['endpoints'])}")
    
    # Routes complexes
    print(f"\n5. Routes complexes (3+ paramètres): {len(issues['complex_routes'])}")
    if issues['complex_routes']:
        for i, route in enumerate(issues['complex_routes'][:5], 1):
            print(f"   {i}. {route['endpoint']} - {route['path']} - Paramètres: {', '.join(route['arguments'])}")
        if len(issues['complex_routes']) > 5:
            print(f"   ... et {len(issues['complex_routes']) - 5} autres routes")
    
    # Problèmes de sécurité
    print(f"\n6. Routes avec risques de sécurité potentiels: {len(issues['security_issues'])}")
    if issues['security_issues']:
        for i, route in enumerate(issues['security_issues'][:5], 1):
            print(f"   {i}. {route['endpoint']} - {route['path']}")
        if len(issues['security_issues']) > 5:
            print(f"   ... et {len(issues['security_issues']) - 5} autres routes")
    
    # Résumé
    total_issues = sum(len(issue_list) for issue_list in issues.values())
    print(f"\n=== RÉSUMÉ ===")
    print(f"Total des problèmes potentiels identifiés: {total_issues}")
    print(f"Les détails complets sont disponibles dans le rapport 'route_analysis_report.html'")

def generate_detailed_report(routes, issues):
    """
    Génère un rapport HTML détaillé de l'analyse des routes
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    html = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Rapport d'Analyse des Routes</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; }}
            h1, h2, h3 {{ color: #333; }}
            table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
            .issue {{ color: #d9534f; }}
            .warning {{ color: #f0ad4e; }}
            .info {{ color: #5bc0de; }}
            .success {{ color: #5cb85c; }}
        </style>
    </head>
    <body>
        <h1>Rapport d'Analyse des Routes</h1>
        <p>Généré le {now}</p>
        <h2>Résumé</h2>
        <table>
            <tr>
                <th>Catégorie</th>
                <th>Nombre</th>
            </tr>
            <tr>
                <td>Nombre total de routes</td>
                <td>{len(routes)}</td>
            </tr>
            <tr>
                <td>Routes sans protection d'authentification</td>
                <td>{len(issues['missing_authorization'])}</td>
            </tr>
            <tr>
                <td>Routes avec opérations de base de données</td>
                <td>{len(issues['db_operations'])}</td>
            </tr>
            <tr>
                <td>Routes nécessitant une validation de paramètres</td>
                <td>{len(issues['parameter_validation'])}</td>
            </tr>
            <tr>
                <td>Routes avec chemins dupliqués</td>
                <td>{len(issues['duplicate_paths'])}</td>
            </tr>
            <tr>
                <td>Routes complexes (3+ paramètres)</td>
                <td>{len(issues['complex_routes'])}</td>
            </tr>
            <tr>
                <td>Routes avec risques de sécurité potentiels</td>
                <td>{len(issues['security_issues'])}</td>
            </tr>
        </table>
        
        <h2>Liste complète des routes</h2>
        <table>
            <tr>
                <th>Endpoint</th>
                <th>Chemin</th>
                <th>Méthodes</th>
                <th>Paramètres</th>
                <th>Risques potentiels</th>
            </tr>
    """
    
    # Créer un dictionnaire de risques pour chaque route
    route_risks = {}
    for route in routes:
        endpoint = route['endpoint']
        route_risks[endpoint] = []
        
        if route in issues['missing_authorization']:
            route_risks[endpoint].append("Authentification manquante")
        
        if route in issues['db_operations']:
            route_risks[endpoint].append("Opérations DB")
        
        if route in issues['parameter_validation']:
            route_risks[endpoint].append("Validation de paramètres requise")
        
        if route in issues['complex_routes']:
            route_risks[endpoint].append("Route complexe")
        
        if route in issues['security_issues']:
            route_risks[endpoint].append("Risque de sécurité potentiel")
        
        # Vérifier les chemins dupliqués
        for dup in issues['duplicate_paths']:
            if endpoint in dup['endpoints']:
                route_risks[endpoint].append("Chemin dupliqué")
                break
    
    # Ajouter chaque route au rapport
    for route in sorted(routes, key=lambda r: r['endpoint']):
        risks = route_risks[route['endpoint']]
        risk_class = "issue" if risks else "success"
        risk_text = ", ".join(risks) if risks else "Aucun"
        
        html += f"""
            <tr>
                <td>{route['endpoint']}</td>
                <td>{route['path']}</td>
                <td>{', '.join(route['methods'])}</td>
                <td>{', '.join(route['arguments']) if route['arguments'] else '-'}</td>
                <td class="{risk_class}">{risk_text}</td>
            </tr>
        """
    
    html += """
        </table>
        
        <h2>Recommandations</h2>
        <ol>
            <li>Vérifiez que toutes les routes non-publiques sont protégées par une authentification</li>
            <li>Ajoutez une validation des paramètres pour les routes qui en ont besoin</li>
            <li>Utilisez des transactions pour les opérations DB critiques</li>
            <li>Évitez les routes trop complexes avec de nombreux paramètres</li>
            <li>Vérifiez les routes avec chemins dupliqués pour éviter les conflits</li>
            <li>Implémentez une gestion d'erreur robuste pour toutes les routes</li>
            <li>Ajoutez une protection CSRF pour les routes qui modifient des données</li>
            <li>Implémentez une limitation de taux (rate limiting) pour les routes sensibles</li>
        </ol>
    </body>
    </html>
    """
    
    # Écrire le rapport dans un fichier
    with open("route_analysis_report.html", "w") as f:
        f.write(html)
    
    print(f"\nRapport détaillé généré: route_analysis_report.html")

if __name__ == "__main__":
    try:
        print("Démarrage de l'inspection des routes...")
        
        # Import l'application Flask
        try:
            from app import app
            inspect_routes(app)
        except ImportError:
            print("Impossible d'importer l'application Flask directement.")
            inspect_routes()
        
        print("\nInspection des routes terminée.")
    except Exception as e:
        print(f"Erreur lors de l'inspection des routes: {str(e)}")
        traceback.print_exc()
