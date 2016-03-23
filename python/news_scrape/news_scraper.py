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
import requests
import urllib2
import datetime
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

        set_to_date(year, month, day)

        # Check if start directory was set
        # throw exception if not set
        if self._start_directory == None:
            raise "Required Start directory is not set"

        # Retrieve the starting page to scrape data from
        try:
            source = self._domain + self._start_directory
            initial_html = fetch_html_raw(source)
        except requests.exceptions.RequestException as e:
            print e
            return None

        # TODO: Continue implementing pseudo code
        news_post = []

        get_all_posts(initial_html, id, "post-[0-9]+")
        # TODO: Continue implementing pseudo code

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

    def get_all_posts(self, bs4_data, news_store,html_attribute, value):
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
            raise "No math found", html_attribute, value
        return posts_list

    def fetch_html_raw(self, url, num_retries=2):
        """
        Returns the raw html from the specified url
        Note: no 'http://' format checking in URL
        TODO: Add logging
        """
        html = ""
        try:
            response = requests.get(url)
        except requests.exceptions.RequestException as e:
            print "Error Occurred", e
            return None

        html = response.content
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

    def set_filter(self, filter_list):
        pass

if __name__ == "__main__":
    data_file = open("./data/mb_sample_data.txt", "r")
    mb = NewsArchiver("www.mb.com.ph")
    html = mb.fetch_html_raw(source)
    # html = requests.get(source)
    print html
