from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from user_agents import DEFAULT_USER_AGENT
import time
import random
import sys

# TODO: Refactor page loading waits with explicit/implicit waits

def start_driver():
    # Create Selenium driver with PhantomJS and a custom user agent
    dc = {"phantomjs.page.settings.userAgent" : DEFAULT_USER_AGENT}
    driver = webdriver.PhantomJS(desired_capabilities=dc)
    return driver

def search_google(driver, search_term):
    # Open search page and wait for page to load
    driver.get("https://www.google.com/")
    random_sleep(1.5, 2.5)
    # Enter search term
    elem = driver.find_element_by_name("q")
    elem.send_keys(search_term)
    elem.send_keys(Keys.RETURN)
    
def get_search_source(search_term):
    driver = start_driver()

    search_google(driver,search_term)
    # Wait for page to load after the search has been made
    random_sleep(5.5, 10)
    # Grab body of the page source
    source = driver.execute_script('return document.body.innerHTML;')
    # Encode with ascii to solve solve encoding issues
    source = source.encode("ascii", "ignore")
    
    driver.quit()
    write_file("test_files/test.html", source)

# Sleep for a random time bounded by a range
def random_sleep(lower, upper):
    sleep_time = random.uniform(lower, upper)
    time.sleep(sleep_time)
    
def write_file(file, text):
    f = open(file, "w")
    f.write(str(text))
    f.close

if __name__ == "__main__":
    get_search_source(sys.argv[1])
# Use explicit wait