import subprocess
import json
import os

def scrape_site(source, query):
    output_file = f"data/{source}.json"
    os.makedirs("data", exist_ok=True)  # Crée le dossier s'il n'existe pas
    subprocess.run(["python", "ecommerce_comparator/run_single_spider.py", source, query])
    with open(output_file, encoding="utf-8") as f:
        return json.load(f)