# The classes in this file are essentially drivers - how data is gathered (Google Alerts RSS Feeds, News API, and topic pages on various news sites - that last one hasn't been implemented yet)
import feedparser
from scrapers import *
from utilityFunctions import *
from newsapi import NewsApiClient
from bs4 import BeautifulSoup
import datetime

class TopicSites:
    def __init__(self):
        self.pages = []

    # topic site driver
    def collect(self):
        print("Collecting CNN articles...")
        self.collectCNN()
        print("Collecting Politico articles...")
        print()
        self.collectPolitico()
        successes = 0
        for p in self.pages:
            printBasicInfo(p.title,p.url)
            article = p.scrape()
            if article:
                article.printInfo()
                if article.isRelevant():
                    # add to database
                    successes += 1
                    print("Accepted")
            print("=================================")
        print("***",successes,"/",len(self.pages),"articles collected from topic sites ***")
        print("=================================")

    # scrapes CNN's supreme court topic page for articles and their metadata - other functions should be pretty similar
    def collectCNN(self):
        url = "https://www.cnn.com/specials/politics/supreme-court-nine"
        soup = downloadPage(url)
        if soup:
            # remove journalist sidebar (it gets in the way of properly scraping)
            journalistSidebar = soup.find("div",{"class":"column zn__column--idx-1"})
            if journalistSidebar:
                journalistSidebar.decompose()

            headlines = soup.select("h3.cd__headline a")
            if headlines:
                for h in headlines:
                    url = "https://www.cnn.com" + h['href']
                    title = h.text
                    s = Scraper(url,title,None,None,[])
                    self.pages.append(s) # build list of pages to scrape

    def collectPolitico(self):
        links = {}
        url = "https://www.politico.com/news/supreme-court"
        soup = downloadPage(url)
        if soup:
            pages = soup.select("ul.story-frag-list.layout-grid.grid-3 li div.summary")
            if pages:
                for p in pages:
                    headline = p.select_one("h3 a")
                    url = headline['href']
                    title = headline.text
                    author = p.find(itemprop="name").get("content")
                    date = convertDate(p.find(itemprop="datePublished").get("datetime"),"%Y-%m-%d %H:%M:%S")
                    s = Scraper(url,title,author,date,[])
                    self.pages.append(s)

class RSSFeeds:
    def __init__(self,feeds):
        self.feeds = feeds

    def parseFeeds(self):
        total = 0
        successes = 0
        for feed in self.feeds:
            feed = feedparser.parse(feed)
            for post in feed.entries:
                total += 1
                url = getURL(post['link'])
                title = cleanTitle(post['title'])
                date = convertDate(post['date'],"%Y-%m-%dT%H:%M:%SZ")

                printBasicInfo(title,url)
                s = Scraper(url,title,None,date,[])

                article = s.scrape()
                if article:
                    article.printInfo()
                    if article.isRelevant():
                        # add to database
                        successes += 1
                        print("Accepted")
                
                print("======================================")
        print("***",successes,"/",total,"articles collected from Google Alerts RSS Feeds ***")
        print("======================================")

class NewsAPICollection:
    def __init__(self,queries):
        self.queries = queries
        self.newsapi = NewsApiClient(api_key='43fe19e9160d4a178e862c796a06aea8') # this should be set as an environment variable at some point, it's never a good idea to hardcode API keys
    
    def parseResults(self):
        total = 0
        successes = 0

        # check articles from the the last two days (in case a problem arises and we can 'go back in time')
        today = datetime.datetime.now()
        two_days_ago = (today - datetime.timedelta(days=2)).strftime('%Y-%m-%d')
        today = today.strftime('%Y-%m-%d')
        for q in self.queries:
            results = self.newsapi.get_everything(q=q, language='en', page_size=100, from_param=two_days_ago, to=today, sort_by='relevancy')
            for entry in results['articles']:
                total += 1
                images = []
                if entry['urlToImage']:
                    images.append(entry['urlToImage'])

                if entry['author']:
                    author = entry['author']
                else:
                    author = None

                if entry['publishedAt']:
                    date = convertDate(entry['publishedAt'],"%Y-%m-%dT%H:%M:%SZ")
                else:
                    date = None

                printBasicInfo(entry['title'],entry['url'])
                s = Scraper(entry['url'],entry['title'],author,date,images)
                try: 
                    article = s.scrape()
                    if article:
                        article.printInfo()
                        if article.isRelevant():
                            # add to database
                            successes += 1
                            print("Accepted")
                except Exception as e:
                    print(e)
                print("======================================")
        print("***",successes,"/",total," articles collected from NewsAPI results ***")
        print("======================================")