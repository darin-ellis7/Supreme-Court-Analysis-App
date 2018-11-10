# The classes in this file are essentially drivers - how data is gathered (Google Alerts RSS Feeds, News API, and topic pages on various news sites - that last one hasn't been implemented yet)
import feedparser
from scrapers import *
from utilityFunctions import *
from newsapi import NewsApiClient
from bs4 import BeautifulSoup
import datetime
import MySQLdb

# functions for scraping individual Supreme Court news pages from various well-known sources
class TopicSites:
    def __init__(self):
        self.pages = []

    # topic site driver
    def collect(self,c):
        print("*** Topic Sites Scraping ***")
        print()
        # this dict allows us to dynamically call topic site scrapers without actually writing them in the code
        # the key is the full source name that we print out in the script, the value is the name used for the source in its scraper function
        # e.g., for Los Angeles Times - script prints out "Collecting Los Angeles Times...", calls collectLATimes() function
        functionCalls = {"CNN":["CNN"], "Politico":["Politico",[1,1]], "Fox News":["FoxNews"], "Chicago Tribune": ["ChicagoTribune",[1,1]], "Los Angeles Times":["LATimes",[1,1]],"The Hill":["TheHill",[0,0]]}
        for source in functionCalls:
            print("Collecting " + source + "...")
            try:
                functionName = functionCalls[source][0]
                if len(functionCalls[source]) > 1:
                    pageRange = functionCalls[source][1]
                    getattr(self,"collect" + functionName)(pageRange)
                else:
                    getattr(self,"collect" + functionName)()
            except Exception as e:
                print("Something went wrong when collecting from",source,"-",e)
                continue
        print()
        successes = 0
        for p in self.pages:
            '''if successes > 1:
                break'''
            printBasicInfo(p.title,p.url)
            try:
                if not articleIsDuplicate(p.title,c):
                    article = p.scrape()
                    if article:
                        article.printInfo()
                        if article.isRelevant():
                            # add to database
                            #article.addToDatabase(c)
                            #article.printAnalysisData()
                            successes += 1
                            print()
                            print("Added to database")
            except MySQLdb.Error as e:
                print("Database Error (operation skipped) -",e)         
            print("=================================")
        print("***",successes,"/",len(self.pages),"articles collected from topic sites ***")
        print("=================================")

    # scrapes CNN's supreme court topic page for articles and their metadata - other functions should be pretty similar, so avoiding commenting those much
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

    def collectPolitico(self,pageRange):
        for i in range(pageRange[0],pageRange[1] + 1):
            url = "https://www.politico.com/news/supreme-court/" + str(i)
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

    def collectFoxNews(self):
        url = 'https://www.foxnews.com/category/politics/judiciary/supreme-court'
        soup = downloadPage(url)
        if soup:
            container = soup.select_one("div.content.article-list")
            if container:
                pages = container.select("h4.title a")
                if pages:
                    for p in pages:
                        if 'video.foxnews.com' not in p['href']:
                            url = "https://www.foxnews.com" + p['href']
                            title = p.text
                            s = Scraper(url,title,None,None,[])
                            self.pages.append(s)
                       
    def collectChicagoTribune(self,pageRange):
        for i in range(pageRange[0],pageRange[1]+1):
            url = "http://www.chicagotribune.com/topic/crime-law-justice/justice-system/u.s.-supreme-court-ORGOV0000126-topic.html?page=" + str(i) +"&target=stories&#trb_topicGallery_search"
            soup = downloadPage(url)
            if soup:
                containers = soup.find_all("div",{"class":"trb_search_result_wrapper"})
                for c in containers:
                    headline = c.select_one("h3 a")
                    url = "http://www.chicagotribune.com" + headline['href']
                    title = headline.text
                    author = c.find(itemprop="author")
                    if author:
                        author = author.text
                    else:
                        author = None
                    date = convertDate(c.find(itemprop="datePublished").get("datetime"), "%Y-%m-%dT%H:%M:%SCDT")
                    s = Scraper(url,title,author,date,[])
                    self.pages.append(s)

    
    def collectTheHill(self,pageRange): # page count starts at 0
        for i in range(pageRange[0],pageRange[1] + 1):
            url = "https://thehill.com/social-tags/supreme-court" + "?page=" + str(i)
            soup = downloadPage(url)
            if soup:
                container = soup.find("div",{"class":"view-content"})
                if container:
                    pages = container.find_all("div",{"class":"views-row"})
                    for p in pages:
                        headline = p.select_one("h2.node__title.node-title a")
                        if '/video/' not in headline['href']:
                            url = "https://thehill.com" + headline['href']
                            title = headline.text
                            submitted = p.find("p",{"class":"submitted"})
                            author = submitted.find("span",{"rel":"sioc:has_creator"}).text.split(',')[0]
                            datestr = submitted.find("span",{"class":"date"}).text.split()[0]
                            date = convertDate(datestr,"%m/%d/%y")
                            s = Scraper(url,title,author,date,[])
                            self.pages.append(s)

    def collectLATimes(self,pageRange):
        for i in range(pageRange[0],pageRange[1] + 1): # loop through search results pages
            searchURL = "http://www.latimes.com/search/?q=supreme+court&s=date&t=story&p=" + str(i)
            soup = downloadPage(searchURL)
            if soup:
                pages = soup.select("div.h7 a")
                if pages:
                    for p in pages:
                        if "/espanol/" not in p['href']: # ignore spanish versions of LATimes articles
                            url = "http://www.latimes.com" + p['href']
                            title = p.text
                            s = Scraper(url,title,None,None,[])
                            self.pages.append(s)

        staffURL = "http://www.latimes.com/la-bio-david-savage-staff.html"
        soup = downloadPage(staffURL)
        if soup:
            # author bio pane gets in the way - remove it
            staffPane = soup.select_one("div.card-content.flex-container-column.align-items-start")
            if staffPane:
                staffPane.decompose()
            pages = soup.find_all(["h5","a"],{"class":["","recommender"]})
            if pages:
                for p in pages:
                    author = "David G. Savage" # this is a given since working with a bio page
                    if p.name == "h5": # parsing for large article panes - smaller panes are denoted as <a class:recommender></a>
                        p = p.find("a")
                    if "/espanol/" not in p['href']:
                        url = "http://www.latimes.com" + p['href']
                        title = p.text
                        s = Scraper(url,title,author,None,[])
                        self.pages.append(s)

        '''# scraping two pages here - the first is a search page for "supreme court", the second is LA Times writer David Savage's bio page; he seems to write exclusively on the Supreme Court
        urls = ["http://www.latimes.com/search/?q=supreme+court&s=date&t=story", "http://www.latimes.com/la-bio-david-savage-staff.html"]
        scrapingStaffPage = False # flag set after scraping the search page
        for u in urls:
            soup = downloadPage(u)
            if soup:
                if not scrapingStaffPage: # scraping articles from search page
                    pages = soup.select("div.h7 a") 
                else: # scraping from David Savage's page
                    # author bio pane gets in the way - remove it
                    staffPane = soup.select_one("div.card-content.flex-container-column.align-items-start")
                    if staffPane:
                        staffPane.decompose()
                    pages = soup.find_all(["h5","a"],{"class":["","recommender"]})

                if pages:
                    for p in pages:
                        if scrapingStaffPage:
                            author = "David G. Savage" # this is a given since working with a bio page
                            if p.name == "h5": # parsing for large article panes - smaller panes are denoted as <a class:recommender></a>
                                p = p.find("a")
                        else:
                            author = None

                        if "/espanol/" not in p['href']: # ignore spanish versions of LATimes articles
                            url = "http://www.latimes.com" + p['href']
                            title = p.text
                            s = Scraper(url,title,author,None,[])
                            self.pages.append(s)
                scrapingStaffPage = True'''

#t = TopicSites()
#t.collectChicagoTribune([2,3])

# functions for Google Alerts RSS feeds
class RSSFeeds:
    def __init__(self,feeds):
        self.feeds = feeds # list of feeds to parse
    
    # driver
    def parseFeeds(self,c):
        print("*** Google Alerts RSS Feeds ***")
        print()
        total = 0
        successes = 0
        for feed in self.feeds:
            feed = feedparser.parse(feed)
            for post in feed.entries:
                #if successes > 5:
                    #break
                total += 1
                url = getURL(post['link'])
                title = cleanTitle(post['title'])
                date = convertDate(post['date'],"%Y-%m-%dT%H:%M:%SZ")

                printBasicInfo(title,url)
                try:
                    if not articleIsDuplicate(title,c):
                        if not isBlockedSource(url):
                            s = Scraper(url,title,None,date,[])
                            article = s.scrape()
                            if article:
                                article.printInfo()
                                if article.isRelevant():
                                    # add to database
                                    #article.addToDatabase(c)
                                    #article.printAnalysisData()
                                    successes += 1
                                    print()
                                    print("Added to database")
                except MySQLdb.Error as e:
                    print("Database Error (operation skipped) -",e)
                print("======================================")
        print("***",successes,"/",total,"articles collected from Google Alerts RSS Feeds ***")
        print("======================================")

# functions for NewsAPI functionality
class NewsAPICollection:
    def __init__(self,queries):
        self.queries = queries # list of queries to search NewsAPI for
        self.newsapi = NewsApiClient(api_key='43fe19e9160d4a178e862c796a06aea8') # this should be set as an environment variable at some point, it's never a good idea to hardcode API keys
    
    # driver
    def parseResults(self,c):
        print("*** NewsAPI Search ***")
        print()
        total = 0
        successes = 0
        # check articles from the the last two days (in case a problem arises and we can 'go back in time')
        today = datetime.datetime.now()
        two_days_ago = (today - datetime.timedelta(days=2)).strftime('%Y-%m-%d')
        today = today.strftime('%Y-%m-%d')
        for q in self.queries:
            results = self.newsapi.get_everything(q=q, language='en', page_size=50, from_param=two_days_ago, to=today, sort_by='relevancy')
            for entry in results['articles']:
                #if successes > 3:
                    #break
                total += 1
                images = []
                # get as much information as possible about the article before shipping it off to the scraper
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
                try:
                    if not articleIsDuplicate(entry['title'],c):
                        if not isBlockedSource(entry['url']):
                            s = Scraper(entry['url'],entry['title'],author,date,images)
                            article = s.scrape()
                            if article:
                                article.printInfo()
                                if article.isRelevant():
                                    # add to database
                                    #article.addToDatabase(c)
                                    #article.printAnalysisData()
                                    successes += 1
                                    print()
                                    print("Added to database")
                except MySQLdb.Error as e:
                    print("Database Error (operation skipped) -",e)
                print("======================================")
        print("***",successes,"/",total," articles collected from NewsAPI results ***")
        print("======================================")