from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from user_agents import DEFAULT_USER_AGENT
import time
import random
import sys
from abc import ABCMeta, abstractmethod

# TODO: Refactor page loading waits with explicit/implicit waits
# TODO: consider abstracting scraper further to cover non-selenium scraping
# Consider adding threading
# TODO: Add proxy support
# TODO: create error/exception checking

class SearchScraper(metaclass=ABCMeta):
    def __init__(self, search_engine_name, search_page_url, page_source_file_name, search_input_name, should_encode=False, 
                 search_wait_lower=0, search_wait_upper=0, result_wait_lower=0, result_wait_upper=0, 
                 use_proxies=False):

        self.search_engine_name = search_engine_name
        # Name of the search input box
        self.search_input_name = search_input_name
        # Url of the search page
        self.search_page_url = search_page_url
        # Whether to ascii encode the page source because of encoding bug
        self.should_encode = should_encode

        self.page_source_file_name = page_source_file_name

        # Wait times
        self.search_wait_lower = search_wait_lower
        self.search_wait_upper = search_wait_upper
        self.result_wait_lower = result_wait_lower
        self.result_wait_upper = result_wait_upper

        # Whether to use proxies
        self.use_proxies = use_proxies


    def start_driver(self, user_agent=DEFAULT_USER_AGENT):
        # Create Selenium driver with PhantomJS and a custom user agent
        dc = {"phantomjs.page.settings.userAgent" : user_agent}
        driver = webdriver.PhantomJS(desired_capabilities=dc)
        self.driver = driver

    # Sleep to wait for search start page to load
    def pre_search_wait(self):
        self.random_sleep(self.search_wait_lower, self.search_wait_upper)

    # Enter the search term and hit enter
    def perform_search(self, search_term):
        # Find input text box
        elem = self.driver.find_element_by_name(self.search_input_name)

        elem.send_keys(search_term)
        elem.send_keys(Keys.RETURN)

    # Open the starting search page
    def load_search_page(self):
       self.driver.get(self.search_page_url)

    # Sleep while waiting for result page to load
    def result_wait(self):
        self.random_sleep(self.result_wait_lower, self.result_wait_upper)

    # Grab the page source of the page that the driver is pointed at right nwo
    def grab_page_source(self):
        self.result_source = self.driver.page_source#execute_script('return document.body.innerHTML;')
        # Encode with ascii to solve solve encoding issues
        if self.should_encode:
            self.ascii_encode()
    
    # Write page source into a file
    def write_file(self):
        if self.result_source:
            f = open(self.page_source_file_name, "w")
            f.write(str(self.result_source))
            f.close

    # Search for a search_term using Selenium
    def search(self, search_term):
        self.start_driver()
        self.load_search_page()
        self.pre_search_wait()
        self.perform_search(search_term)
        self.result_wait()
        self.grab_page_source()
        self.write_file()

    # Sleep for a random time bounded by a range
    def random_sleep(self, lower, upper):
        sleep_time = random.uniform(lower, upper)
        time.sleep(sleep_time)

    # Encode result_source with ascii
    def ascii_encode(self):
        if self.result_source:
            self.result_source = self.result_source.encode("ascii", "ignore")
    

class GoogleScraper(SearchScraper):
    def __init__(self, **kwargs):
        kwargs['search_engine_name'] = 'google'
        kwargs['page_source_file_name'] = 'test_files/google.html'
        kwargs['search_page_url'] = "https://www.google.com/"
        kwargs['search_input_name'] = "q"
        kwargs['should_encode'] = True

        super().__init__(**kwargs)


class BingScraper(SearchScraper):
    def __init__(self, **kwargs):
        kwargs['search_engine_name'] = 'bing'
        kwargs['page_source_file_name'] = 'test_files/bing.html'
        kwargs['search_page_url'] = "http://www.bing.com"
        kwargs['search_input_name'] = "q"
        kwargs['should_encode'] = True
        
        super().__init__(**kwargs)


class YahooScraper(SearchScraper):
    def __init__(self, **kwargs):
        kwargs['search_engine_name'] = 'yahoo'
        kwargs['page_source_file_name'] = 'test_files/yahoo.html'
        kwargs['search_page_url'] = "https://www.yahoo.com/"
        kwargs['search_input_name'] = "p"
      #  kwargs['should_encode'] = True
        
        super().__init__(**kwargs)


if __name__ == "__main__":
    search_term = sys.argv[1]
    yahoo = YahooScraper(search_wait_lower=1, search_wait_upper=2, result_wait_lower=5.5, result_wait_upper=10)
    bing = BingScraper(search_wait_lower=1, search_wait_upper=2, result_wait_lower=5.5, result_wait_upper=10)
    google = GoogleScraper(search_wait_lower=1, search_wait_upper=2, result_wait_lower=5.5, result_wait_upper=10)
    yahoo.search(search_term)
    bing.search(search_term)
    google.search(search_term)
