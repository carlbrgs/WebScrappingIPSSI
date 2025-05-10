import scrapy
import json

class IntersportSpider(scrapy.Spider):
    name = "intersport"

    def __init__(self, search_query="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [f"https://www.sportsdirect.fr/search?q={search_query}"]
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        print(f"Spider initialized with search query: {search_query}")

    def parse(self, response):
        products = response.css('a[data-testid="product-card"]')
        name = response.css('p[data-testid="product-card-name-without-brand"]::text').get(default="Nom indisponible").strip()
        print (f"Nombre de produits trouvés : {len(products)}")
        if not products:
            self.logger.warning("Aucun produit trouvé sur la page.")
            return
        for product in products:
            link = product.css('::attr(href)').get()
            if link:
                full_link = response.urljoin(link)
                print(f"Product link: {full_link}")
                yield scrapy.Request(full_link, callback=self.parse_product, headers=self.headers, cb_kwargs={"name": name})

    def parse_product(self, response, name ):
        # Vérifier le prix et la promotion
        price_element = response.css('p[data-testid="price"]')
        spans = price_element.css('span::text').getall()

        if len(spans) == 2:
            # Cas avec promotion
            original_price = spans[1].replace(",", ".").replace("€", "").strip()
            current_price = spans[0].replace(",", ".").replace("€", "").strip()
            discount = round((1 - float(current_price) / float(original_price)) * 100, 2)
        else:
            # Cas sans promotion
            current_price = spans[0].replace(",", ".").replace("€", "").strip()
            original_price = current_price
            discount = 0

        # Extraire la description
        description = response.css('div[data-testid="description"] *::text').getall()
        description = " ".join([text.strip() for text in description if text.strip()]) or "Description indisponible"

        # Extraire les autres informations
        item = {
            "name": name,
            "link": response.url,
            "current_price": current_price,
            "original_price": original_price,
            "discount": discount,
            "image_url": response.css('img[data-testid="picture-img"]::attr(src)').get(),
            "description": description,
            "source": "Direct Sport"
        }

        print(item)

        # Sauvegarder les données dans un fichier JSON
        with open("data/intersport.json", "a", encoding="utf-8") as f:
            json.dump(item, f, ensure_ascii=False, indent=2)
            f.write(",\n")