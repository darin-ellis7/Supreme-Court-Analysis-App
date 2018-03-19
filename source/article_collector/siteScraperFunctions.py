import urllib2
from bs4 import BeautifulSoup

#Scrapes CNN's supreme court section. Logic to scrape is correct as of 03/19/2018
#Returns lists of urls of articles
def scrapeCNN():
    supreme_court_link = 'https://www.cnn.com/specials/politics/supreme-court-nine'
    page = urllib2.urlopen(supreme_court_link)
    soup = BeautifulSoup(page, 'html.parser')
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
    page = urllib2.urlopen(supreme_court_link)
    soup = BeautifulSoup(page, 'html.parser')
    articles = soup.find('ol', {'class' : 'story-menu'})
    links = articles.find_all('a', {'class' : 'story-link'})
    for link in links:
        urls.append(link.get('href'))
    return urls