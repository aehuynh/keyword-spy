# keyword-spy
A search engine result and ads scraper

### Table of Contents

1. [Description](#description)

2. [Scraping Method](#scraping-method)

3. [How It Parses HTML](#how-it-parses-html)

4. [Future Features](#future-features)

4. [Scaling Up](#scaling-up)

###  Description
Keyword Spy is a keyword analytics tool that scrapes search engine results and ads from popular 
search engine result pages(SERPs) like Google, Yahoo and Bing.

### Scraping Method
This project uses Selenium to grab the page source of SERPs. The main reason for using Selenium over the basic 
requests library is because it is able to load Javascript.

There are two advantages in using Selenium:

1. There might be Javascript that loads that checks whether or not the driver is human.
2. Some content is loaded through Javascript.

### How It Parses HTML
I am mainly using CSS selectors to parse the ads and search results. I use BeautifulSoup
instead of lxml because there might be content that is hard to parse from just a CSS selector. I might 
make the switch to lxml if I end up cleaning the hard to parse content instead of parsing it directly 
with a parsing library.

I use CSS selectors because it seems like the easiest way to parse content because the CSS path 
is already laid out nicely when using "Inspect Element". I am not sure about the performance of
using CSS selectors and will take a look at all the HTML parsing methods when scaling up.

### Future Features
Here's a list of possible future features:

1. Proxy support
2. Ability to scrape past first SERP page
3. SERP error page handling(captcha)
4. A database and models for scraped results and ads 
5. A scheduler that manages scraping on multiple VMs
6. Simple Django website that takes in keywords and shows analysis on the SERP pages scraped
7. Periodic snapshots of popular search results
8. Indexing of search results into a cache for quick access

For analysis, I want to take this tool in the NLP direction and provide analysis of ads 
that will give people who are not the best copywriters ideas on how to write their ad.
Ideally, the tool would be able to spin the scraped ads to create a new, unique ad out
of the old ad.

### Scaling Up
One of the first problems I will run into is that one IP can only make around one search every 2-4 minutes or
it will get flagged by the search engine. There are some ways to handle this:

1. Multiple VMs scraping
2. Many proxies

When scaling up, I will implement both of those features with a scheduling system that will assign
 VMs with proxies and keywords to scrape.
 
With a website, there can be many keyword requests per minute. To handle this, I will create snapshots of popular 
search results when the load is low, and show these snapshots to users instead of real time results. These snapshots
will expire after a certain time and a new snapshot will be taken.
