from bs4 import BeautifulSoup
import re
from abc import ABCMeta, abstractmethod

''' Thoughts
1. TODO: Create some sort of dictionary to show what is inside self.text_"ads,
2. Consider refactoring with a dictionary of target css elements and the variable name 
   to map the element to without explicitly calling BeautifulSoup.find every time
3. What layer do I need between the list of dictionaries and creating actual objects
   to store in the database?
4. Should I use factory DP for parser/scraper/objects? Is it pythonic?
5 Consider making all parse methods private except for parse()
'''
class SearchResultParser(metaclass=ABCMeta):
    def __init__(self, search_engine_name, file_name, html=None):
        self.search_engine_name = "google"
        # File to get html from
        self.file_name = file_name

        # Declaring the lists
        self.text_ads = []
        self.shopping_ads = []
        self.search_results = []

        self.html = html
        

    @abstractmethod
    def parse_text_ads(self, html):
        '''Parse text ads'''

    @abstractmethod
    def parse_search_results(self, html):
        '''Parse search results'''
    
    @abstractmethod
    def parse_shopping_ads(self, html):
        '''Parse shopping ads'''

    def parse(self, html=None):
        if html:
            self.html = html
        if self.html is None:
            self.get_html_from_file()

        self.parse_text_ads()
        self.parse_shopping_ads()
        self.parse_search_results()
        

    # Used for testing
    def get_html_from_file(self):
        f = open(self.file_name, "r")
        self.html = f.read()

class GoogleParser(SearchResultParser):
    def __init__(self, **kwargs):
        kwargs['search_engine_name'] = 'google'

        super().__init__(**kwargs)

    def parse_shopping_ads(self):
        pass

    def parse_search_results(self):
        pass    

    def parse_text_ads(self):
        # Consider removing exception when you learn more about Python errors
        if self.html is None:
            raise Exception("NO HTML!")

        rank = 1
        soup = BeautifulSoup(self.html)
        
        for ad_li in soup.find_all('li', class_=re.compile("ads-ad")):
            text_ad = self._parse_text_ad(ad_li)
            # If the ad info was successfully found
            if text_ad is not None:
                text_ad['rank'] = rank
                rank += 1
                self.text_ads.append(text_ad)

    def _parse_text_ad(self, ad_li):
        ad_info = {}
        # Grab the url displayed on the ad
        visible_url = ad_li.find('cite')
        if visible_url is not None:
            ad_info['visible_url'] = ''.join(map(str, visible_url.contents))
        # Grab the ad creative
        creative = ad_li.find('div', class_=re.compile("ads-creative"))
        if creative is not None:
            ad_info['creative'] = creative.text
        # Grab the actual link and the title of the ad
        link = ad_li.find('a', class_=re.compile("^(?!display:none).*$"))
        if link is not None:
            ad_info['title'] = link.text
            ad_info['link'] = link['href']
        # if one of the info is missing
        if not all([visible_url, creative, link]):
            return None

        return ad_info

if __name__ == "__main__":
    google = GoogleParser(file_name="test_files/google.html")
    google.parse()
    
    for text_ad in google.text_ads:
        for key,value in text_ad.items():
            print(str(key) + ": " + str(value))
        print("\n")