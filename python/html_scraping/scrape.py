"""
An example html web scraper
Sources:
    http://docs.python-guide.org/en/latest/scenarios/scrape/
"""
from lxml import html
import requests

def scrape():
    """
    basic html scraping
    """
    source = "http://econpy.pythonanywhere.com/ex/001.html"
    page = requests.get(source)
    tree = html.fromstring(page.content)
    # create a list of buyers
    buyers = tree.xpath('//div[@title="buyer-name"]/text()')
    # create a list of proces
    prices = tree.xpath('//span[@class="item-price"]/text()')

    print "buyers: ", buyers
    print "prices: ", prices

if __name__ == "__main__":
    print "main"
    scrape()
