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
        # the key is the full source name that we print out in the script and potentially has two values -  the first is the name used for the source in its scraper function, the second is a page range if the page being scraped has paginated search results (not every function has this)
        # e.g., for Politico - script prints out "Collecting Los Angeles Times...", calls collectLATimes() function, and searches from page 1 to 1 (inclusive) [default setting is to only scrape first results pages]
        functionCalls = {
                            "CNN":["CNN"], "New York Times":["NYTimes"], "Washington Post":["WaPo"], "Politico":["Politico",[1,1]], "Fox News":["FoxNews"], 
                            "Chicago Tribune": ["ChicagoTribune",[1,1]], "Los Angeles Times":["LATimes",[1,1]],"The Hill":["TheHill",[0,0]], "Reuters":["Reuters"],
                            "New York Post": ["NYPost"], "Huffington Post": ["HuffPost"], "NPR":["NPR"]
                        }
        for source in functionCalls:
            print("Collecting " + source + "...")
            functionName = functionCalls[source][0]
            if len(functionCalls[source]) > 1:
                pageRange = functionCalls[source][1]
                getattr(self,"collect" + functionName)(pageRange)
            else:
                getattr(self,"collect" + functionName)()
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
                    try:
                        url = "https://www.cnn.com" + h['href']
                        title = h.text.strip()
                        s = Scraper(url,title,None,None,[])
                        self.pages.append(s) # build list of pages to scrape
                    except Exception as e:
                            print("SCRAPING ERROR:",e)
                            continue

    def collectPolitico(self,pageRange):
        for i in range(pageRange[0],pageRange[1] + 1):
            url = "https://www.politico.com/news/supreme-court/" + str(i)
            soup = downloadPage(url)
            if soup:
                pages = soup.select("ul.story-frag-list.layout-grid.grid-3 li div.summary")
                if pages:
                    for p in pages:
                        try:
                            headline = p.select_one("h3 a")
                            url = headline['href']
                            title = headline.text.strip()
                            a = p.find(itemprop="name")
                            if a:
                                author = a.get("content").strip()
                            else:
                                author = None

                            d = p.find(itemprop="datePublished")
                            if d:
                                date = convertDate(d.get("datetime"),"%Y-%m-%d %H:%M:%S")
                            else:
                                date = None

                            s = Scraper(url,title,author,date,[])
                            self.pages.append(s)
                        except Exception as e:
                            print("SCRAPING ERROR:",e)
                            continue

    def collectFoxNews(self):
        url = 'https://www.foxnews.com/category/politics/judiciary/supreme-court'
        soup = downloadPage(url)
        if soup:
            container = soup.select_one("div.content.article-list")
            if container:
                pages = container.select("h4.title a")
                if pages:
                    for p in pages:
                        try:
                            if 'video.foxnews.com' not in p['href']:
                                url = "https://www.foxnews.com" + p['href']
                                title = p.text.strip()
                                s = Scraper(url,title,None,None,[])
                                self.pages.append(s)
                        except Exception as e:
                            print("SCRAPING ERROR:",e)
                            continue
                       
    def collectChicagoTribune(self,pageRange):
        for i in range(pageRange[0],pageRange[1]+1):
            url = "http://www.chicagotribune.com/topic/crime-law-justice/justice-system/u.s.-supreme-court-ORGOV0000126-topic.html?page=" + str(i) +"&target=stories&#trb_topicGallery_search"
            soup = downloadPage(url)
            if soup:
                containers = soup.find_all("div",{"class":"trb_search_result_wrapper"})
                for c in containers:
                    try:
                        headline = c.select_one("h3 a")
                        url = "http://www.chicagotribune.com" + headline['href']
                        title = headline.text.strip()

                        a = c.find(itemprop="author")
                        if a:
                            author = a.text.strip()
                        else:
                            author = None

                        d = c.find(itemprop="datePublished")
                        if d:
                            date = d.get("datetime").split("T")[0]
                        else:
                            date = None
                            
                        s = Scraper(url,title,author,date,[])
                        self.pages.append(s)
                    except Exception as e:
                        print("SCRAPING ERROR:",e)
                        continue

    
    def collectTheHill(self,pageRange): # page count starts at 0
        for i in range(pageRange[0],pageRange[1] + 1):
            url = "https://thehill.com/social-tags/supreme-court" + "?page=" + str(i)
            soup = downloadPage(url)
            if soup:
                container = soup.find("div",{"class":"view-content"})
                if container:
                    pages = container.find_all("div",{"class":"views-row"})
                    for p in pages:
                        try:
                            headline = p.select_one("h2.node__title.node-title a")
                            if '/video/' not in headline['href']:
                                url = "https://thehill.com" + headline['href']
                                title = headline.text.strip()
                                submitted = p.find("p",{"class":"submitted"})

                                a = submitted.find("span",{"rel":"sioc:has_creator"})
                                if a:
                                    author = a.text.split(',')[0].strip()
                                else:
                                    author = None

                                d = submitted.find("span",{"class":"date"})
                                if d:
                                    datestr = d.text.split()[0].strip()
                                    date = convertDate(datestr,"%m/%d/%y")
                                else:
                                    date = None

                                s = Scraper(url,title,author,date,[])
                                self.pages.append(s)
                        except Exception as e:
                            print("SCRAPING ERROR:",e)
                            continue

    def collectLATimes(self,pageRange):
        for i in range(pageRange[0],pageRange[1] + 1): # loop through search results pages
            searchURL = "http://www.latimes.com/search/?q=supreme+court&s=date&t=story&p=" + str(i)
            soup = downloadPage(searchURL)
            if soup:
                pages = soup.select("div.h7 a")
                if pages:
                    for p in pages:
                        try:
                            if "/espanol/" not in p['href']: # ignore spanish versions of LATimes articles
                                url = "http://www.latimes.com" + p['href']
                                title = p.text.strip()
                                s = Scraper(url,title,None,None,[])
                                self.pages.append(s)
                        except Exception as e:
                            print("SCRAPING ERROR:",e)
                            continue

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
                    try:
                        author = "David G. Savage" # this is a given since working with a bio page
                        if p.name == "h5": # parsing for large article panes - smaller panes are denoted as <a class:recommender></a>
                            p = p.find("a")
                        if "/espanol/" not in p['href']:
                            url = "http://www.latimes.com" + p['href']
                            title = p.text.strip()
                            s = Scraper(url,title,author,None,[])
                            self.pages.append(s)
                    except Exception as e:
                        print("SCRAPING ERROR:",e)
                        continue

    def collectWaPo(self):
        url = "https://www.washingtonpost.com/politics/courts-law/?utm_term=.7a05b7096145"
        soup = downloadPage(url)
        if soup:
            pages = soup.select("div.story-list-story")
            if pages:
                for p in pages:
                    try:
                        headline = p.select_one("h3 a")
                        title = headline.text.strip()
                        url = headline['href']
                        a = p.select_one("span.author")
                        if a:
                            author = a.text.strip()
                        else:
                            author = None
                        s = Scraper(url,title,author,None,[])
                        self.pages.append(s)
                    except Exception as e:
                        print("SCRAPING ERROR:",e)
                        continue
                        
    def collectNYTimes(self):
        url = "https://www.nytimes.com/topic/organization/us-supreme-court"
        soup = downloadPage(url)
        if soup:
            container = soup.select_one("ol.story-menu.theme-stream.initial-set")
            if container:
                pages = container.select("li a")
                if pages:
                    for p in pages:
                        try:
                            url = p["href"] 
                            title = p.select_one("h2.headline").text.strip()
                            a = p.select_one("p.byline")
                            if a:
                                author = a.text[3:].strip()
                            else:
                                author = None
                            s = Scraper(url,title,author,None,[])
                            self.pages.append(s)
                        except Exception as e:
                            print("SCRAPING ERROR:",e)
                            continue
                        
    def collectReuters(self):
        url = "https://www.reuters.com/subjects/supreme-court"
        soup = downloadPage(url)
        if soup:
            container = soup.select_one("div.FeedPage_item-list span")
            if container:
                pages = container.select("div.FeedItem_item")
                if pages:
                    for p in pages:
                        try:
                            url = p.select_one("h2.FeedItemHeadline_headline a")["href"]
                            title = p.select_one("h2.FeedItemHeadline_headline").text.strip()
                            i = p.select_one("span a img")
                            if i:
                                images = [i["src"]]
                            else:
                                images = []
                            s = Scraper(url,title,None,None,images)
                            self.pages.append(s)
                        except Exception as e:
                            print("SCRAPING ERROR:",e)
                            continue
                                        
    def collectNPR(self):
        url = "https://www.npr.org/tags/125938785/supreme-court"
        soup = downloadPage(url)
        if soup:
            containers = []
            containers.append(soup.select_one("main div.featured"))
            containers.append(soup.select_one("main div.list-overflow"))
            if (containers[0] and containers[1]):
                for c in containers:
                    pages = c.select("div.item-info")
                    if pages:
                        for p in pages:
                            try:
                                url = p.select_one("h2.title a")["href"]
                                title = p.select_one("h2.title a").text.strip()
                                #print(title,url)
                                s = Scraper(url,title,None,None,[])
                                self.pages.append(s)
                            except Exception as e:
                                print("SCRAPING ERROR:",e)
                                continue
                            
    def collectNYPost(self):
        url = "https://nypost.com/tag/supreme-court/"
        soup = downloadPage(url)
        if soup:
            container = soup.select_one("div.article-loop")
            if container:
                pages = container.select("article")
                if pages:
                    for p in pages:
                        try:
                            url = p.select_one("h3.entry-heading a")["href"]
                            title = p.select_one("h3.entry-heading a").text.strip()
                            d = p.select_one("div.entry-meta p")
                            if d:
                                datestr = d.text.split("|")[0].strip()
                                date = convertDate(datestr,"%B %d, %Y")
                            else:
                                date = None
                            s = Scraper(url,title,None,date,[])
                            self.pages.append(s)
                        except Exception as e:
                            print("SCRAPING ERROR:",e)
                            continue
                        
    def collectHuffPost(self):
        url = "https://www.huffingtonpost.com/topic/supreme-court"
        soup = downloadPage(url)
        if soup:
            containers = []
            containers.append(soup.select_one("section.js-zone-twilight_upper"))
            containers.append(soup.select_one("section.js-zone-twilight_lower"))
            if (containers[0] and containers[1]):
                for c in containers:
                    pages = c.select("div.card")
                    if pages:
                        for p in pages:
                            try:
                                url = "https://www.huffingtonpost.com" + p.select_one("a.card__image__wrapper")["href"]
                                title = p.select_one("div.card__headline__text").text.strip()
                                a = p.select_one("div.card__byline")
                                author = None
                                if a:
                                    atext = a.text.strip()
                                    if atext != '':
                                        asplit = atext.split()
                                        author = ' '.join(asplit[1:]).strip()
                                s = Scraper(url,title,author,None,[])
                                self.pages.append(s)
                            except Exception as e:
                                print("SCRAPING ERROR:",e)
                                continue
         
#t = TopicSites()
#t.collectNPR()

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
                title = cleanTitle(post['title']).strip()
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
            results = self.newsapi.get_everything(q=q, language='en', page_size=100, from_param=two_days_ago, to=today, sort_by='relevancy')
            for entry in results['articles']:
                #if successes > 3:
                    #break
                total += 1
                images = []
                # get as much information as possible about the article before shipping it off to the scraper

                if entry['title']:
                    title = entry['title'].strip()
                else:
                    title = "Untitled"

                if entry['urlToImage']:
                    images.append(entry['urlToImage'])

                if entry['author']:
                    author = entry['author'].strip()
                else:
                    author = None

                if entry['publishedAt']:
                    date = convertDate(entry['publishedAt'],"%Y-%m-%dT%H:%M:%SZ")
                else:
                    date = None

                printBasicInfo(title,entry['url'])
                try:
                    if not articleIsDuplicate(title,c):
                        if not isBlockedSource(entry['url']):
                            s = Scraper(entry['url'],title,author,date,images)
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
