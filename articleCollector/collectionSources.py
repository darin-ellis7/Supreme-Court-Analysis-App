# The classes in this file are essentially drivers - how data is gathered (Google Alerts RSS Feeds, News API, and topic pages on various news sites - that last one hasn't been implemented yet)
import feedparser
from scrapers import *
from utilityFunctions import *
from newsapi import NewsApiClient
from bs4 import BeautifulSoup
import datetime
import re
import MySQLdb
from SeleniumInstance import *

# functions for scraping individual Supreme Court news pages from various well-known sources
class TopicSites:
    def __init__(self):
        self.pages = []

    # topic site driver
    def collect(self,c,clf,v_text,v_title,tz,smm):
        print("*** Topic Sites Scraping ***")
        print()
        # this dict allows us to dynamically call topic site scrapers without actually writing them in the code
        # the key is the full source name that we print out in the script and potentially has two values -  the first is the name used for the source in its scraper function, the second is a page range if the page being scraped has paginated search results (not every function has this)
        # e.g., for Politico - script prints out "Collecting Los Angeles Times...", calls collectLATimes() function, and searches from page 1 to 1 (inclusive) [default setting is to only scrape first results pages]
        functionCalls = {
                            "CNN":["CNN"], "New York Times":["NYTimes"], "Washington Post":["WaPo"], "Politico":["Politico",[1,1]], "Fox News":["FoxNews"], 
                            "Chicago Tribune": ["ChicagoTribune",[1,1]], "Los Angeles Times":["LATimes",[1,1]],"The Hill":["TheHill",[0,0]], "Reuters":["Reuters"],
                            "New York Post": ["NYPost"], "Huffington Post": ["HuffPost"], "NPR":["NPR"], "Wall Street Journal":["WSJ",[1,1]]
                        }
        oldsize = len(self.pages)
        dead_sources = [] # list of potentially outdated topic site scrapers (we'll need to notify the admins)
        for source in functionCalls:
            print("Collecting " + source + "...")
            functionName = functionCalls[source][0]
            if len(functionCalls[source]) > 1:
                pageRange = functionCalls[source][1]
                getattr(self,"collect" + functionName)(pageRange)
            else:
                getattr(self,"collect" + functionName)()
            if len(self.pages) == oldsize: # if pages array hasn't grown after a topic site visit, there's a good chance the scraper isn't working anymore - add to dead sources
                dead_sources.append(source)
            oldsize = len(self.pages) 
        if dead_sources:
            self.TopicSiteAlert(dead_sources,c)
        else: # all topic sites functional - remove any alerts from DB
            c.execute("""DELETE FROM alerts WHERE type='TS'""")
        print()
        successes = 0
        si = SeleniumInstance()
        for p in self.pages:
            #if successes > 1:
                #break
            printBasicInfo(p.title,p.url)
            try:
                if not articleIsDuplicate(p.title,p.url,c) and not rejectedIsDuplicate(p.title,p.url,c):
                    driver = decideScraperMethod(p.source,si)
                    article = p.scrape(c,driver,tz)
                    if article:
                        article.printInfo()
                        if article.isRelevant_exp(clf,v_text,v_title,c,True):
                            # add to database
                            article.addToDatabase(c,smm)
                            article.printAnalysisData()
                            successes += 1
                            print()
                            print("Added to database")
            except MySQLdb.Error as e:
                print("Database Error (operation skipped) -",e)         
            print("=================================")
        print("***",successes,"/",len(self.pages),"articles collected from topic sites ***")
        print("=================================")
        if si.driver: 
            # if a webdriver is open, we close it at the end of every "phase" (Google Alerts -> NewsAPI -> TopicSites)
            # This is done to prevent memory leaks as it seems the longer a webdriver is open, the more memory it takes up
            print("Selenium driver was properly quit.")
            si.driver.quit()
    
    # alerts app admins to a topic site scraper that is no longer collecting articles
    def TopicSiteAlert(self,dead_sources,c):
        source_str = ', '.join(dead_sources) # store downed sources in db via comma-delimited format
        print("\nThe following topic site sources failed to scrape any articles:",source_str)
        c.execute("SELECT * FROM alerts WHERE sources=%s AND type='TS' LIMIT 1",(source_str,)) # check if alert already exists in database (don't want to send alert every time script is run)
        if c.rowcount == 0:
            c.execute("""INSERT INTO alerts(sources,type) VALUES (%s,'TS')""",(source_str,))
            subject = "SCOTUSApp - Topic Site Outage"
            text = "During the latest run of the SCOTUSApp article collection script, the following topic site sources failed to scrape any articles: " + source_str + "\n\nThis usually means a topic site scraper has become outdated - it may require maintenance."
            sendAlert(subject,text)

    # scrapes CNN's supreme court topic page for articles and their metadata - other functions should be pretty similar, so avoiding commenting those much
    def collectCNN(self):
        url = "https://www.cnn.com/specials/politics/supreme-court-nine"
        soup = downloadPage(url)
        if soup:
            # remove journalist sidebar (it gets in the way of properly scraping)
            junk = soup.find_all("div",{"class":"column zn"})
            if junk and len(junk) > 1:
                journalistSidebar = junk[1]
                journalistSidebar.decompose()

            headlines = soup.select("h3.cd__headline a")
            if headlines:
                for h in headlines:
                    try:
                        if not h['href'].startswith("/videos/") and "/live-news/" not in h['href']: # keeping video and live blogs out of the feed
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
                                date = d.get("datetime").strip()
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
            url = "https://www.chicagotribune.com/search/supreme%20court/1-w/story/score/" + str(i) + "/"
            soup = downloadPage(url)
            if soup:
                pages = soup.select("ul.flex-grid li.col")
                for p in pages:
                    try:
                        h = p.select_one("p.h7 > a")
                        title = h.text.strip()
                        url = "https://www.chicagotribune.com" + h['href']
                        author = None
                        a = p.select_one("span.byline  > span")
                        if a: author = a.text.strip()
                        s = Scraper(url,title,author,None,[])
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
                                s = Scraper(url,title,author,None,[])
                                self.pages.append(s)
                        except Exception as e:
                            print("SCRAPING ERROR:",e)
                            continue

    def collectLATimes(self,pageRange):
        staffURL = "http://www.latimes.com/la-bio-david-savage-staff.html" # David Savage writes most Supreme Court articles, so we're checking his page first
        self.LATimesCollectionScraper(staffURL,"David G. Savage")
        for i in range(pageRange[0],pageRange[1] + 1): # loop through search results pages
            searchURL = "http://www.latimes.com/search/?q=supreme+court&s=date&t=story&p=" + str(i)
            self.LATimesCollectionScraper(searchURL,None)
    
    def LATimesCollectionScraper(self,url,author): # set author parameter when scraping David G. Savage's page
        soup = downloadPage(url)
        if soup:
            pages = soup.select("div.PromoMedium-wrapper")
            for p in pages:
                try:
                    a = p.select_one("div.PromoMedium-title a")
                    url = a['href']
                    title = a.text.strip()
                    images = []
                    i = p.select_one("div.PromoMedium-media img")
                    if i: images = [i['data-src']]
                    s = Scraper(url,title,author,None,images)
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
                        headline = p.select_one("h2 a")
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
            pages = soup.select("section[id=stream-panel] li")
            for p in pages:
                try:
                    url = "https://www.nytimes.com" + p.find("a")['href']
                    title = p.find("h2").text.strip()
                    a = p.select_one("span.css-1n7hynb")
                    if a:
                        author = a.text.strip()
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
            pages = soup.select("div.FeedItem_item")
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
                                s = Scraper(url,title,None,None,[])
                                self.pages.append(s)
                            except Exception as e:
                                print("SCRAPING ERROR:",e)
                                continue
                            
    def collectNYPost(self):
        url = "https://nypost.com/tag/supreme-court/"
        soup = downloadPage(url)
        if soup:
                pages = soup.select("div.entry-header")
                if pages:
                    for p in pages:
                        try:
                            url = p.select_one("h3.entry-heading a")["href"]
                            title = p.select_one("h3.entry-heading a").text.strip()
                            d = p.select_one("div.entry-meta p")
                            if d:
                                datesplit = d.text.split("|")
                                date = datesplit[0].strip()
                                time = convertTime(datesplit[1].strip().upper(),"%I:%M%p")
                                datestr = date + " " + time
                                date = convertDate(datestr,"%B %d, %Y %H:%M:%S")
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
                junk = [soup.find("div",{"id":"zone-trending"}),soup.find("div",{"class":"card--newsletter"})]
                for j in junk: 
                    if j: j.decompose()
                pages = soup.select("div.card")
                for p in pages:
                    try:
                        h = p.select_one("a.card__headline")
                        url = h['href']
                        title = h.text.strip()
                        author = None
                        auths = p.select("span.card__byline__author")
                        if auths:
                            auths = [a.text.strip() for a in auths]
                            author = ' & '.join(auths)
                        s = Scraper(url,title,author,None,[])
                        self.pages.append(s)
                    except Exception as e:
                        print("SCRAPING ERROR:",e)
                        continue
    
    def collectWSJ(self,pageRange):
        max_date = datetime.datetime.today()
        min_date = (max_date - datetime.timedelta(days=2)).strftime('%Y/%m/%d') # searching for articles published in the last two days
        max_date = max_date.strftime('%Y/%m/%d')
        for i in range(pageRange[0],pageRange[1]+1):
            url = "https://www.wsj.com/search/term.html?KEYWORDS=supreme%20court&min-date=" + min_date + "&max-date=" + max_date + "&isAdvanced=true&daysback=7d&andor=AND&sort=relevance&source=wsjarticle,wsjblogs&page=" + str(i)
            soup = downloadPage(url)
            # WSJ has some funkiness (maybe an actual error) in their formatting on the search page that makes BeautifulSoup parsing tricky
            # so we have to convert our soup object to a str and manipulate the HTML to parse it properly
            soupstr = str(soup)
            find = soupstr.find('<div class="search-results-sector">') # what we want starts at the beginning of this element
            if find > -1:
                soupstr = "<html>" + soupstr[find:] # create an easily-parsable HTML document out of the remainder of the page
                soup = BeautifulSoup(soupstr,"html.parser") #...and convert it to a Soup for scraping (now it's business as usual)
                if soup:
                    pages = soup.select("div.item-container")
                    for p in pages:
                        try:
                            c = p.select_one("div.category")
                            if c:
                                category = c.text.strip().lower()
                                blockedCategories = ["u.k.","india","latin america","europe","world","photos","corrections & amplifications"] # search results in these categories are useless to us
                                if category not in blockedCategories:
                                    h = p.select_one("h3.headline a")
                                    title = h.text.strip()
                                    url = "https://wsj.com" + h['href'].split('?')[0]
                                    author = None
                                    a = p.select_one("li.byline")
                                    if a:
                                        author = a.text.strip()[3:]
                                    s = Scraper(url,title,author,None,[])
                                    self.pages.append(s)
                        except Exception as e:
                            print("SCRAPING ERROR;",e)

# functions for Google Alerts RSS feeds
class RSSFeeds:
    def __init__(self,feeds):
        self.feeds = feeds # list of feeds to parse
    
    # driver
    def parseFeeds(self,c,clf,v_text,v_title,tz,smm):
        print("*** Google Alerts RSS Feeds ***")
        print()
        total = 0
        successes = 0
        si = SeleniumInstance()
        for feed in self.feeds:
            feed = feedparser.parse(feed)
            for post in feed.entries:
                #if successes > 1:
                    #break
                total += 1
                url = getURL(post['link'])
                title = processTitle(cleanTitle(post['title']).strip())
                date = tz.fromutc(datetime.datetime.strptime(post['date'],"%Y-%m-%dT%H:%M:%SZ")).strftime("%Y-%m-%d %H:%M:%S")
                printBasicInfo(title,url)
                try:
                    if not articleIsDuplicate(title,url,c) and not rejectedIsDuplicate(title,url,c):
                        if not isBlockedSource(url):
                            s = Scraper(url,title,None,date,[])
                            driver = decideScraperMethod(s.source,si)
                            article = s.scrape(c,driver,tz)
                            if article:
                                article.printInfo()
                                if article.isRelevant_exp(clf,v_text,v_title,c,True):
                                    # add to database
                                    article.addToDatabase(c,smm)
                                    article.printAnalysisData()
                                    successes += 1
                                    print()
                                    print("Added to database")
                except MySQLdb.Error as e:
                    print("Database Error (operation skipped) -",e)
                print("======================================")
        print("***",successes,"/",total,"articles collected from Google Alerts RSS Feeds ***")
        if si.driver:
            print("Selenium driver was properly quit.")
            si.driver.quit()
        print("======================================")

# functions for NewsAPI functionality
class NewsAPICollection:
    def __init__(self,newsapi_key,queries):
        self.queries = queries # list of queries to search NewsAPI for
        self.newsapi = NewsApiClient(api_key=newsapi_key)
    
    # driver
    def parseResults(self,c,clf,v_text,v_title,tz,smm):
        print("*** NewsAPI Search ***")
        print()
        total = 0
        successes = 0
        # check articles from the the last two days (in case a problem arises and we can 'go back in time')
        today = datetime.datetime.now()
        days_ago = (today - datetime.timedelta(days=2)).strftime('%Y-%m-%d')
        today = today.strftime('%Y-%m-%d')
        si = SeleniumInstance()
        for q in self.queries:
            results = self.newsapi.get_everything(q=q, language='en', page_size=100, from_param=days_ago, to=today, sort_by='relevancy')
            for entry in results['articles']:
                #if successes > 1:
                    #break
                total += 1
                images = []
                # get as much information as possible about the article before shipping it off to the scraper
                if entry['title']:
                    title = processTitle(entry['title'].strip())
                else:
                    title = untitledArticle()
                if entry['urlToImage']:
                    images.append(entry['urlToImage'])
                if entry['author']:
                    author = entry['author'].strip()
                else:
                    author = None
                if entry['publishedAt']:
                    date = tz.fromutc(datetime.datetime.strptime(entry['publishedAt'],"%Y-%m-%dT%H:%M:%SZ")).strftime("%Y-%m-%d %H:%M:%S")
                else:
                    date = None
                printBasicInfo(title,entry['url'])
                try:
                    if not articleIsDuplicate(title,entry['url'],c) and not rejectedIsDuplicate(title,entry['url'],c):
                        if not isBlockedSource(entry['url']):
                            s = Scraper(entry['url'],title,author,date,images)
                            driver = decideScraperMethod(s.source,si)
                            article = s.scrape(c,driver,tz)
                            if article:
                                article.printInfo()
                                if article.isRelevant_exp(clf,v_text,v_title,c,True):
                                    # add to database
                                    article.addToDatabase(c,smm)
                                    article.printAnalysisData()
                                    successes += 1
                                    print()
                                    print("Added to database")
                except MySQLdb.Error as e:
                    print("Database Error (operation skipped) -",e)
                print("======================================")
        print("***",successes,"/",total," articles collected from NewsAPI results ***")
        if si.driver:
            print("Selenium driver was properly quit.")
            si.driver.quit()
        print("======================================")