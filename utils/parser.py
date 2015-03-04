from bs4 import BeautifulSoup
import re
from abc import ABCMeta, abstractmethod
import os
''' Thoughts
TODO: serious refactoring of BeautifulSoup html parsing, consider using LXML for speed boost
        My process is to find the "base" tag of what I want and then navigate through the tree 
        by tags without any further pattern matching. TODO: Figure out best library for my scraping process
2. Consider refactoring with a dictionary of target css elements and the variable name 
   to map the element to without explicitly calling BeautifulSoup.find every time
3. What layer do I need between the list of dictionaries and creating actual objects
   to store in the database?
4. Should I use factory DP for parser/scraper/objects? 
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

    def create_soup(self):
        return BeautifulSoup(self.html)

    def parse(self, html=None):
        if html:
            self.html = html
        if self.html is None:
            self.get_html_from_file()

      #  self.parse_text_ads()
      #  self.parse_shopping_ads()
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
        # rank: The position of the search result on the page
        rank = 1
        soup = self.create_soup()

        ''' <ol> with class ="rso" surrounds the list of search results.
            Each li with class "g" represents one search result 
        '''                                     
         
        # <li class="g"> is the start of a single search result
        for search_li in soup.select('li[class="g"]'):
            print("s")
            # Parse each search result individually
            search_result = self._parse_search_result(search_li)
            
            if search_result is not None:
                search_result['rank'] = rank
                rank += 1
                self.search_results.append(search_result)


    def _parse_search_result(self, search_li):
        search_result = {}

        # Grab title link
        title_link = search_li.select('div.rc > h3.r > a')
        if title_link is not None and len(title_link)==1:
            search_result['title'] = title_link[0].text
            search_result['link'] = title_link[0]['href']
        
        # Grab the green url
        visible_url = search_li.select('div.rc > div.s > div > div.f.kv._SWb > cite._Rm')
        if visible_url is not None and len(visible_url)==1:
            search_result['visible_url'] = remove_outer_tag(visible_url[0])

        # Grab the ad creative
        # Clean the creative date later on
        creative = search_li.select('div.rc > div.s > div > span.st')
        if creative is not None and len(creative)==1:
            search_result['creative'] = remove_outer_tag(creative[0])
      
        # if one of the info is missing
        if not(visible_url or creative or title_link):
            return None

        return search_result


    def parse_text_ads(self):
        # rank: The position of the ad on the page
        rank = 1
        soup = self.create_soup()
        ''' li elements with class "ads-ad" represent one text ad
        '''
        for ad_li in soup.find_all('li', class_=re.compile("ads-ad")):
            # Parse each text ad individually
            text_ad = self._parse_text_ad(ad_li)
            
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
        title_link = ad_li.find('a', class_=re.compile("^(?!display:none).*$"))
        if title_link is not None:
            text_ad['title'] = title_link.text
            text_ad['link'] = title_link['href']
        # if one of the info is missing
        if not all([visible_url, creative, title_link]):
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
        # rank: The position of the ad on the page
        rank = 1
        soup = self.create_soup()

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
        title_link = ad_div.find('h2')
        if title_link is not None:
            title_link = title_link.a
            text_ad['link'] = title_link['href']
            text_ad['title'] = remove_outer_tag(title_link)

        return text_ad





# Use this to remove outer tag until I figure out better way to
def remove_outer_tag(contents):
    return ''.join(map(str, contents))

def traverse_path(soup, path):
    for tag in path:
        soup = soup.tag
        if soup is None:
            return None

if __name__ == "__main__":
    google = GoogleParser()
    google.parse()
    
    for text_ad in google.search_results:
        for key,value in text_ad.items():
            print(str(key) + ": " + str(value))
        print("\n")

   # bing = BingParser()
  #  bing.parse()
    
   # for text_ad in bing.text_ads:
  #      for key,value in text_ad.items():
  #          print(str(key) + ": " + str(value))
 #       print("\n")
#
