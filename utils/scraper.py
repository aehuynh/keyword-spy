from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from user_agents import DEFAULT_USER_AGENT
import time
import sys
from abc import ABCMeta, abstractmethod

# TODO: Refactor page loading waits with explicit/implicit waits
# TODO: consider abstracting scraper further to cover non-selenium scraping
# Consider adding threading
# TODO: Add proxy support
# TODO: create error/exception checking

class SearchScraper(metaclass=ABCMeta):
    def __init__(self, search_engine_name, search_page_url, page_source_file_name, search_input_name, should_encode=False, 
                 driver_wait=10, use_proxies=False):
        self.search_engine_name = search_engine_name
        # Name of the search input box
        self.search_input_name = search_input_name
        # Url of the search page
        self.search_page_url = search_page_url
        # Whether to ascii encode the page source because of encoding bug
        self.should_encode = should_encode

        self.page_source_file_name = page_source_file_name

        # Default max wait time for driver
        self.driver_wait = driver_wait

        # Whether to use proxies
        self.use_proxies = use_proxies


    def start_driver(self, user_agent=DEFAULT_USER_AGENT):
        # Create Selenium driver with PhantomJS and a custom user agent
        dc = {"phantomjs.page.settings.userAgent" : user_agent}
        driver = webdriver.PhantomJS(desired_capabilities=dc)
        self.driver = driver

    # Sleep to wait for search start page to load
    def wait(self, locator):
        WebDriverWait(self.driver, self.driver_wait).until(
            EC.visibility_of_element_located((locator)))

    # Enter the search term and hit enter
    def perform_search(self, search_term):
        # Find input text box
        elem = self.driver.find_element_by_name(self.search_input_name)

        elem.send_keys(search_term)
        elem.send_keys(Keys.RETURN)

    # Open the starting search page
    def load_search_page(self):
       self.driver.get(self.search_page_url)

    # Grab the page source of the page that the driver is pointed at right nwo
    def grab_page_source(self):
        self.result_source = self.driver.page_source
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
        self.wait_until_input_field_loads()
        self.perform_search(search_term)
        self.wait_until_result_page_loads()
        self.grab_page_source()
        self.write_file()

    # Encode result_source with ascii
    def ascii_encode(self):
        if self.result_source:
            self.result_source = self.result_source.encode("ascii", "ignore")
    
    @abstractmethod
    def wait_until_input_field_loads(self):
        """Wait until the input field for the search query loads. It is an 
        abstract method because each search engine has a specific element 
        to wait for.
        """

    @abstractmethod
    def wait_until_result_page_loads(self):
        """Wait until the result page loads. It is an abstract method because
        each search engine has a specific element to wait for.
        """

class GoogleScraper(SearchScraper):
    def __init__(self, **kwargs):
        kwargs['search_engine_name'] = 'google'
        kwargs['page_source_file_name'] = 'test_files/google.html'
        kwargs['search_page_url'] = "https://www.google.com/"
        kwargs['search_input_name'] = "q"
        kwargs['should_encode'] = True

        super().__init__(**kwargs)

    def wait_until_input_field_loads(self):
        self.wait((By.NAME,self.search_input_name))
            
    def wait_until_result_page_loads(self):
        self.wait((By.ID, "resultStats"))


class BingScraper(SearchScraper):
    def __init__(self, **kwargs):
        kwargs['search_engine_name'] = 'bing'
        kwargs['page_source_file_name'] = 'test_files/bing.html'
        kwargs['search_page_url'] = "http://www.bing.com"
        kwargs['search_input_name'] = "q"
        kwargs['should_encode'] = True
        
        super().__init__(**kwargs)

    def wait_until_input_field_loads(self):
        """Wait until the an element with name ='q' is visible"""

        try:
            self.wait((By.NAME,self.search_input_name))
        except TimeoutException:
            pass
           
    def wait_until_result_page_loads(self):
        try:
            # TODO: FIgure out which element to wait fo
            time.sleep(6)
        except TimeoutException:
            pass
        

class YahooScraper(SearchScraper):
    def __init__(self, **kwargs):
        kwargs['search_engine_name'] = 'yahoo'
        kwargs['page_source_file_name'] = 'test_files/yahoo.html'
        kwargs['search_page_url'] = "https://www.yahoo.com/"
        kwargs['search_input_name'] = "p"
        kwargs['should_encode'] = True
        
        super().__init__(**kwargs)

    def wait_until_input_field_loads(self):
        """Wait until an element with name ='p' is visible"""
        try:
            self.wait((By.NAME,self.search_input_name))
        except TimeoutException:
            pass

    def wait_until_result_page_loads(self):
        
        try:
            # TODO: FIgure out which element to wait for
            time.sleep(6)
        except TimeoutException:
            pass

if __name__ == "__main__":
    search_term = sys.argv[1]
    yahoo = YahooScraper()
    bing = BingScraper()
    google = GoogleScraper()
    yahoo.search(search_term)
    bing.search(search_term)
    google.search(search_term)
