import scrapy
import json
import os

class DecathlonSpider(scrapy.Spider):
    name = "decathlon"

    def __init__(self, search_query="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.search_query = search_query
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Accept-Language": "fr-FR,fr;q=0.9",
            "Accept-Encoding": "gzip, deflate",  # pas de 'br'
            "Connection": "keep-alive",
            "Referer": "https://www.google.com/",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Dest": "document"
        }
        # Crée le dossier de sortie si nécessaire
        os.makedirs("data", exist_ok=True)

    def start_requests(self):
        url = f"https://www.decathlon.fr/search?Ntt={self.search_query}"
        yield scrapy.Request(url=url, headers=self.headers, callback=self.parse)

    def parse(self, response):
        products = response.css('div.product-block-top-main')
        if not products:
            self.logger.warning("Aucun produit trouvé sur la page.")
            return

        self.logger.info(f"Nombre de produits trouvés : {len(products)}")

        for product in products:
            link = product.css('a.product-card-link::attr(href)').get()
            name = product.css('span.product-card-title::text').get(default="Nom indisponible").strip()
            if link:
                full_link = response.urljoin(link)
                yield scrapy.Request(
                    full_link,
                    callback=self.parse_product,
                    headers=self.headers,
                    cb_kwargs={"name": name}
                )

    def parse_product(self, response, name):
        # Récupérer les prix
        spans = response.css('p[data-testid="price"] span::text').getall()
        if len(spans) >= 2:
            original_price = spans[0].replace(",", ".").replace("€", "").strip()
            current_price = spans[1].replace(",", ".").replace("€", "").strip()
            discount = round((1 - float(current_price) / float(original_price)) * 100, 2)
        else:
            current_price = spans[0].replace(",", ".").replace("€", "").strip()
            original_price = current_price
            discount = 0

        # Description
        description = response.css('div[data-testid="accordion-group"] div[data-testid="accordion-details"]::text').get()
        if description:
            description = description.strip()
        else:
            description = "Description indisponible"

        # Image
        image_url = response.css('img.product-image::attr(src)').get()

        item = {
            "name": name,
            "link": response.url,
            "current_price": current_price,
            "original_price": original_price,
            "discount": discount,
            "image_url": image_url,
            "description": description,
            "source": "Decathlon"
        }

        print(item)

        # Sauvegarde JSON
        with open("data/decathlon.json", "a", encoding="utf-8") as f:
            json.dump(item, f, ensure_ascii=False)
            f.write(",\n")
