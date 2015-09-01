from bs4 import BeautifulSoup
import re
from abc import ABCMeta, abstractmethod
from models import dict_to_google_search_result, dict_to_google_search_ad
import datetime

class SearchResultParser(metaclass=ABCMeta):
    """Abstract bases class for search engine parsers. 

    The purpose of the parser classes is to parse the results
    page HTML. 

    This base class depends on CSS Selectors to parse the HTML pages. Although
    BeautifulSoup can do much more, parsing by CSS Selectors provides a 
    more modular approach to web parsing. 

    One problem of using only CSS Selectors is that some pages require 
    special text manipulation that CSS Selectors cannot accomplish. 
    The way this class deals with this problem is to grab more data 
    than necessary when in doubt and then clean the data.
    """

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
        """Get the BeautifulSoup instance of the html. Creates
        a new instance from self.html if self.soup does not exist.
        """

        if self.soup is None:
            # Create new Beautiful soup instance out of fed html
            self.soup = BeautifulSoup(self.html)
        return self.soup

    def parse(self, html=None):
        """Public method to start the html parsing. It initiates the
        pre-parsing setup. 
        """

        if html:
            self.html = html
        if self.html is None:
            self.get_html_from_file()
      
        self._parse()

    def _parse(self):
        """Private method that parses html using the search engine
        specific CSS Selectors.
        """

        soup = self.get_soup()
        selectors = self.css_selectors

        # Loop through each type of item to parse
        # ie. text_ads or search_results
        for item_name, element_selectors in self.css_selectors.items():
            rank = 1
            results = []
            
            # Navigate to the tag that represents one item
            for start_tag in soup.select(element_selectors['start_tag']):
                result = self._find_elements_with_selectors(start_tag, element_selectors['elements'])

                if result is not None:
                    result['rank'] = rank
                    rank += 1

                    results.append(result)

            # Set an instance variable representing all the items of the type
            # item_name 
            setattr(self, item_name, results)

    def _find_elements_with_selectors(self, soup, css_selectors):
        """Parse one entry using css_selectors to figure out the
        proper css_selector and variable name.
        """ 

        elements = {}
        for name, selectors in css_selectors.items():
            result = soup.select(selectors['css_selector'])
            if result and len(result) == 1:
                if selectors['target'] is "text":
                    # Get the "text" variable of the element
                    element = getattr(result[0], "text")
                elif selectors['target'] is "untag":
                    # Get everything inside of tag as a string
                    element = remove_outer_tag(result[0])
                else:
                    # Get the attribute selects['target'] 
                    element = result[0][selectors['target']]

                elements[name] = element
        
        if len(elements) < 1:
            return None

        return elements
   
    # Use this to remove outer tag until I figure out better way to
    def remove_outer_tag(contents):
        """Returns BeautifulSoup contents with its outer tag removed."""

        return ''.join(map(str, contents))

    # Used for testing
    def get_html_from_file(self):
        f = open(self.file_name, "r")
        self.html = f.read()



class GoogleParser(SearchResultParser):
    """Google search result html parser."""

    css_selectors = {
        'search_results': {
            'start_tag': 'ol#rso li[class="g"]',
            'elements': {
                'title': {
                    'target': 'text',
                    'css_selector': 'div.rc > h3.r > a'
                },
                'link': {
                    'target': 'href',
                    'css_selector': 'div.rc > h3.r > a'
                },
                'visible_url': {
                    'target': 'text',
                    'css_selector': 'div.rc > div.s > div > div.f.kv._SWb > cite._Rm'
                },
                'creative': {
                    'target': 'text',
                    'css_selector': 'div.rc > div.s > div > span.st'
                }
            }

        },
        'text_ads': {
            'start_tag': 'li[class="ads-ad"]',
            'elements': {
                'title': {
                    'target': 'text',
                    'css_selector': 'h3 > a:nth-of-type(2)'
                },
                'link': {
                    'target': 'href',
                    'css_selector': 'h3 > a:nth-of-type(2)'
                },
                'visible_url': {
                    'target': 'text',
                    'css_selector': 'div.ads-visurl > cite'
                },
                'creative': {
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
    """Bing search result html parser."""

    css_selectors = {
        'search_results': {
            'start_tag': 'ol#b_results > li[class="b_algo"]',
            'elements': {
                'title': { 
                    'target': 'text',
                    'css_selector': 'h2 > a:nth-of-type(1)' 
                },
                'link': {
                    'target': 'href',
                    'css_selector': 'h2 > a:nth-of-type(1)' 
                },
                'visible_url': {
                    'target': 'text',
                    'css_selector': 'div.b_caption > div.b_attribution'
                },
                'creative': {
                    'target': 'text',
                    'css_selector': 'div.b_caption > p:nth-of-type(1)'
                }
            }
        },
        'text_ads': {
            'start_tag': 'div.sb_add.sb_adTA',
            'elements': {
                'title': {
                    'target': 'text',
                    'css_selector': 'h2 > a:nth-of-type(1)'
                },
                'link': {
                    'target': 'href',
                    'css_selector': 'h2 > a:nth-of-type(1)'
                },
                'visible_url': {
                    'target': 'text',
                    'css_selector': 'div.b_caption > div.b_attribution > cite'
                },
                'secondary_text': {
                    'target': 'text',
                    'css_selector': 'div.b_caption > div.b_secondaryText'
                },
                'creative': {
                    'target': 'text',
                    'css_selector': 'div.ads-creative'
                }
            }
        }
    }

    def __init__(self, **kwargs):
        kwargs['search_engine_name'] = 'bing'
        kwargs['file_name'] = 'test_files/bing.html'

        super().__init__(**kwargs)
    

class YahooParser(SearchResultParser):
    """Yahoo search result html parser."""

    css_selectors = {
        'search_results': {
            'start_tag': 'ol.reg.searchCenterMiddle > li > div.dd.algo',
            'elements': {
                'title': { 
                    'target': 'text',
                    'css_selector': 'div.compTitle > h3.title > a:nth-of-type(1)' 
                },
                'link': {
                    'target': 'href',
                    'css_selector': 'div.compTitle > h3.title > a:nth-of-type(1)' 
                },
                'visible_url': {
                    'target': 'text',
                    'css_selector': 'div.compTitle > div > span'
                },
                'creative': {
                    'target': 'text',
                    'css_selector': 'div.compText.aAbs > p:nth-of-type(1)'
                }
            }
        },
        'text_ads': {
            'start_tag': 'li > div.dd > div[class="layoutMiddle"]',
            'elements': {
                'title': {
                    'target': 'text',
                    'css_selector': 'div.compTitle > h3.title > a:nth-of-type(1)'
                },
                'link': {
                    'target': 'href',
                    'css_selector': 'div.compTitle > h3.title > a:nth-of-type(1)'
                },
                'visible_url': {
                    'target': 'text',
                    'css_selector': 'div.compTitle >  div'
                },
                'creative': {
                    'target': 'text',
                    'css_selector': 'div.layoutCenter > div.compText > p:nth-of-type(1) > a'
                }
            }
        }
    }

    def __init__(self, **kwargs):
        kwargs['search_engine_name'] = 'yahoo'
        kwargs['file_name'] = 'test_files/yahoo.html'

        super().__init__(**kwargs)

    # TODO: Clean ad out of visible link in the end
    # TODO: Clean the duplicate ads from the bottom
    # TODO: Clean first search result showing in text_ads


# Testing 
if __name__ == "__main__":
    
    google = GoogleParser()
    google.parse()
    
    dict_to_google_search_ad("cars", datetime.datetime.now(), google.text_ads)
    dict_to_google_search_result("cars", datetime.datetime.now(), google.search_results)    
    '''
    for text_ad in google.text_ads:
        for key,value in text_ad.items():
            print(str(key) + ": " + str(value))
        print("\n")

    bing = BingParser()
    bing.parse()
    
    for fe in bing.search_results:
        for key,value in fe.items():
            print(str(key) + ": " + str(value))
        print("\n")
    
'''
