import urllib.request
import certifi
from bs4 import BeautifulSoup

def grabPage(url):
    page = urllib.request.urlopen(url, cafile=certifi.where())
    return BeautifulSoup(page, 'html.parser')


#Scrapes CNN's supreme court section. Logic to scrape is correct as of 03/19/2018
#Returns lists of urls of articles
def scrapeCNN():
    supreme_court_link = 'https://www.cnn.com/specials/politics/supreme-court-nine'
    soup = grabPage(supreme_court_link)
    articles = soup.find_all('article')
    urls = []
    for article in articles:
        headline = article.find('h3', attrs={'class': 'cd__headline'})
        link = headline.find('a')
        path = link.get('href')
        if not path.startswith('/profiles') and not path.startswith('/videos'):
            urls.append("https://www.cnn.com" + path)
    return urls


def scrapeNYT():
    urls = []
    supreme_court_link = 'https://www.nytimes.com/topic/organization/us-supreme-court'
    soup = grabPage(supreme_court_link)
    articles = soup.find('ol', {'class' : 'story-menu'})
    links = articles.find_all('a', {'class' : 'story-link'})
    for link in links:
        urls.append(link.get('href'))
    return urls

def scrapeWaPo():
    urls = []
    supreme_court_link = 'https://www.washingtonpost.com/politics/courts-law/'
    soup = grabPage(supreme_court_link)
    articles = soup.find_all('div', {'class' : 'story-headline'})
    for article in articles:
        headline = article.find('h3')
        link = headline.find('a')
        path = link.get('href')
        urls.append(path)
    return urls

def scrapeFoxNews():
    urls = []
    supreme_court_link = 'http://www.foxnews.com/category/politics/judiciary/supreme-court.html'
    soup = grabPage(supreme_court_link)
    articles = soup.find_all('header', {'class' : 'info-header'})
    for article in articles:
        if article.find('span', {'class' : 'is-article'}):
            title = article.find('h2', {'class' : 'title'})
            path = title.find('a').get('href')
            urls.append("http://www.foxnews.com" + path)
    return urls

def scrapeEconomist():
    urls = []
    supreme_court_link = 'https://www.economist.com/topics/us-supreme-court-1'
    soup = grabPage(supreme_court_link)
    articles = soup.find_all('p', {'class': 'topic-item-title'})

    for article in articles:
        urls.append("https://economist.com" + article.find('a').get('href'))
    return urls

def scrapeChiTrib():
    urls = []
    supreme_court_link = 'http://www.chicagotribune.com/topic/crime-law-justice/justice-system/u.s.-supreme-court-ORGOV0000126-topic.html?target=stories'
    soup = grabPage(supreme_court_link)
    articles = soup.find_all('div', {'class': 'trb_search_result'})
    for article in articles:
        if article.find('a', {'class' : 'trb_search_result_figure'}):
            urls.append("http://www.chicagotribune.com" + article.find('a', {'class' : 'trb_search_result_figure'}).get('href'))
    return urls

def scrapeReuters():
    urls = []
    supreme_court_link = 'https://www.reuters.com/subjects/supreme-court'
    soup = grabPage(supreme_court_link)
    articles = soup.find_all('h2', {'class': 'headline_ZR_Fh'})
    for article in articles:
        if article.find('a'):
            urls.append(article.find('a').get('href'))
    return urls

def scrapePolitico():
    urls = []
    supreme_court_link = 'https://www.politico.com/news/supreme-court'
    soup = grabPage(supreme_court_link)
    articles = soup.find_all('article', {'class': 'story-frag'})
    for article in articles:
        header = article.find('header')
        cat = header.find('p', {'class' : 'category'})
        if cat:
            if cat.find('a').text != 'CARTOON CAROUSEL':
                urls.append(header.find('h3').find('a').get('href'))
        else:
            urls.append(header.find('h3').find('a').get('href'))
    return urls

def scrapeNPR():
    urls = []
    supreme_court_link = 'https://www.npr.org/tags/125938785/supreme-court'
    soup = grabPage(supreme_court_link)
    articles = soup.find_all('article', {'class': 'item'})
    for article in articles:
        header = article.find('h2', {'class': 'title'})
        urls.append(header.find('a').get('href'))
    return urls

def scrapeMSNBC():
    urls = []
    supreme_court_link = 'http://www.msnbc.com/topics/supreme-court'
    soup = grabPage(supreme_court_link)
    articles = soup.find_all('article', {'class': 'article'})
    for article in articles:
        header = article.find('h2', {'class': 'teaser__title'})
        if header:
            urls.append("http://www.msnbc.com/" + header.find('a').get('href'))
    return urls

def scrapeWSJ():
    urls = []
    supreme_court_link = 'https://blogs.wsj.com/law/category/supreme-court/'
    soup = grabPage(supreme_court_link)
    articles = soup.find_all('div', {'class': 'copy'})
    for article in articles:
        header = article.find('h4', {'class' : 'headline'})
        if header:
            urls.append(header.find('a').get('href'))
    return urls

def scrapeSlate():
    urls = []
    supreme_court_link = 'http://www.slate.com/articles/news_and_politics/supreme_court_dispatches.html'
    soup = grabPage(supreme_court_link)
    article = soup.find('section', {'class': 'full-width'})
    if article:
        urls.append(article.find('a').get('href'))
    articles = soup.find_all('div', {'class': 'tile'})
    for art in articles:
        link = art.find('a')
        if link:
            urls.append(link.get('href'))
    return urls

def scrapeNYPost():
    urls = []
    supreme_court_link = 'https://nypost.com/tag/supreme-court/'
    soup = grabPage(supreme_court_link)
    articles = soup.find_all('article', {'class': 'tag-supreme-court'})
    for art in articles:
        link = art.find('h3')
        if link:
            urls.append(link.find('a').get('href'))
    return urls

def scrapeHuffPo():
    urls = []
    supreme_court_link = 'https://www.huffingtonpost.com/topic/supreme-court'
    soup = grabPage(supreme_court_link)
    zone = soup.find('div', {'class' : 'zone__content'})
    articles = zone.find_all('div', {'class': 'card__headline'})
    for art in articles:
        link = art.find('a')
        if link:
            urls.append('https://www.huffingtonpost.com' + link.get('href'))
    return urls


