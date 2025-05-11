import subprocess
import json
import os
import time

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")

def scrape_site(source, query):
    output_file = os.path.join(DATA_DIR, f"{source}.json")
    os.makedirs(DATA_DIR, exist_ok=True)

    # Chemin absolu vers le script spider
    script_path = os.path.join(BASE_DIR, "run_single_spider.py")

    # Exécute avec le bon cwd pour éviter les erreurs d'import
    subprocess.run(["python", script_path, source, query], cwd=BASE_DIR)

    # Attente du fichier
    timeout = 10
    waited = 0
    while not os.path.exists(output_file) and waited < timeout:
        time.sleep(0.5)
        waited += 0.5

    if not os.path.exists(output_file):
        raise FileNotFoundError(f"Fichier {output_file} introuvable après exécution du spider.")

    with open(output_file, encoding="utf-8") as f:
        return json.load(f)
