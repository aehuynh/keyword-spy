from bs4 import BeautifulSoup
import re

def parse_google_text_ads(html):
    ads = []
    rank = 1
    soup = BeautifulSoup(html)
    
    for ad_li in soup.find_all('li', class_=re.compile("ads-ad")):
        ad = parse_google_text_ad(ad_li)
        # If the ad info was successfully found
        if ad is not None:
            ad['rank'] = rank
            rank += 1
            ads.append(ad)

    return ads

def parse_google_text_ad(ad_li):
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
    f = open("test_files/test.html", "r")
    ad_infos = parse_google_text_ads(f.read())
    
    for ad_info in ad_infos:
        for key,value in ad_info.items():
            print(str(key) + ": " + str(value))
        print("\n")