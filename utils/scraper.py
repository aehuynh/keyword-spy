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


class SearchScraper(metaclass=ABCMeta):
    """Abstract base class of search engine result page scrapers.

    It uses Selenium to simulate real user actions to not get flagged 
    by search engines and because some content is loaded through JavaScript.

    Basic HTTP library support will be provided later on when error checking
    evolves to handle captchas and bad pages and proxies are implemented.
    """

    def __init__(self, search_engine_name, search_page_url, page_source_file_name, search_input_name, should_ascii_encode=False, 
                 driver_wait=10, use_proxies=False):
        self.search_engine_name = search_engine_name
        # Name of the search input box
        self.search_input_name = search_input_name
        # Url of the search page
        self.search_page_url = search_page_url
        # Whether to ascii encode the page source because of encoding bug
        self.should_ascii_encode = should_ascii_encode
        # Name of the file to save source to
        self.page_source_file_name = page_source_file_name
        # Default max wait time for driver
        self.driver_wait = driver_wait
        # Whether to use proxies
        self.use_proxies = use_proxies


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

    def search(self, search_term):
        """Public method to perform all the actions to search for a search
        term and save the result page source.
        """

        self.start_driver()
        self.load_search_page()
        self.wait_until_input_field_loads()
        self.perform_search(search_term)
        self.wait_until_result_page_loads()
        self.grab_page_source()
        self.write_file()

    def start_driver(self, user_agent=DEFAULT_USER_AGENT):
        """Create Selenium driver with PhantomJS and a custom user agent

        Sets self.driver with the created web driver
        """
        
        dc = {"phantomjs.page.settings.userAgent" : user_agent}
        driver = webdriver.PhantomJS(desired_capabilities=dc)
        self.driver = driver

    def load_search_page(self):
        """Sends GET request to the starting search page"""

        self.driver.get(self.search_page_url)

    def perform_search(self, search_term):
        """Simulates entering search_term and Enter into input field"""

        # Locate the element
        element = self.driver.find_element_by_name(self.search_input_name)
        # Send input to the element
        element.send_keys(search_term)
        element.send_keys(Keys.RETURN)

    def grab_page_source(self):
        """Grab the page source of the page that the driver is 
        pointed at right now.
        """

        self.result_source = self.driver.page_source
        # Encode with ascii to solve encoding issues
        if self.should_ascii_encode:
            self.ascii_encode()
    
    def write_file(self):
        """Write page source of result into a file. Used for testing."""

        if self.result_source:
            f = open(self.page_source_file_name, "w")
            f.write(str(self.result_source))
            f.close

    def wait(self, locator):
        """Wait for an element that matches locator to load.  """
        
        WebDriverWait(self.driver, self.driver_wait).until(
            EC.visibility_of_element_located((locator)))

    def ascii_encode(self):
        """Encode self.result_source with ASCII to resolve encoding issues."""

        if self.result_source:
            self.result_source = self.result_source.encode("ascii", "ignore")


class GoogleScraper(SearchScraper):
    """A Google search result scraper"""

    def __init__(self, **kwargs):
        kwargs['search_engine_name'] = 'google'
        kwargs['page_source_file_name'] = 'test_files/google.html'
        kwargs['search_page_url'] = "https://www.google.com/"
        kwargs['search_input_name'] = "q"
        kwargs['should_ascii_encode'] = True

        super().__init__(**kwargs)

    def wait_until_input_field_loads(self):
        self.wait((By.NAME,self.search_input_name))
            
    def wait_until_result_page_loads(self):
        self.wait((By.ID, "resultStats"))


class BingScraper(SearchScraper):
    """A Bing search result scraper"""

    def __init__(self, **kwargs):
        kwargs['search_engine_name'] = 'bing'
        kwargs['page_source_file_name'] = 'test_files/bing.html'
        kwargs['search_page_url'] = "http://www.bing.com"
        kwargs['search_input_name'] = "q"
        kwargs['should_ascii_encode'] = True
        
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
    """A Yahoo search result scraper"""

    def __init__(self, **kwargs):
        kwargs['search_engine_name'] = 'yahoo'
        kwargs['page_source_file_name'] = 'test_files/yahoo.html'
        kwargs['search_page_url'] = "https://www.yahoo.com/"
        kwargs['search_input_name'] = "p"
        kwargs['should_ascii_encode'] = True
        
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
