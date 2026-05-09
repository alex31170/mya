#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import sys
from pathlib import Path

# Configuration
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.JPG', '.JPEG', '.PNG', '.GIF'}
DOCS_DIR = Path(__file__).parent.absolute()
DATA_JSON_PATH = DOCS_DIR / 'data.json'
DATA_JS_PATH = DOCS_DIR / 'data.js'


def get_images_in_directory(dir_path):
    """Récupère toutes les images d'un répertoire."""
    try:
        images = []
        if dir_path.exists() and dir_path.is_dir():
            for file in sorted(dir_path.iterdir()):
                if file.is_file() and file.suffix in IMAGE_EXTENSIONS:
                    relative_path = file.relative_to(DOCS_DIR).as_posix()
                    images.append(relative_path)
        return images
    except Exception as e:
        print(f"[!] Erreur lors de la lecture de {dir_path}: {e}", file=sys.stderr)
        return []


def update_gallery_recursively(node, dir_path, relative_path=""):
    """Met à jour récursivement UNIQUEMENT la section gallery des données existantes."""
    # Mettre à jour la galerie pour ce nœud
    gallery = get_images_in_directory(dir_path)
    node['gallery'] = gallery
    
    # Parcourir les sous-répertoires
    try:
        if dir_path.exists() and dir_path.is_dir():
            subdirs = {}
            for item in sorted(dir_path.iterdir()):
                if item.is_dir() and not item.name.startswith('.'):
                    subdirs[item.name] = item
            
            # Mettre à jour les enfants existants
            for child in node.get('children', []):
                child_name = child.get('name')
                if child_name in subdirs:
                    sub_relative_path = f"{relative_path}/{child_name}" if relative_path else child_name
                    update_gallery_recursively(child, subdirs[child_name], sub_relative_path)
    except Exception as e:
        print(f"[!] Erreur lors du scan de {dir_path}: {e}", file=sys.stderr)


def print_summary(data, indent=0):
    """Affiche un résumé des images trouvées."""
    prefix = "  " * indent
    
    if data['gallery']:
        name = data['name']
        count = len(data['gallery'])
        print(f"{prefix}📁 {name}: {count} image(s)")
    
    for child in data['children']:
        print_summary(child, indent + 1)


def update_data_files():
    """Met à jour les fichiers data.json et data.js (uniquement les galleries)."""
    print("[*] Chargement des données existantes...", file=sys.stderr)
    
    # Charger les données existantes
    try:
        with open(DATA_JSON_PATH, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
        print("[OK] data.json chargé", file=sys.stderr)
    except Exception as e:
        print(f"[!] Erreur lors de la lecture de data.json: {e}", file=sys.stderr)
        return False, None
    
    print("[*] Scan des répertoires et mise à jour des galleries...", file=sys.stderr)
    
    # Mettre à jour uniquement les galleries
    update_gallery_recursively(data, DOCS_DIR, "")
    
    # Mettre à jour la galerie racine
    data['gallery'] = get_images_in_directory(DOCS_DIR)
    
    print("[OK] Structure mise à jour (galleries uniquement)", file=sys.stderr)
    
    # Sauvegarder data.json
    try:
        with open(DATA_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print("[OK] data.json mis à jour", file=sys.stderr)
    except Exception as e:
        print(f"[!] Erreur lors de la sauvegarde de data.json: {e}", file=sys.stderr)
        return False
    
    # Sauvegarder data.js
    try:
        json_str = json.dumps(data, ensure_ascii=False)
        js_content = f"window.SITE_DATA = {json_str};"
        with open(DATA_JS_PATH, 'w', encoding='utf-8') as f:
            f.write(js_content)
        print("[OK] data.js mis à jour", file=sys.stderr)
    except Exception as e:
        print(f"[!] Erreur lors de la sauvegarde de data.js: {e}", file=sys.stderr)
        return False
    
    return True, data


if __name__ == "__main__":
    print("\n[START] Démarrage de la mise à jour des données...", file=sys.stderr)
    print("", file=sys.stderr)
    
    success, data = update_data_files()
    
    if success:
        print("", file=sys.stderr)
        print("[RESUME] Images trouvées:", file=sys.stderr)
        print("=" * 50, file=sys.stderr)
        print_summary(data)
        print("", file=sys.stderr)
        print("[SUCCESS] Mise à jour terminée!", file=sys.stderr)
        print("", file=sys.stderr)
        sys.exit(0)
    else:
        print("", file=sys.stderr)
        print("[ERROR] Erreur lors de la mise à jour", file=sys.stderr)
        print("", file=sys.stderr)
        sys.exit(1)
