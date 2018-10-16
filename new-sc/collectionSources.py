# The classes in this file are essentially drivers - how data is gathered (Google Alerts RSS Feeds, News API, and topic pages on various news sites - that last one hasn't been implemented yet)
import feedparser
from scrapers import *
from utilityFunctions import *
from newsapi import NewsApiClient
import datetime

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

                print(title)
                print(url)
                s = Scraper(url,title,None,date,[])
                try:
                    article = s.scrape()
                    if article:
                        # add to database
                        successes += 1
                        #print(article.title)
                        print(article.author)
                        print(article.date)
                        print(article.keywords)
                        print(article.images)
                        print()
                        print(article.text)
                    
                except Exception as e:
                    print(e)
                    continue
                print("======================================")
        print()
        print("***",successes,"/",total,"collected from Google Alerts RSS Feeds ***")

#
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

                print(entry['title'])
                print(entry['url'])

                s = Scraper(entry['url'],entry['title'],author,date,images)
                try: 
                    article = s.scrape()
                    if article:
                        successes += 1
                        #print(article.title)
                        print(article.author)
                        print(article.date)
                        print(article.images)
                        print()
                        print(article.text)
                except Exception as e:
                    print(e)
                print("======================================")
        print()
        print("***",successes,"/",total,"collected from NewsAPI results ***")