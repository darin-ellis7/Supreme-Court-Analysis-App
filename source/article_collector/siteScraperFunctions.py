#File that contains functions to scrape articles from supreme court sections of prominent news website

#The below are used to download pages and sign GET requests for HTTPS
import urllib.request
import certifi

#Used to scrape HTML pages. Useful in functions
from bs4 import BeautifulSoup

#Grabs the html of the webpage and returns a BeautifulSoup Object for scraping tags
def grabPage(url):
    page = urllib.request.urlopen(url, cafile=certifi.where())
    try:
        soup = BeautifulSoup(page, 'html.parser')
        return soup
    #Sometimes will get 404 from HTTPs pages
    except Exception as e:
        print("Could not retrieve: " + url)
        return "<html></html>"

#Calls all scraper functions and adds to ongoing list. Returns list
def scrapeAll():
    urls = scrapeCNN()
    urls += scrapeNYT()
    urls +=scrapeWaPo()
    urls +=scrapeFoxNews()
    urls +=scrapeEconomist()
    urls +=scrapeChiTrib()
    urls +=scrapeReuters()
    urls +=scrapePolitico()
    urls +=scrapeNPR()
    urls +=scrapeMSNBC()
    urls +=scrapeWSJ()
    urls +=scrapeSlate()
    urls +=scrapeNYPost()
    return urls

#Scrapes CNN's supreme court section. Logic to scrape is correct as of 04/08/2018
#Returns lists of urls of articles
def scrapeCNN():
    #link of CNN supreme court page
    supreme_court_link = 'https://www.cnn.com/specials/politics/supreme-court-nine'
    #downloads page in soup format
    soup = grabPage(supreme_court_link)
    #each scraper function is different because of the differing formats. For cnn, any tags "article" contain links to articles
    articles = soup.find_all('article')
    urls = []
    #For loop extracts links from the article tag and descendants
    for article in articles:
        headline = article.find('h3', attrs={'class': 'cd__headline'})
        link = headline.find('a')
        path = link.get('href')
        #Ignores videos and profiles of reporters
        if not path.startswith('/profiles') and not path.startswith('/videos'):
            urls.append("https://www.cnn.com" + path)
    return urls

#Scrapes New York Times and returns list of urls
def scrapeNYT():
    urls = []
    supreme_court_link = 'https://www.nytimes.com/topic/organization/us-supreme-court'
    soup = grabPage(supreme_court_link)
    articles = soup.find('ol', {'class' : 'story-menu'})
    links = articles.find_all('a', {'class' : 'story-link'})
    # For loop extracts links from the list tag and descendants
    for link in links:
        urls.append(link.get('href'))
    return urls

#Scrapes Washington Post and returns list of urls
def scrapeWaPo():
    urls = []
    supreme_court_link = 'https://www.washingtonpost.com/politics/courts-law/'
    soup = grabPage(supreme_court_link)
    articles = soup.find_all('div', {'class' : 'story-headline'})
    # For loop extracts links from the div tag and descendants
    for article in articles:
        headline = article.find('h3')
        link = headline.find('a')
        path = link.get('href')
        urls.append(path)
    return urls

#Scrapes Fox News and returns list of urls
def scrapeFoxNews():
    urls = []
    supreme_court_link = 'http://www.foxnews.com/category/politics/judiciary/supreme-court.html'
    soup = grabPage(supreme_court_link)
    articles = soup.find_all('header', {'class' : 'info-header'})
    # For loop extracts links from the article header tag and descendants
    for article in articles:
        if article.find('span', {'class' : 'is-article'}):
            title = article.find('h2', {'class' : 'title'})
            path = title.find('a').get('href')
            urls.append("http://www.foxnews.com" + path)
    return urls

#Scrapes Economist and returns list of urls
def scrapeEconomist():
    urls = []
    supreme_court_link = 'https://www.economist.com/topics/us-supreme-court-1'
    soup = grabPage(supreme_court_link)
    articles = soup.find_all('p', {'class': 'topic-item-title'})
    # For loop extracts links from the p tag and descendants
    for article in articles:
        urls.append("https://economist.com" + article.find('a').get('href'))
    return urls

#Scrapes Chicago Tribune and returns list of urls
def scrapeChiTrib():
    urls = []
    supreme_court_link = 'http://www.chicagotribune.com/topic/crime-law-justice/justice-system/u.s.-supreme-court-ORGOV0000126-topic.html?target=stories'
    soup = grabPage(supreme_court_link)
    articles = soup.find_all('div', {'class': 'trb_search_result'})
    # For loop extracts links from the tag and descendants
    for article in articles:
        if article.find('a', {'class' : 'trb_search_result_figure'}):
            urls.append("http://www.chicagotribune.com" + article.find('a', {'class' : 'trb_search_result_figure'}).get('href'))
    return urls

#Scrapes Reuters and returns list of urls
def scrapeReuters():
    urls = []
    supreme_court_link = 'https://www.reuters.com/subjects/supreme-court'
    soup = grabPage(supreme_court_link)
    articles = soup.find_all('h2', {'class': 'headline_ZR_Fh'})
    # For loop extracts links from the tag and descendants
    for article in articles:
        if article.find('a'):
            urls.append(article.find('a').get('href'))
    return urls

#Scrapes Politico and returns list of urls
def scrapePolitico():
    urls = []
    supreme_court_link = 'https://www.politico.com/news/supreme-court'
    soup = grabPage(supreme_court_link)

    articles = soup.find_all('article', {'class': 'story-frag'})
    # For loop extracts links from the article tag and descendants
    for article in articles:
        header = article.find('header')
        cat = header.find('p', {'class' : 'category'})
        if cat:
            if cat.find('a').text != 'CARTOON CAROUSEL':
                urls.append(header.find('h3').find('a').get('href'))
        else:
            urls.append(header.find('h3').find('a').get('href'))
    return urls

#Scrapes NPR and returns list of urls
def scrapeNPR():
    urls = []
    supreme_court_link = 'https://www.npr.org/tags/125938785/supreme-court'
    soup = grabPage(supreme_court_link)
    articles = soup.find_all('article', {'class': 'item'})
    # For loop extracts links from the article tag and descendants
    for article in articles:
        header = article.find('h2', {'class': 'title'})
        urls.append(header.find('a').get('href'))
    return urls

#Scrapes MSNBC and returns list of urls
def scrapeMSNBC():
    urls = []
    supreme_court_link = 'http://www.msnbc.com/topics/supreme-court'
    soup = grabPage(supreme_court_link)
    articles = soup.find_all('article', {'class': 'article'})
    # For loop extracts links from the article tag and descendants
    for article in articles:
        header = article.find('h2', {'class': 'teaser__title'})
        if header:
            urls.append("http://www.msnbc.com/" + header.find('a').get('href'))
    return urls

#Scrapes Wall Street Journal and returns list of urls
def scrapeWSJ():
    urls = []
    supreme_court_link = 'https://blogs.wsj.com/law/category/supreme-court/'
    soup = grabPage(supreme_court_link)
    articles = soup.find_all('div', {'class': 'copy'})
    # For loop extracts links from the article tag and descendants
    for article in articles:
        header = article.find('h4', {'class' : 'headline'})
        if header:
            urls.append(header.find('a').get('href'))
    return urls

#Scrapes slate and returns list of urls
def scrapeSlate():
    urls = []
    supreme_court_link = 'http://www.slate.com/articles/news_and_politics/supreme_court_dispatches.html'
    soup = grabPage(supreme_court_link)
    # Gets large headline article
    largeArticle = soup.find('section', {'class': 'full-width'})
    if largeArticle:
        urls.append(largeArticle.find('a').get('href'))
    articles = soup.find_all('div', {'class': 'tile'})
    # For loop extracts links from the tags and descendants
    for article in articles:
        link = article.find('a')
        if link:
            urls.append(link.get('href'))
    return urls

#scrapes NYPost page and returns list of urls
def scrapeNYPost():
    urls = []
    supreme_court_link = 'https://nypost.com/tag/supreme-court/'
    soup = grabPage(supreme_court_link)
    articles = soup.find_all('article', {'class': 'tag-supreme-court'})
    # For loop extracts links from the tags and descendants
    for article in articles:
        link = article.find('h3')
        if link:
            urls.append(link.find('a').get('href'))
    return urls

#Scrapes Huffington post section and returns list of urls
def scrapeHuffPo():
    urls = []
    supreme_court_link = 'https://www.huffingtonpost.com/topic/supreme-court'
    soup = grabPage(supreme_court_link)
    zone = soup.find('div', {'class' : 'zone__content'})
    articles = zone.find_all('div', {'class': 'card__headline'})
    # For loop extracts links from the tags and descendants
    for article in articles:
        link = article.find('a')
        if link:
            urls.append('http://www.huffingtonpost.com' + link.get('href'))
    return urls


