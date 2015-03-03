from bs4 import BeautifulSoup
import re
from abc import ABCMeta, abstractmethod

''' Thoughts
TODO: serious refactoring of BeautifulSoup html parsing 
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
        kwargs['file_name'] = 'test_files/google.html'

        super().__init__(**kwargs)

    def parse_shopping_ads(self):
        pass

    def parse_search_results(self):
        pass    

    def parse_text_ads(self):
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
        text_ad = {}
        # Grab the url displayed on the ad
        visible_url = ad_li.find('div', class_='ads-visurl')
        if visible_url is not None:
            text_ad['visible_url'] = remove_outer_tag(visible_url.cite)#remove_outer_tag(visible_url.contents)
        # Grab the ad creative
        creative = ad_li.find('div', class_=re.compile("ads-creative"))
        if creative is not None:
            text_ad['creative'] = creative.text
        # Grab the actual link and the title of the ad
        link = ad_li.find('a', class_=re.compile("^(?!display:none).*$"))
        if link is not None:
            text_ad['title'] = link.text
            text_ad['link'] = link['href']
        # if one of the info is missing
        if not all([visible_url, creative, link]):
            return None

        return text_ad

class BingParser(SearchResultParser):
    def __init__(self, **kwargs):
        kwargs['search_engine_name'] = 'bing'
        kwargs['file_name'] = 'test_files/bing.html'

        super().__init__(**kwargs)

    def parse_shopping_ads(self):
        pass

    def parse_search_results(self):
        pass    

    def parse_text_ads(self):
        rank = 1
        soup = BeautifulSoup(self.html)

        for ad_div in soup.find_all('div', class_="sb_add sb_adTA"):
            text_ad = self._parse_text_ad(ad_div)
            # If the ad info was successfully found
            if text_ad is not None:
                text_ad['rank'] = rank
                rank += 1
                self.text_ads.append(text_ad)

    def _parse_text_ad(self, ad_div):
        text_ad = {}

        # Navigate to the caption
        caption = ad_div.find('div', class_='b_caption')
        if caption is not None:
            # Get the text creative
            creative = caption.find('p', class_=None)
            if creative is not None:
                text_ad['creative'] = remove_outer_tag(creative)
            # Get the green url
            visible_url = caption.find('div', class_='b_attribution')
            if visible_url is not None:
                text_ad['visible_url'] = remove_outer_tag(visible_url.cite)
            # Get the greyed out secondary text
            secondary_text = caption.find('div', class_='b_secondaryText')
            if secondary_text is not None:
                text_ad['secondary_text'] = remove_outer_tag(secondary_text)

        # Grab title and the title link
        actual_link = ad_div.find('h2')
        if actual_link is not None:
            actual_link = actual_link.a
            text_ad['link'] = actual_link['href']
            text_ad['title'] = remove_outer_tag(actual_link)

        return text_ad





# Use this to remove outer tag until I figure out better way to
def remove_outer_tag(contents):
    return ''.join(map(str, contents))

if __name__ == "__main__":
    google = GoogleParser()
    google.parse()
    
    for text_ad in google.text_ads:
        for key,value in text_ad.items():
           pass#  print(str(key) + ": " + str(value))
        print("\n")

    bing = BingParser()
    bing.parse()
    
    for text_ad in bing.text_ads:
        for key,value in text_ad.items():
            print(str(key) + ": " + str(value))
        print("\n")

