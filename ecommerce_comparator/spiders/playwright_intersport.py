from playwright.sync_api import sync_playwright
import json
import os
import sys
import urllib.parse

def scrape_intersport(search_query=""):
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)
    output_path = os.path.join(BASE_DIR, "data", "intersport.json")

    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=50)
        page = browser.new_page()

        encoded_query = urllib.parse.quote_plus(search_query)
        url = f"https://www.sportsdirect.fr/search?q={encoded_query}"
        page.goto(url, timeout=60000)
        page.wait_for_timeout(3000)

        cards = page.query_selector_all('a[data-testid="product-card"]')
        print(f"Nombre de produits trouvés : {len(cards)}")

        for card in cards[:5]:
            name_el = card.query_selector('p[data-testid="product-card-name-without-brand"]')
            link_el = card
            img_el = card.query_selector('img[data-testid="picture-img"]')

            if not name_el or not link_el:
                continue

            name = name_el.inner_text().strip()
            link = link_el.get_attribute("href")
            if not link.startswith("http"):
                link = "https://www.sportsdirect.fr" + link
            image_url = img_el.get_attribute("src") if img_el else ""

            product_page = browser.new_page()
            product_page.goto(link, timeout=60000)
            product_page.wait_for_timeout(2000)

            price_container = product_page.query_selector('p[data-testid="price"]')
            spans = price_container.query_selector_all('span') if price_container else []
            prices = [s.inner_text().strip().replace(",", ".").replace("€", "") for s in spans]

            if len(prices) == 2:
                current_price = prices[0]
                original_price = prices[1]
                discount = round((1 - float(current_price) / float(original_price)) * 100, 2)
            elif len(prices) == 1:
                current_price = original_price = prices[0]
                discount = 0
            else:
                current_price = original_price = "0"
                discount = 0

            try:
                toggle = product_page.query_selector('div[data-testid="accordion-group"] div[data-testid="accordion-details"] button')
                if toggle:
                    toggle.click()
                    product_page.wait_for_timeout(500)  # Attendre que le contenu charge
            except Exception as e:
                print(f"⚠️ Impossible de cliquer sur l'accordéon description : {e}")
            try:
                product_page.wait_for_selector('div[data-testid="description"]', timeout=3000)
                desc_container = product_page.query_selector('div[data-testid="description"]')
                description = desc_container.inner_text().strip() if desc_container else "Description indisponible"
            except Exception as e:
                print(f"⚠️ Erreur description : {e}")
                description = "Description indisponible"
            product_page.close()

            item = {
                "name": name,
                "link": link,
                "current_price": current_price,
                "original_price": original_price,
                "discount": discount,
                "description": description,
                "image_url": image_url,
                "source": "Intersport"
            }
            results.append(item)

            print(f"✅ {name} - {current_price}€")
            print(f"🔗 Lien: {link}")
            print(f"🖼️ Image: {image_url}")
            print(f"💰 Prix original: {original_price}€")
            print(f"📉 Réduction: {discount}%")
            print(f"📜 Description: {description}\n")

        # Écriture JSON propre
        # Supprimer les anciennes données du fichier JSON s'il existe
        if os.path.exists(output_path):
            os.remove(output_path)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
        print(f"Produits enregistrés dans {output_path}")
        browser.close()

    print(f"\n🎯 {len(results)} produit(s) enregistrés dans {output_path} pour '{search_query}'")

if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "nike air force"
    scrape_intersport(query)
