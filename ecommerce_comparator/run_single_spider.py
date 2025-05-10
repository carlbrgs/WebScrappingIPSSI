import sys
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from spiders.intersport_spider import IntersportSpider
from spiders.decathlon_spider import DecathlonSpider

def run_spider(source, search_query):
    process = CrawlerProcess(get_project_settings())

    if source == "intersport":
        process.crawl(IntersportSpider, search_query=search_query, use_playwright=True)
    elif source == "decathlon":
        process.crawl(DecathlonSpider, search_query=search_query)
    else:
        raise ValueError("Source inconnue")

    process.start()

if __name__ == "__main__":
    run_spider(sys.argv[1], sys.argv[2])
