import sys
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Import spiders et scripts
from spiders.intersport_spider import IntersportSpider
from spiders.playwright_decathlon import scrape_decathlon
from spiders.playwright_intersport import scrape_intersport

def run_spider(source, search_query):
    if source == "decathlon":
        # Playwright
        scrape_decathlon(search_query)
    elif source == "intersport":
        # Playwright
        scrape_intersport(search_query)
    # Optionnel : si un jour tu veux réutiliser Scrapy
    elif source == "intersport_scrapy":
        process = CrawlerProcess(get_project_settings())
        process.crawl(IntersportSpider, search_query=search_query)
        process.start()
    else:
        raise ValueError("Source inconnue")

if __name__ == "__main__":
    run_spider(sys.argv[1], sys.argv[2])