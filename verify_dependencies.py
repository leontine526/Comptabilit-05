
#!/usr/bin/env python
"""
Script de vérification rapide des dépendances
"""
import sys
import importlib

def verify_dependencies():
    """Vérifie que toutes les dépendances critiques sont disponibles"""
    critical_deps = {
        'flask': 'Flask',
        'flask_login': 'Flask-Login',
        'flask_sqlalchemy': 'Flask-SQLAlchemy', 
        'flask_socketio': 'Flask-SocketIO',
        'sqlalchemy': 'SQLAlchemy',
        'dotenv': 'python-dotenv',
        'werkzeug': 'Werkzeug',
        'eventlet': 'eventlet',
        'numpy': 'NumPy',
        'sklearn': 'scikit-learn'
    }
    
    print("=== VÉRIFICATION DES DÉPENDANCES CRITIQUES ===")
    
    missing = []
    available = []
    
    for module, name in critical_deps.items():
        try:
            importlib.import_module(module)
            print(f"✅ {name}")
            available.append(name)
        except ImportError:
            print(f"❌ {name} - MANQUANT")
            missing.append(name)
    
    print(f"\n📊 RÉSUMÉ:")
    print(f"✅ Disponibles: {len(available)}/{len(critical_deps)}")
    print(f"❌ Manquants: {len(missing)}")
    
    if missing:
        print(f"\n⚠️ Dépendances manquantes:")
        for dep in missing:
            print(f"  - {dep}")
        print(f"\n🔧 Pour corriger, exécutez: python install_all_dependencies.py")
        return False
    else:
        print(f"\n🎉 Toutes les dépendances critiques sont disponibles!")
        return True

if __name__ == "__main__":
    success = verify_dependencies()
    sys.exit(0 if success else 1)
