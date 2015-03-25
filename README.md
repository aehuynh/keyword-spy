# keyword-spy
A search engine result and ads scraper

### Table of Contents

1. [Description](#description)

2. [Scraping Method](#scraping-method)

3. [How It Parses HTML](#html-parsing)

4. [Future Features](#features)

5. [Scaling Up](#scaling)

<a name="description" \>
###  Description
Keyword Spy is a keyword analytics tool that scrapes search engine results and ads from popular 
search engine result pages(SERPs) like Google, Yahoo and Bing.

<a name="scraping-method" \>
### Scaping Method
This project uses Selenium to grab the page source of SERPs. The main reason for using Selenium over the basic 
requests library is because it is able to load Javascript.

There are two advantages in using Selenium:

1. There might be Javascript that loads that checks whether or not the driver is human.
2. Some content is loaded through Javascript.

<a name="html-parsing" \>
### How It Parses HTML
I am mainly using CSS selectors parse the ads and search results. I am currently using BeautifulSoup
instead of LXML because there might be content that is hard to parse from just a CSS selector. I might 
make the switch to LXML if I end up only using CSS selectors and cleaning the hard to parse content.

I used CSS selectors because it seems like the easiest way to parse content because the CSS path 
is already laid out nicely when using "Inspect Element". I am not sure about the performance of
using CSS selectors and will take a look at all the HTML parsing methods when scaling up.

<a name="features">
### Future Features
Here's a list of features I plan to implement:

1. Proxy support
2. Ability to scrape past first SERP page
3. SERP error page handling(captcha)
4. A database and models for all scraped results
5. A scheduler that manages scraping on many, different VMs
6. Simple Django website that takes in keywords and shows analysis on the SERP pages scraped
7. Periodic snapshots of popular search results
8. Indexing of search results into a cache for quick access

For analysis, I want to take this tool in the NLP direction and provide analysis of ads 
that will give people who are not the best copywriters ideas on how to write their ad.
Ideally, the tool would be able to spin the scraped ads to create a new, unique ad out
of the old ad.

<a name="scaling">
### Scaling Up
One of the first problems I will run into is that I can only make around one search every 2-4 minutes or
I will get flagged by the search engine. There are some ways to handle this:

1. Multiple VMs scraping
2. Many proxies

When scaling up, I will implement both of those features with a scheduling system that will assign
 VMs with proxies and keywords to scrape.
