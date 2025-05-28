
#!/usr/bin/env python
"""
Diagnostic rapide des dépendances
"""
import sys
import importlib

def check_dependencies():
    """Vérifie rapidement les dépendances critiques"""
    critical_deps = {
        "flask": "Flask",
        "flask_login": "Flask-Login", 
        "flask_sqlalchemy": "Flask-SQLAlchemy",
        "flask_socketio": "Flask-SocketIO",
        "sqlalchemy": "SQLAlchemy",
        "dotenv": "python-dotenv",
        "werkzeug": "Werkzeug",
        "eventlet": "eventlet"
    }
    
    print("=== DIAGNOSTIC RAPIDE DES DÉPENDANCES ===")
    missing = []
    
    for module, name in critical_deps.items():
        try:
            importlib.import_module(module)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} - MANQUANT")
            missing.append(name)
    
    if missing:
        print(f"\n⚠️ {len(missing)} dépendances manquantes:")
        for dep in missing:
            print(f"  - {dep}")
        print("\nExécutez: python install_replit_dependencies.py")
        return False
    else:
        print("\n🎉 Toutes les dépendances critiques sont disponibles!")
        return True

if __name__ == "__main__":
    success = check_dependencies()
    sys.exit(0 if success else 1)
