"""
A news scraper that gathers the following data:
    1. News title
    2. Presidential Candidate involved
    3. News Content
    4. Link to the news
    5. News Company source
    6. Date of news published
    7. Date of Retrieval

General Structure:
    1. Crawler/Scraper
    2. Parser
    3. Database
    4. Archiver - for HTML scraping
    5. RSS archiver? or Real time changes listener
    6. Logger

Sample Website scraped:
    1. www.mb.com (The Manila Bulletin)
"""
import re
import requests
import urllib2
import datetime
import calendar
from pymongo import MongoClient
from scraper_logger import ScraperLogger
from bs4 import BeautifulSoup

class NewsArchiver(object):
    """
    Archiver class stores the data to be used for visualization.
    Data is then being constantly updated by another listener
    class that listens for changes or arrival of new news.
    Class Roles:
        1. Download news archives from a news domain site
        2. Store the data in a database for persistence
        3. Saved data can be processed by a scraper
        4. Saved data can be outputted to a file in JSON format
           or CSV format
    """
    def __init__(self, domain):
        """
        Initialization of Archiver class
        """
        self._domain = domain
        self._from_year = None
        self._from_month = None
        self._from_day = None
        self._to_year = None
        self._to_month = None
        self._to_day = None
        self._start_directory = None
        self._user_agent = {}
        self._model = None

    def start_archiving(self):
        """
        Initiate the archiving after initial setup has been done
        1. Check if from date is not none:
            if NONE: Use today's date
            else: Use set date
        2. Check if to date is not none:
            if NONE: Use today's date
            else Use set date
        3. Set first page to scan
        4. Get all news posts in <div id="container">
        5. For each news, If news is within the date interval:
            4.1 Store <div id=post-[0-9]+>
            4.2 Crawl to read-more then:
                4.2.1 Store <div id="content">
        6. If starting page has pagination, go to next page 
           and repeat from step 4
        Notes: On checking date
        """

        # Check if end time was set
        # throw exception of not set
        if self._to_year == None or \
           self._to_month == None or \
           self._to_day == None:
            raise "Required End date is not set"

        # Check if start time was set
        # Use current date as start date
        if self._from_year == None or \
           self._from_month == None or \
           self._from_day == None:
            year = datetime.date.today().year
            month = datetime.date.today().month
            day = datetime.date.today().day
            # Set to-date to today's date
            self.set_from_date(year, month, day)

        # Check if start directory was set
        # throw exception if not set
        if self._start_directory == None:
            raise "Required Start directory is not set"

        # Check the domain if it has the 'http://' prefix
        if self.check_domain_schema() is not True:
            self._domain = "http://" + self._domain

        source = self._domain + self._start_directory

        to_date = datetime.datetime(self._to_year,
                                self._to_month,
                                self._to_day)
        from_date = datetime.datetime(self._from_year,
                                  self._from_month,
                                  self._from_day)

        # Check if connected to mongoDB data store
        if self._model is None:
            # connect to db server and get a handle
            self._model = MongoClient('localhost', 27017).test_news

        # Retrieve the starting page to gather news links
        while True:
            print "Retrieving html from", source
            initial_html = self.get_html_raw(source)
            bs4_fetched_data = BeautifulSoup(initial_html, "html.parser")
            posts_regex = re.compile("post-[0-9]+")
            posts = bs4_fetched_data.find_all(id=posts_regex)

            for index in range(len(posts)):
                # check if article is within the time delta
                # get published year, month and day meta data
                article_date = self.get_article_date(posts[index])
                if from_date >= article_date >= to_date:
                    # Check if article exists in the database
                    # if it does not exist, add to database
                    # else move on to the next news article
                    article_title = self.get_article_title(posts[index])
                    print "processing", article_title
                    if len(list(self._model.articles.find({"article_title" : article_title}))) <= 0:
                        article_link = self.get_article_link(posts[index])
                        article_html = self.get_html_raw(article_link)
                        bs4_article = BeautifulSoup(article_html, "html.parser")
                        article_author = self.get_article_author(bs4_article)
                        article_body = self.get_article_body(bs4_article)
                        json_article = {
                            "article_title" : article_title,
                            "article_author" : article_author,
                            "article_body" : article_body,
                            "article_link" : article_link,
                            "article_html" : article_html,
                            "article_date" : article_date
                        }
                        # add the article to DB
                        client = MongoClient('localhost', 27017)
                        db_test_news = client['test_news']
                        self.add_article_to_db(json_article, db_test_news)
                    else:
                        # Article already present in database
                        # skip to the next article
                        print "Article present in db. Skipping..."
                        pass
                else:
                    # date of article is already out of scope
                    # stop the archiving
                    print "Stopping archiving"
                    return
                # when all posts have been processed and the out-of
                # -bounds article has not yet been found, crawl to 
                # the next link and start all over again.
            print "going next page"
            source = bs4_fetched_data.find_all(class_="pagi-next")
            if len(source) > 0:
                source = source[0]['href'].encode("utf-8")
            else:
                # No more next page
                print "No more next page. Stopping archiving"
                return

    def set_from_date(self, year, month, day):
        """
        Set the starting date to scrape news from.
        If no date was set before starting to archive,
        Use today's date.
        """
        self._from_year = year
        self._from_month = month
        self._from_day = day

    def set_to_date(self, year, month, day):
        """
        Set the ending date to scrape news from.
        If no date was set before starting to archive,
        to dates has to have value. Error if none!
        """
        self._to_year = year
        self._to_month = month
        self._to_day = day

    def set_start_directory(self, start_dir):
        """
        Sets the directory to be appended to the domain
        where the archiving will start
        """
        self._start_directory = start_dir

    def get_all_posts(self, bs4_data, html_attribute, value):
        """
        Returns a list of available news posts in a specific
        BeautifulSoup data
        TODO: Recursive
        exit condition:
            to date has been reached or
            pagi-next was not found
        """
        if type(bs4_data) is not BeautifulSoup:
            raise TypeError
        posts_list = bs4_data.find_all(html_attribute=re.compile(value))
        if len(posts_list) == 0:
            raise "No match found", html_attribute, value
        return posts_list

    def get_html_raw(self, url, num_retries=2):
        """
        Returns the raw html from the specified url
        Note: no 'http://' format checking in URL
        TODO: Add logging
        """
        html = ""
        if num_retries >= 0:
            try:
                response = requests.get(url)
                html = response.content
            except requests.exceptions.RequestException as e:
                print "Request Error Occurred", type(e)
                return self.get_html_raw(url, num_retries=num_retries-1)
        else:
            print "Maximum retries reached. Aborting get_html_raw"

        return html

    def check_domain_schema(self):
        """
        Checks if http is found in the domain
        Returns boolean
        """
        retVal = False
        url = self._domain.split("//")
        if len(url) > 0:
            if "http" in url[0]:
                retVal = True
        return retVal

    def set_user_agent(self, agent):
        """
        http://www.mb.com.ph requires no user agent
        """
        for k,v in agent.iteritems():
            self._user_agent[k] = v

    def set_filter(self, filter_list):
        pass

    def get_article_title(self, bs4_data):
        """
        Return the title of an article bs4 data
        """
        bs4_title = ""
        container_title = bs4_data.find_all(class_="catname testCSS")
        if len(list(container_title)) > 0:
            if len(list(container_title[0].find_all("a"))) > 0:
                bs4_title = container_title[0].find_all("a")[0]
            else:
                raise "No Title found"
        else:
            raise "catname testCSS not found"
        return bs4_title.text.strip()

    def get_article_link(self, bs4_data):
        """
        Return the link to the article itself
        """
        return bs4_data.p.a['href']

    def get_article_body(self, bs4_data):
        """
        Return the body of the article
        """
        post_regex = re.compile("post-[0-9]+")
        post_div_bs4 = bs4_data.find_all(id=post_regex)
        post_body = post_div_bs4[0].find_all('p')
        body = ""
        for paragraph in post_body:
            body += paragraph.text.strip() + "\n"
        return body

    def get_article_author(self, bs4_post):
        """
        Returns the author of the article
        """
        container_author = bs4_post.find_all(class_="single_postmeta")[0].find_all("a")
        article_author = ""
        if len(container_author) > 0:
            article_author = container_author[0].text.strip()
        return article_author

    def get_article_date(self, bs4_post):
        """
        Returns the date of the article
        """
        date_list = bs4_post.span.text.strip().split(" ")
        date_list[0] = list(calendar.month_abbr).index(date_list[0][:3])
        date_list[1] = date_list[1][:2] # remove comma from date
        print date_list
        article_date = datetime.datetime(int(date_list[2]),
                                     date_list[0],
                                     int(date_list[1]))
        return article_date

    def add_article_to_db(self, json_article, mongodb_handle):
        """
        Returns the ObjectId
        """
        print "Storing", json_article['article_title'], " to db"
        return mongodb_handle.articles.insert_one(json_article)

if __name__ == "__main__":
    # data_file = open("./data/mb_sample_data.txt", "r")
    # article_data_file = open("./data/mb_article_sample.txt", "r")
    source = "www.mb.com.ph"
    mb = NewsArchiver(source)
    # bs4_data = BeautifulSoup(data_file.read(), "html.parser")
    # posts = bs4_data.find_all(class_=re.compile("post-[0-9]+"))
    # article_html = mb.get_html_raw(posts[0].p.a['href'])
    # bs4_data = BeautifulSoup(article_html)
    # all_links = bs4_data.find_all(class_="single_postmeta")
    # print all_links
    # print all_links[0].find_all("a")[0].text.strip()
    # to_year = datetime.date.today().year
    # to_month = datetime.date.today().month
    # to_day = datetime.date.today().day
    # mb.set_to_date(to_year, to_month, to_day)
    mb.set_to_date(2016, 3, 28)
    mb.set_from_date(2016, 3, 28)
    mb.set_start_directory("/category/news/national")
    mb.start_archiving()
    # data_file.close()
    # article_data_file.close()
