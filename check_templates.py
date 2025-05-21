
#!/usr/bin/env python
"""
Script pour vérifier tous les templates et leur structure
Identifie les problèmes courants dans les templates Jinja2
"""
import os
import re
import sys
import logging
from collections import defaultdict

# Configuration du logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("template_checker")

def check_templates():
    """Vérifie tous les templates dans le dossier templates"""
    print("=== VÉRIFICATION DES TEMPLATES ===")
    
    # Vérifier si le dossier templates existe
    if not os.path.isdir("templates"):
        print("❌ Dossier templates non trouvé!")
        return False
    
    # Récupérer tous les fichiers HTML
    template_files = []
    for root, _, files in os.walk("templates"):
        for file in files:
            if file.endswith(".html"):
                template_files.append(os.path.join(root, file))
    
    print(f"Nombre de templates trouvés: {len(template_files)}")
    
    # Statistiques
    stats = {
        "extends_base": 0,
        "extends_other": 0,
        "no_extends": 0,
        "missing_blocks": defaultdict(list),
        "undefined_blocks": defaultdict(list),
        "missing_endblock": [],
        "missing_endif": [],
        "missing_endfor": [],
        "missing_title": [],
        "problematic_templates": []
    }
    
    # Vérifier chaque template
    for template_file in template_files:
        relative_path = os.path.relpath(template_file, "templates")
        print(f"\nVérification de: {relative_path}")
        
        with open(template_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Vérifier l'extension
        extends_match = re.search(r'{%\s*extends\s+[\'"]([^\'"]+)[\'"]', content)
        if extends_match:
            extended_template = extends_match.group(1)
            if extended_template == "base.html":
                stats["extends_base"] += 1
                print(f"✅ Étend le template de base")
            else:
                stats["extends_other"] += 1
                print(f"✅ Étend le template: {extended_template}")
                
            # Vérifier si le template étendu existe
            extended_path = os.path.join("templates", extended_template)
            if not os.path.exists(extended_path):
                print(f"❌ Le template étendu n'existe pas: {extended_template}")
                stats["problematic_templates"].append((relative_path, f"Template étendu manquant: {extended_template}"))
        else:
            # C'est peut-être le template de base ou un template qui devrait étendre
            if "base.html" not in template_file and "layout.html" not in template_file:
                stats["no_extends"] += 1
                print(f"⚠️ Ne semble pas étendre un autre template")
        
        # Vérifier les blocs
        block_starts = re.findall(r'{%\s*block\s+([^\s%]+)\s*%}', content)
        block_ends = re.findall(r'{%\s*endblock(?:\s+[^\s%]+)?\s*%}', content)
        
        if len(block_starts) != len(block_ends):
            print(f"❌ Certains blocs ne sont pas fermés correctement: {len(block_starts)} ouvertures vs {len(block_ends)} fermetures")
            stats["missing_endblock"].append(relative_path)
            stats["problematic_templates"].append((relative_path, "Blocs non fermés"))
        
        # Vérifier si le bloc title est défini
        if "block title" not in content and "base.html" not in template_file:
            print("⚠️ Pas de bloc title défini")
            stats["missing_title"].append(relative_path)
        
        # Vérifier les if sans endif
        if_count = len(re.findall(r'{%\s*if\s+', content))
        endif_count = len(re.findall(r'{%\s*endif\s*%}', content))
        
        if if_count != endif_count:
            print(f"❌ Conditions if non fermées: {if_count} if vs {endif_count} endif")
            stats["missing_endif"].append(relative_path)
            stats["problematic_templates"].append((relative_path, "Conditions if non fermées"))
        
        # Vérifier les for sans endfor
        for_count = len(re.findall(r'{%\s*for\s+', content))
        endfor_count = len(re.findall(r'{%\s*endfor\s*%}', content))
        
        if for_count != endfor_count:
            print(f"❌ Boucles for non fermées: {for_count} for vs {endfor_count} endfor")
            stats["missing_endfor"].append(relative_path)
            stats["problematic_templates"].append((relative_path, "Boucles for non fermées"))
        
        # Vérifier les liens statiques
        static_links = re.findall(r'(href|src)=[\'"](.*?)[\'"]', content)
        for link_type, link in static_links:
            if link.startswith("/static/") or link.startswith("static/"):
                # Vérifier si le fichier existe
                clean_link = link.lstrip("/")
                if not os.path.exists(clean_link):
                    print(f"⚠️ Lien vers un fichier statique qui n'existe pas: {link}")
                    stats["problematic_templates"].append((relative_path, f"Fichier statique manquant: {link}"))
    
    # Afficher le résumé
    print("\n=== RÉSUMÉ DE LA VÉRIFICATION DES TEMPLATES ===")
    print(f"Templates qui étendent base.html: {stats['extends_base']}")
    print(f"Templates qui étendent d'autres templates: {stats['extends_other']}")
    print(f"Templates qui n'étendent aucun template: {stats['no_extends']}")
    print(f"Templates avec des blocs non fermés: {len(stats['missing_endblock'])}")
    print(f"Templates avec des conditions if non fermées: {len(stats['missing_endif'])}")
    print(f"Templates avec des boucles for non fermées: {len(stats['missing_endfor'])}")
    print(f"Templates sans bloc title défini: {len(stats['missing_title'])}")
    
    # Afficher les templates problématiques
    if stats["problematic_templates"]:
        print("\n=== TEMPLATES AVEC PROBLÈMES ===")
        for template, problem in stats["problematic_templates"]:
            print(f"- {template}: {problem}")
    else:
        print("\n✅ Aucun problème critique détecté dans les templates")
    
    return True

if __name__ == "__main__":
    try:
        check_templates()
    except Exception as e:
        logger.error(f"Erreur lors de la vérification des templates: {str(e)}")
        import traceback
        traceback.print_exc()
