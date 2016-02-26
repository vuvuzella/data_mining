"""
An example html web scraper
Sources:
    http://docs.python-guide.org/en/latest/scenarios/scrape/
Description:
    Scrapes the buyers and prices from all pages of
    http://econpy.pythonanywhere.com/ex/001.html to 005.html
"""
from lxml import html
import requests

def scrape(web_source):
    """
    basic html scraping
    """
    page = requests.get(web_source)
    tree = html.fromstring(page.content)
    links_list = get_succeeding_links(tree)
    buyer_price_tuple_list = []
    for pair in get_buyer_price(tree):
        buyer_price_tuple_list.append(pair)
    # do the same for the succeeding links
    for link in links_list:
        page = requests.get(link)
        tree = html.fromstring(page.content)
        for pair in iter(get_buyer_price(tree)):
            buyer_price_tuple_list.append(pair)
    # create a list of buyers
    # buyers = tree.xpath('//div[@title="buyer-name"]/text()')
    # create a list of prices
    # prices = tree.xpath('//span[@class="item-price"]/text()')
    # create a list of buyers and prices
    # buyers_prices = tree.xpath('//div[@title="buyer-info"]')
    # print the list of buyers
    # print "buyers: ", buyers
    # print the list of prices
    # print "prices: ", prices
    #print the buyer and price as a tuple
    for pair in buyer_price_tuple_list:
        print pair

def get_buyer_price(content_tree):
    """
    Parameters:
        content_tree - an Element class variable
    """
    buyer_price_list = []
    xpath = '//div[@title="buyer-info"]'
    buyers_prices = content_tree.xpath(xpath)
    if len(buyers_prices) > 0:
        for pair in buyers_prices:
            buyer_price_list.append((pair.find("div").text, pair.find("span").text))
    else:
        # nothing was retrieved
        print "Nothing was retrieved with ", xpath
    return buyer_price_list

def get_succeeding_links(content_tree):
    """
    Retrieves succeeding links to crawl and scrape
    """
    links_list = []
    # XPATH 1.0 does not support regular expression. hassle man!
    # boolean(number(...)) taken from
    # http://stackoverflow.com/questions/21405267/xpath-using-regex-in-contains-function
    xpath = '//a[boolean(number(substring-before(substring-after(@href, "http://econpy.pythonanywhere.com/ex/"), ".html")))]'
    link_children = content_tree.xpath(xpath)
    if len(link_children) > 0:
        for pair in link_children:
            links_list.append(pair.get("href"))
    else:
        # nothing was retrieved
        print "Nothing was retrieved with ", xpath
    return links_list


if __name__ == "__main__":
    source = "http://econpy.pythonanywhere.com/ex/001.html"
    scrape(source)
