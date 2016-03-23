"""
Function that retrieves the relevant news in an html
Store and print html of all news
"""
import re
from bs4 import BeautifulSoup

html = BeautifulSoup(open("./data/mb_sample_data.txt", "r").read())

# Retrieve all news groups on this page
news_html = html.find_all(id=re.compile("post-[0-9]+"))
for news in news_html:
    print news.p.a.string

# Get the next page if available
page_html = html.find_all(class_=re.compile("pagi-next"))

print page_html


