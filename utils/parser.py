from bs4 import BeautifulSoup
import re
from abc import ABCMeta, abstractmethod
import os
''' Thoughts
TODO: consider using LXML for speed boost since I only traverse through path with CSS selector
TODO: Figure out most efficient tool to scrape by path
TODO: Create between method and variable names
TODO: Add error checking 
3. Research ETL for python scraping
4. Should I use factory DP for parser/scraper/objects? 

5 Consider making all parse methods private except for parse()
'''
class SearchResultParser(metaclass=ABCMeta):
    def __init__(self, search_engine_name, file_name, html=None, soup=None):
        self.search_engine_name = "google"
        # File to get html from
        self.file_name = file_name

        # Declaring the lists
        self.text_ads = []
        self.shopping_ads = []
        self.search_results = []

        self.html = html
        self.soup = soup        

    def get_soup(self):
        ''' Get the beautiful soup instance. Creates one from self.html if 
            self.soup does not exist
        '''

        if self.soup is None:
            # Create new Beautiful soup instance out of fed html
            self.soup = BeautifulSoup(self.html)
        return self.soup

    def _parse_one(self, soup, css_selectors):
        ''' Parse one entry using css_selectors to figure out the
            proper css_selector and variable name
        '''

        results = {}
        for name, selectors in css_selectors.items():
            element = soup.select(selectors['css_selector'])
            if element and len(element) == 1:
                if selectors['target'] is "text":
                    # Get the "text" variable of the element
                    result = getattr(element[0], "text")
                elif selectors['target'] is "untag":
                    # Get all children of element as a single string
                    result = remove_outer_tag(element[0])
                else:
                    result = element[0][selectors['target']]

                results[name] = result
        
        
        if len(results) < 1:
            return None

        return results

    def _parse(self):
        rank = 1
        soup = self.get_soup()
        selectors = self.css_selectors
        for name, selector in self.css_selectors.items():
            results = []
            if name is "text_ads":
                # Navigate to the tag that represents one object
                for start_tag in soup.select(selector['start_tag']):
                    result = self._parse_one(start_tag, selector['elements'])
                    if result is not None:
                        result['rank'] = rank
                        rank += 1

                        results.append(result)

                setattr(self, name, results)

                    

    def parse(self, html=None):
        if html:
            self.html = html
        if self.html is None:
            self.get_html_from_file()
      
        self._parse()


    # Used for testing
    def get_html_from_file(self):
        f = open(self.file_name, "r")
        self.html = f.read()

class GoogleParser(SearchResultParser):
    css_selectors = {
        'search_results': {
            'start_tag' : 'li[class="g"]',
            'elements': {
                'title' : {
                    'target': 'text',
                    'css_selector': 'div.rc > h3.r > a'
                },
                'link' : {
                    'target': 'href',
                    'css_selector': 'div.rc > h3.r > a'
                },
                'visible_url' : {
                    'target': 'text',
                    'css_selector': 'div.rc > div.s > div > div.f.kv._SWb > cite._Rm'
                },
                'creative' : {
                    'target': 'text',
                    'css_selector': 'div.rc > div.s > div > span.st'
                }
            }

        },
        'text_ads': {
            'start_tag' : 'li[class="ads-ad"]',
            'elements': {
                'title' : {
                    'target': 'text',
                    'css_selector': 'h3 > a:nth-of-type(2)'
                },
                'link' : {
                    'target': 'href',
                    'css_selector': 'h3 > a:nth-of-type(2)'
                },
                'visible_url' : {
                    'target': 'text',
                    'css_selector': 'div.ads-visurl > cite'
                },
                'creative' : {
                    'target': 'text',
                    'css_selector': 'div.ads-creative'
                }
            }
        }
    }

    def __init__(self, **kwargs):
        kwargs['search_engine_name'] = 'google'
        kwargs['file_name'] = 'test_files/google.html'

        super().__init__(**kwargs)

    

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
                text_ad['creative'] = creative.text
            # Get the green url
            visible_url = caption.find('div', class_='b_attribution')
            if visible_url is not None:
                text_ad['visible_url'] = visible_url.cite.text
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
    
    for text_ad in google.text_ads:
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
