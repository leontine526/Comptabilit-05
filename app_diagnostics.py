
#!/usr/bin/env python
"""
Script de diagnostic complet pour SmartOHADA
Vérifie tous les aspects de l'application: routes, templates, static files, base de données
"""
import os
import sys
import logging
import importlib
import traceback
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("app_diagnostics")

def print_header(title):
    """Affiche un en-tête formaté"""
    print("\n" + "=" * 60)
    print(f" {title} ".center(60, "="))
    print("=" * 60)

def check_static_files():
    """Vérifie que tous les fichiers statiques référencés existent"""
    print_header("VÉRIFICATION DES FICHIERS STATIQUES")
    
    # Dossiers à vérifier
    static_folders = [
        "static/css", 
        "static/js", 
        "static/images",
        "static/uploads"
    ]
    
    for folder in static_folders:
        if os.path.exists(folder):
            print(f"✅ Dossier {folder} trouvé")
            # Vérifier le nombre de fichiers
            files = os.listdir(folder)
            print(f"   - {len(files)} fichiers dans ce dossier")
        else:
            print(f"❌ Dossier {folder} manquant")
            # Créer le dossier manquant
            try:
                os.makedirs(folder, exist_ok=True)
                print(f"   - Dossier {folder} créé automatiquement")
            except Exception as e:
                print(f"   - Erreur lors de la création du dossier: {str(e)}")
    
    # Vérifier les fichiers CSS critiques
    css_files = ["main.css", "custom.css", "dashboard.css"]
    for css_file in css_files:
        css_path = os.path.join("static/css", css_file)
        if os.path.exists(css_path):
            print(f"✅ Fichier CSS {css_file} trouvé")
        else:
            print(f"⚠️ Fichier CSS {css_file} manquant")
    
    # Vérifier les fichiers JS critiques
    js_files = ["app.js", "realtime.js"]
    for js_file in js_files:
        js_path = os.path.join("static/js", js_file)
        if os.path.exists(js_path):
            print(f"✅ Fichier JS {js_file} trouvé")
        else:
            print(f"⚠️ Fichier JS {js_file} manquant")

def check_template_inheritance():
    """Vérifie la structure d'héritage des templates"""
    print_header("VÉRIFICATION DES TEMPLATES")
    
    # Vérifier l'existence du template de base
    base_template = "templates/base.html"
    if os.path.exists(base_template):
        print(f"✅ Template de base trouvé: {base_template}")
        
        # Analyser le contenu pour les blocs essentiels
        with open(base_template, "r", encoding="utf-8") as f:
            content = f.read()
            
        essential_blocks = ["title", "content", "scripts", "styles"]
        for block in essential_blocks:
            if f"{{% block {block} %}}" in content:
                print(f"✅ Bloc '{block}' trouvé dans le template de base")
            else:
                print(f"⚠️ Bloc '{block}' manquant dans le template de base")
    else:
        print(f"❌ Template de base manquant: {base_template}")
    
    # Vérifier d'autres templates importants
    important_templates = [
        "templates/index.html", 
        "templates/dashboard.html",
        "templates/auth/login.html",
        "templates/auth/register.html"
    ]
    
    for template in important_templates:
        if os.path.exists(template):
            print(f"✅ Template {template} trouvé")
            
            # Vérifier si le template étend le template de base
            with open(template, "r", encoding="utf-8") as f:
                content = f.read()
            
            if "{% extends" in content:
                print(f"   - Étend correctement un autre template")
            else:
                print(f"⚠️ - Ne semble pas étendre le template de base")
        else:
            print(f"❌ Template {template} manquant")

def check_route_handlers():
    """Vérifie que toutes les routes sont correctement déclarées"""
    print_header("VÉRIFICATION DES ROUTES")
    
    try:
        # Importer l'application Flask
        from app import app
        
        # Configuration pour éviter les erreurs lors de la génération des URLs
        app.config['SERVER_NAME'] = 'localhost:5000'
        app.config['APPLICATION_ROOT'] = '/'
        
        with app.app_context():
            # Récupérer toutes les routes
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
            
            # Afficher un résumé des routes
            print(f"Total des routes: {len(routes)}")
            
            # Vérifier les routes essentielles
            essential_routes = [
                "/", "/index", "/dashboard", "/login", "/register"
            ]
            
            for route_path in essential_routes:
                found = False
                for route in routes:
                    if route['path'] == route_path:
                        found = True
                        print(f"✅ Route essentielle '{route_path}' trouvée")
                        break
                
                if not found:
                    print(f"❌ Route essentielle '{route_path}' manquante")
            
            # Analyser les routes avec paramètres
            param_routes = [r for r in routes if r['has_params']]
            print(f"\nRoutes avec paramètres: {len(param_routes)}")
            if len(param_routes) > 0:
                print("Exemples de routes avec paramètres:")
                for i, route in enumerate(param_routes[:3], 1):
                    print(f"{i}. {route['path']} - Paramètres: {', '.join(route['arguments'])}")
            
            # Vérifier les routes en double
            paths = {}
            duplicate_paths = []
            
            for route in routes:
                path = route['path']
                methods = tuple(sorted(route['methods']))
                
                if (path, methods) in paths:
                    duplicate_paths.append({
                        'path': path,
                        'methods': methods,
                        'endpoints': [route['endpoint'], paths[(path, methods)]]
                    })
                else:
                    paths[(path, methods)] = route['endpoint']
            
            if duplicate_paths:
                print(f"\n⚠️ Routes en double détectées: {len(duplicate_paths)}")
                for dup in duplicate_paths:
                    print(f"  - {dup['path']} ({', '.join(dup['methods'])}) -> {', '.join(dup['endpoints'])}")
            else:
                print("\n✅ Aucune route en double détectée")
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification des routes: {str(e)}")
        traceback.print_exc()

def check_database_models():
    """Vérifie les modèles de base de données"""
    print_header("VÉRIFICATION DES MODÈLES DE BASE DE DONNÉES")
    
    try:
        # Importer les modèles
        from models import User, Exercise, Account, Transaction, TransactionItem
        from models import Document, Workgroup, Message, Note, Notification
        
        # Liste des modèles à vérifier
        models = [
            User, Exercise, Account, Transaction, TransactionItem,
            Document, Workgroup, Message, Note, Notification
        ]
        
        print(f"Nombre de modèles vérifiés: {len(models)}")
        
        # Vérifier chaque modèle
        for model in models:
            print(f"\nModèle: {model.__name__}")
            
            # Vérifier les attributs clés
            try:
                if hasattr(model, "__tablename__"):
                    print(f"✅ Table: {model.__tablename__}")
                else:
                    print(f"❌ Attribut __tablename__ manquant")
                
                # Vérifier si le modèle a des colonnes
                columns = [attr for attr in dir(model) 
                          if not attr.startswith("_") 
                          and not callable(getattr(model, attr))
                          and attr != "metadata"
                          and attr != "query"
                          and attr != "query_class"]
                
                print(f"Colonnes détectées: {len(columns)}")
                
                # Vérifier les relations
                relationships = []
                for attr_name in dir(model):
                    if not attr_name.startswith('_'):
                        attr = getattr(model, attr_name)
                        if hasattr(attr, 'prop') and hasattr(attr.prop, 'direction'):
                            relationships.append((attr_name, attr.prop.direction.name))
                
                if relationships:
                    print(f"Relations: {len(relationships)}")
                else:
                    print("Aucune relation trouvée")
                
            except Exception as e:
                print(f"Erreur lors de l'analyse du modèle {model.__name__}: {str(e)}")
    
    except ImportError as e:
        print(f"❌ Erreur d'importation des modèles: {str(e)}")
    except Exception as e:
        print(f"❌ Erreur lors de la vérification des modèles: {str(e)}")
        traceback.print_exc()

def check_database_connection():
    """Vérifie la connexion à la base de données"""
    print_header("VÉRIFICATION DE LA CONNEXION À LA BASE DE DONNÉES")
    
    try:
        # Vérifier si la connexion à la base de données fonctionne
        print("Tentative de connexion à la base de données...")
        
        # Importer la base de données et l'application
        from app import db, app
        
        with app.app_context():
            # Exécuter une requête simple
            result = db.session.execute("SELECT 1").scalar()
            
            if result == 1:
                print("✅ Connexion à la base de données réussie")
                
                # Vérifier les tables
                from sqlalchemy import inspect
                inspector = inspect(db.engine)
                tables = inspector.get_table_names()
                
                print(f"Tables dans la base de données: {len(tables)}")
                if tables:
                    print("Tables trouvées:")
                    for i, table in enumerate(tables, 1):
                        print(f"{i}. {table}")
                else:
                    print("⚠️ Aucune table trouvée dans la base de données")
            else:
                print(f"❌ La connexion à la base de données a échoué: résultat inattendu ({result})")
    
    except ImportError as e:
        print(f"❌ Erreur d'importation: {str(e)}")
    except Exception as e:
        print(f"❌ Erreur lors de la vérification de la connexion à la base de données: {str(e)}")
        traceback.print_exc()
        
        # Recommandations spécifiques pour les erreurs de connexion
        print("\nRecommandations pour résoudre les problèmes de connexion à la base de données:")
        print("1. Vérifiez que la variable DATABASE_URL est correctement définie")
        print("2. Assurez-vous que le service de base de données est accessible")
        print("3. Exécutez le script db_initialize.py pour initialiser la base de données")

def check_javascript_console_errors():
    """Vérifie les erreurs JavaScript potentielles"""
    print_header("VÉRIFICATION DES SCRIPTS JAVASCRIPT")
    
    # Vérifier l'existence des fichiers JS principaux
    js_files = [
        "static/js/app.js",
        "static/js/realtime.js", 
        "static/js/error-handler.js"
    ]
    
    for js_file in js_files:
        if os.path.exists(js_file):
            print(f"✅ Fichier JavaScript {js_file} trouvé")
            
            # Rechercher des erreurs courantes
            with open(js_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Vérifier les erreurs courantes
            issues = []
            
            if "console.log" in content:
                issues.append("Contient des appels console.log (à supprimer en production)")
            
            if "alert(" in content:
                issues.append("Utilise alert() (à éviter, préférer les notifications modernes)")
            
            if "document.write" in content:
                issues.append("Utilise document.write (déconseillé, peut bloquer le rendu)")
            
            if issues:
                print(f"⚠️ Problèmes potentiels dans {js_file}:")
                for issue in issues:
                    print(f"   - {issue}")
            else:
                print(f"   - Aucun problème courant détecté")
        else:
            print(f"⚠️ Fichier JavaScript {js_file} manquant")

def check_responsive_design():
    """Vérifie les éléments de design responsive"""
    print_header("VÉRIFICATION DU RESPONSIVE DESIGN")
    
    # Vérifier si le template de base contient les méta-tags responsives
    base_template = "templates/base.html"
    if os.path.exists(base_template):
        with open(base_template, "r", encoding="utf-8") as f:
            content = f.read()
        
        responsive_elements = {
            "viewport": 'name="viewport"' in content,
            "media queries": "@media" in content or "media=" in content,
            "responsive css": "responsive.css" in content
        }
        
        for element, exists in responsive_elements.items():
            if exists:
                print(f"✅ Élément responsive trouvé: {element}")
            else:
                print(f"⚠️ Élément responsive manquant: {element}")
                
                # Suggestion pour le viewport manquant
                if element == "viewport":
                    print("   Suggestion: Ajoutez cette balise dans le <head> du template de base:")
                    print('   <meta name="viewport" content="width=device-width, initial-scale=1.0">')
    else:
        print(f"❌ Template de base manquant: {base_template}")

def generate_report():
    """Génère un rapport HTML de diagnostic complet"""
    print_header("GÉNÉRATION DU RAPPORT DE DIAGNOSTIC")
    
    # Créer le rapport HTML
    report_file = "diagnostic_report.html"
    
    try:
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport de diagnostic SmartOHADA</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; max-width: 1200px; margin: 0 auto; }}
        h1, h2, h3 {{ color: #333; }}
        .success {{ color: #28a745; }}
        .warning {{ color: #ffc107; }}
        .error {{ color: #dc3545; }}
        .card {{ border: 1px solid #ddd; border-radius: 5px; padding: 20px; margin-bottom: 20px; }}
        .header {{ background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-bottom: 20px; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Rapport de diagnostic SmartOHADA</h1>
        <p>Généré le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="card">
        <h2>Résumé</h2>
        <p>Ce rapport présente les résultats du diagnostic complet de l'application SmartOHADA.</p>
        <p>Pour une analyse détaillée des routes, consultez également le fichier <code>route_analysis_report.html</code>.</p>
    </div>
    
    <div class="card">
        <h2>Recommandations principales</h2>
        <ul>
            <li>Vérifiez que tous les templates étendent correctement le template de base</li>
            <li>Assurez-vous que les fichiers statiques (CSS, JS, images) sont correctement référencés</li>
            <li>Testez l'application sur différents appareils pour vérifier le responsive design</li>
            <li>Utilisez le workflow "Démarrage Simple" pour démarrer l'application de manière fiable</li>
            <li>Consultez les logs d'erreur régulièrement pour identifier les problèmes</li>
        </ul>
    </div>
    
    <div class="card">
        <h2>Prochaines étapes</h2>
        <ol>
            <li>Exécutez l'inspecteur de routes pour une analyse approfondie: <code>python route_inspector.py</code></li>
            <li>Vérifiez les erreurs JavaScript dans la console du navigateur</li>
            <li>Testez toutes les fonctionnalités critiques de l'application</li>
            <li>Mettez à jour les dépendances si nécessaire</li>
        </ol>
    </div>
</body>
</html>""")
        
        print(f"✅ Rapport de diagnostic généré: {report_file}")
    except Exception as e:
        print(f"❌ Erreur lors de la génération du rapport: {str(e)}")

def run_full_diagnostics():
    """Exécute tous les diagnostics"""
    print_header("DIAGNOSTIC COMPLET DE SMARTOHADA")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Créer le dossier de logs s'il n'existe pas
    os.makedirs("logs", exist_ok=True)
    
    # Exécuter tous les diagnostics
    check_static_files()
    check_template_inheritance()
    check_route_handlers()
    check_database_models()
    check_database_connection()
    check_javascript_console_errors()
    check_responsive_design()
    
    # Générer le rapport final
    generate_report()
    
    print_header("DIAGNOSTIC TERMINÉ")
    print("Un rapport complet a été généré: diagnostic_report.html")
    print("Pour plus de détails sur les routes, exécutez: python route_inspector.py")

if __name__ == "__main__":
    try:
        run_full_diagnostics()
    except Exception as e:
        logger.error(f"Erreur lors du diagnostic: {str(e)}")
        traceback.print_exc()
