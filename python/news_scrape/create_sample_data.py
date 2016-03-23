"""
Create sample data
URL: https://www.mb.com.ph/category/news/national/3
"""
from news_scraper import NewsArchiver
from bs4 import BeautifulSoup

def main():
    domain = "http://www.mb.com"
    source = "http://www.mb.com.ph/category/news/national"
    mb_archiver = NewsArchiver(domain)
    try:
        html = mb_archiver.fetch_html_raw(source)
        html_soup = BeautifulSoup(html)
    except Exception as e:
        print "Error during fetch_html_raw"
        print e
        return None

    data_file = open("./data/mb_sample_data.txt", "w")
    data_file.write(html_soup.prettify().encode("utf-8"))
    data_file.close()

if __name__ == "__main__":
    print "starting sample data"
    main()
    print "sample data finished"
