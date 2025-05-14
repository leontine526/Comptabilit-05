
#!/usr/bin/env python
"""
Script complet pour vérifier toutes les routes de l'application
et identifier les problèmes potentiels à long terme
"""
import os
import sys
import logging
import traceback
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """
    Fonction principale qui exécute toutes les vérifications de routes
    """
    print("===== VÉRIFICATION COMPLÈTE DES ROUTES =====")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 45)
    
    # Vérifier si le serveur est en cours d'exécution
    try:
        import requests
        response = requests.get("http://localhost:5000/", timeout=2)
        print("\n✓ Serveur en cours d'exécution")
    except:
        print("\n⚠ Serveur non accessible. Certains tests ne fonctionneront pas.")
    
    # Partie 1: Analyse statique des routes
    print("\n1. ANALYSE STATIQUE DES ROUTES")
    print("-" * 30)
    try:
        from route_inspector import inspect_routes
        inspect_routes()
    except Exception as e:
        print(f"Erreur lors de l'analyse statique: {str(e)}")
        traceback.print_exc()
    
    # Partie 2: Vérification des modèles et relations
    print("\n2. VÉRIFICATION DES MODÈLES ET RELATIONS DB")
    print("-" * 45)
    try:
        # Import l'application et les modèles
        from app import app, db
        from models import User, Exercise, Account, Transaction, TransactionItem
        from models import Document, Workgroup, Message, Note, Notification
        
        with app.app_context():
            models = [User, Exercise, Account, Transaction, TransactionItem,
                     Document, Workgroup, Message, Note, Notification]
            
            print(f"Nombre de modèles vérifiés: {len(models)}")
            
            # Vérifier chaque modèle
            for model in models:
                print(f"\nModèle: {model.__name__}")
                # Vérifier les relations
                relationships = []
                for attr_name in dir(model):
                    if not attr_name.startswith('_'):
                        attr = getattr(model, attr_name)
                        if hasattr(attr, 'prop') and hasattr(attr.prop, 'direction'):
                            relationships.append((attr_name, attr.prop.direction.name))
                
                if relationships:
                    print(f"  Relations ({len(relationships)}):")
                    for rel_name, direction in relationships:
                        print(f"    - {rel_name} ({direction})")
                else:
                    print("  Aucune relation trouvée")
        
    except Exception as e:
        print(f"Erreur lors de la vérification des modèles: {str(e)}")
        traceback.print_exc()
    
    # Partie 3: Test des routes accessibles
    print("\n3. TEST DES ROUTES ACCESSIBLES")
    print("-" * 30)
    try:
        from route_tester import test_routes
        test_routes()
    except Exception as e:
        print(f"Erreur lors des tests de routes: {str(e)}")
        traceback.print_exc()
    
    # Partie 4: Vérification des routes à risque
    print("\n4. VÉRIFICATION DES ROUTES À RISQUE")
    print("-" * 35)
    try:
        from check_routes import check_routes
        check_routes()
    except Exception as e:
        print(f"Erreur lors de la vérification des routes à risque: {str(e)}")
        traceback.print_exc()
    
    # Conclusion
    print("\n===== CONCLUSION =====")
    print("La vérification complète des routes est terminée.")
    print("Consultez le rapport HTML généré pour plus de détails.")
    print("=" * 24)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Erreur lors de l'exécution du script: {str(e)}")
        traceback.print_exc()
