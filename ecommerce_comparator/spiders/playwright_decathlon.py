from playwright.sync_api import sync_playwright
import json
import os
import sys
import urllib.parse

def scrape_decathlon(search_query=""):
    os.makedirs("data", exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=50)
        page = browser.new_page()

        encoded_query = urllib.parse.quote_plus(search_query)
        url = f"https://www.decathlon.fr/search?Ntt={encoded_query}"

        page.goto(url, timeout=60000)
        page.wait_for_timeout(3000)

        # Accepter les cookies
        try:
            cookie_button = page.query_selector('button#didomi-notice-agree-button')
            if cookie_button:
                cookie_button.click()
                page.wait_for_timeout(2000)
                print("Cookies acceptés.")
            else:
                print("Bouton d'acceptation des cookies non trouvé.")
        except Exception as e:
            print(f"Erreur lors de l'acceptation des cookies : {e}")

        # Scraper les produits
        cards = page.query_selector_all("div.product-block-top-main")
        print(f"Nombre de produits trouvés : {len(cards)}")

        # Ouvrir le fichier JSON en mode append
        with open("../data/decathlon.json", "a", encoding="utf-8") as f:
            for card in cards:
                name_el = card.query_selector("a.product-title h2")
                link_el = card.query_selector("a.product-title[href]")
                image_el = card.query_selector("div.vtmn-relative a img[src]")

                if not (name_el and link_el):
                    print("Nom ou lien indisponible pour un produit.")
                    continue

                name = name_el.inner_text().strip()
                link = "https://www.decathlon.fr" + link_el.get_attribute("href")
                image_url = image_el.get_attribute("src")

                # 👉 Ouvrir la page produit
                product_page = browser.new_page()
                product_page.goto(link, timeout=60000)
                product_page.wait_for_timeout(2000)

                # Vérifier les prix
                old_price_el = product_page.query_selector('span[aria-label="Ancien prix"]')
                current_price_el = product_page.query_selector('span.vtmn-price')

                if old_price_el and current_price_el:
                    # Cas avec promotion
                    original_price = old_price_el.inner_text().strip().replace(",", ".").replace("€", "")
                    current_price = current_price_el.inner_text().strip().replace(",", ".").replace("€", "")
                    discount = round((1 - float(current_price) / float(original_price)) * 100, 2)
                elif current_price_el:
                    # Cas sans promotion
                    current_price = current_price_el.inner_text().strip().replace(",", ".").replace("€", "")
                    original_price = current_price
                    discount = 0
                else:
                    # Aucun prix trouvé
                    current_price = "0"
                    original_price = "0"
                    discount = 0

                # Description
                desc_el1 = product_page.query_selector('p.vtmn-text-base.vtmn-mt-2')
                desc_el2 = product_page.query_selector('div.vtmn-text-base.vtmn-mt-0')
                description = ""
                if desc_el1:
                    description += desc_el1.inner_text().strip()
                if desc_el2 and desc_el1 != desc_el2:
                    description += " " + desc_el2.inner_text().strip()
                if not description:
                    description = "Description indisponible"

                # Fermer la page produit
                product_page.close()

                # Ajouter les infos au résultat
                item = {
                    "name": name,
                    "link": link,
                    "current_price": current_price,
                    "original_price": original_price,
                    "discount": discount,
                    "description": description,
                    "image_url": image_url,
                    "source": "Decathlon"
                }

                # Écrire chaque produit dans le fichier JSON
                f.write(json.dumps(item, ensure_ascii=False, indent=2) + ",\n")

                print(f"✅ {name} - {current_price}€")
                print(f"🔗 Lien: {link}")
                print(f"🖼️ Image: {image_url}")
                print(f"💰 Prix original: {original_price}€")
                print(f"📉 Réduction: {discount}%")
                print(f"📜 Description: {description}\n")

        browser.close()

    print(f"\n🎯 Produits enregistrés pour '{search_query}'.")

if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "nike air force"
    scrape_decathlon(query)