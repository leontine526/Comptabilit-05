
#!/usr/bin/env python
"""
Script pour vérifier les gestionnaires d'erreurs de l'application
"""
import os
import sys
import logging
import importlib.util
import traceback

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("error_check")

def check_error_templates():
    """Vérifie l'existence et l'intégrité des templates d'erreur"""
    logger.info("=== Vérification des templates d'erreur ===")
    
    error_templates = {
        400: "templates/errors/400.html",
        403: "templates/errors/403.html",
        404: "templates/errors/404.html",
        500: "templates/errors/500.html",
        "db": "templates/errors/db_error.html"
    }
    
    all_ok = True
    
    for error_code, template_path in error_templates.items():
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Vérification basique du contenu
            if "{% extends" in content and "{% block content %}" in content:
                logger.info(f"✅ Template {error_code}: {template_path} est valide")
            else:
                logger.warning(f"⚠️ Template {error_code}: {template_path} pourrait être invalide (structure incorrecte)")
                all_ok = False
        else:
            logger.error(f"❌ Template {error_code}: {template_path} n'existe pas")
            all_ok = False
    
    return all_ok

def check_error_handlers():
    """Vérifie l'existence et l'intégrité des gestionnaires d'erreur"""
    logger.info("\n=== Vérification des gestionnaires d'erreur ===")
    
    try:
        # Vérifier error_handlers.py
        if os.path.exists("error_handlers.py"):
            spec = importlib.util.spec_from_file_location("error_handlers", "error_handlers.py")
            error_handlers = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(error_handlers)
            
            if hasattr(error_handlers, "register_error_handlers"):
                logger.info("✅ Module error_handlers.py contient register_error_handlers()")
            else:
                logger.error("❌ Module error_handlers.py ne contient pas register_error_handlers()")
                return False
        else:
            logger.error("❌ Fichier error_handlers.py n'existe pas")
            return False
            
        # Vérifier error_middleware.py
        if os.path.exists("error_middleware.py"):
            spec = importlib.util.spec_from_file_location("error_middleware", "error_middleware.py")
            error_middleware = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(error_middleware)
            
            if hasattr(error_middleware, "register_middleware"):
                logger.info("✅ Module error_middleware.py contient register_middleware()")
            else:
                logger.error("❌ Module error_middleware.py ne contient pas register_middleware()")
                return False
        else:
            logger.error("❌ Fichier error_middleware.py n'existe pas")
            return False
            
        return True
    except Exception as e:
        logger.error(f"❌ Erreur lors de la vérification des gestionnaires d'erreur: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def check_app_integration():
    """Vérifie l'intégration des gestionnaires d'erreur dans app.py"""
    logger.info("\n=== Vérification de l'intégration dans app.py ===")
    
    try:
        with open("app.py", "r", encoding="utf-8") as f:
            content = f.read()
            
        checks = {
            "Import error_handlers": "from error_handlers import register_error_handlers" in content,
            "Register error_handlers": "register_error_handlers(app)" in content,
            "Import error_middleware": "from error_middleware import register_middleware" in content,
            "Register middleware": "app.wsgi_app = register_middleware" in content
        }
        
        all_ok = True
        for check_name, result in checks.items():
            if result:
                logger.info(f"✅ {check_name}: OK")
            else:
                logger.error(f"❌ {check_name}: Manquant")
                all_ok = False
                
        return all_ok
    except Exception as e:
        logger.error(f"❌ Erreur lors de la vérification de l'intégration: {str(e)}")
        return False

if __name__ == "__main__":
    print("\n==================================================")
    print("======== VÉRIFICATION DES GESTIONNAIRES D'ERREUR ========")
    print("==================================================\n")
    
    templates_ok = check_error_templates()
    handlers_ok = check_error_handlers()
    integration_ok = check_app_integration()
    
    print("\n=== RÉSUMÉ ===")
    if templates_ok and handlers_ok and integration_ok:
        print("✅ Tous les contrôles ont réussi!")
        print("Les gestionnaires d'erreur semblent correctement configurés.")
    else:
        print("❌ Certains contrôles ont échoué.")
        print("Veuillez corriger les problèmes identifiés ci-dessus.")
    
    # Conseils supplémentaires
    print("\nConseils supplémentaires:")
    print("1. Vérifiez l'ordre d'enregistrement des gestionnaires d'erreur dans app.py")
    print("2. Assurez-vous que le middleware est enregistré APRÈS le gestionnaire d'erreurs")
    print("3. Redémarrez l'application après les modifications\n")
