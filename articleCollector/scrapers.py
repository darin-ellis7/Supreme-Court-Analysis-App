from bs4 import BeautifulSoup
from Article import *
from utilityFunctions import *
import newspaper
import ssl
import datetime

# This class deals with the scraping aspects of the project, using both generic (Newspaper-powered) and targeted methods
class Scraper:
    # Since we're collecting initial data from RSS feeds, JSON objects, and topic pages, we don't have to scrape everything from a site - generally things like title and date are already provided, possibly author and images as well
    # So, we can import this data as needed into the object so if it's there we don't need to look for it - but if it isn't, we know what to look for
    # if something isn't provided, it should be passed in as None - with the exception of images, which should be passed in as an empty array
    def __init__(self,url,title,author,date,images):
        self.url = url
        self.title = title
        self.author = author
        self.date = date
        self.images = images
        self.source = getSource(url)

    # driver function for scraping
    def scrape(self):
        # if the page to be scraped is from a source we've already written an individual scraper, use that scraper
        specialSources = ["cnn","nytimes","jdsupra","latimes","politico","thehill"]
        if self.source in specialSources:
            article = self.specificScraper()
            if not article: # fallback for specific scraper - if it fails, then attempt again using the generic scraper
                print(self.source,"scraper failed - now attempting with generic scraper")
                article = self.genericScraper()
        else: # otherwise, use Newspaper to try to get the data
            article = self.genericScraper()
        return article

    # driver for specific-site scrapers
    # returns an Article object, or if something goes wrong, None
    def specificScraper(self):
        soup = downloadPage(self.url)
        if soup: # if page is downloaded, scrape!
            try:
                article = getattr(self,self.source)(soup) # call appropriate scraper based on source name (scraper functions should ALWAYS be named the same as its source for this work, verbatim)
            except Exception as e:
                print("Rejected - SCRAPING ERROR (likely formatting change): ",e)
                article = None
        else:
            article = None
        return article

    # generic scraper for sites that don't have their own scrapers
    def genericScraper(self):
        config = newspaper.Config()
        config.browser_user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14'
        #config.request_timeout = 15

        if self.source not in ["washingtonpost","usnews"]: # washingtonpost and usnews get funky when you set a user agent for some reason (WaPo fails if the timeout isn't long, usnews throws a 403)
            a = newspaper.Article(self.url,config=config)
        else:
            a = newspaper.Article(self.url)
        try: # make sure page download goes smoothly
            a.download()
            a.parse()
        except Exception as e:
            print("Rejected - DOWNLOAD ERROR: ",e)
            return None

        text = cleanText(a.text)
        if len(text) < 500: # not much article text - full article is likely not picked up, and worst case scenario a short article is rejected (probably not all that useful in the long run)
            print("Rejected - Article text was less than 500 characters, likely bad scraping job")
            return None

        # get title, author, date and images as necessary
        if not self.title or self.title.split()[-1] == "...":
            if a.title:
                scrapedTitle = a.title.strip()
                if self.title:
                    self.title = replaceTitle(self.title,scrapedTitle)
                else:
                    self.title = scrapedTitle

        if not self.author:
            if a.authors:
                self.author = a.authors[0]

        if not self.date:
            if a.publish_date:
                self.date = a.publish_date.strftime("%Y-%m-%d")
        
        if not self.images:
            if a.top_image:
                self.images.append(a.top_image)

        article = Article(self.title,self.author,self.date,self.url,self.source,text.strip(),self.images)
        return article

    # scraper for CNN
    # all of these scraping functions are pretty similar, so I'm not commenting on the others unless there's a noticable difference (read the BeautifulSoup docs too)
    def cnn(self,soup):
        opener = soup.find("cite",{"class":"el-editorial-source"})
        if opener:
            opener.decompose()

        if "cnn.com/videos/" in self.url: # video link - no text to be scraped, DROPPED
            print("Rejected - CNN video link")
            return None

        if not self.title or self.title.split()[-1] == "...":
            t = soup.find("h1",{"class":"pg-headline"})
            if t:
                scrapedTitle = t.text.strip()
                if self.title:
                    self.title = replaceTitle(self.title,scrapedTitle)
                else:
                    self.title = scrapedTitle

        if not self.author:
            a = soup.find(itemprop="author")
            if a:
                a = a.get("content")
                self.author = a.split(",")[0].strip()
        
        if not self.date:
            d = soup.find(itemprop="datePublished")
            if d:
                d = d.get("content")
                self.date = convertDate(d,"%Y-%m-%dT%H:%M:%SZ")

        if not self.images:
            i = soup.find(itemprop="image")
            if i:
                i = i.get("content")
                self.images.append(i)

        text = ''
        paragraphs = soup.find_all(["div","p"],{"class":"zn-body__paragraph"}) # paragraphs are contained in <div> and <p> tags with the class 'zn-body__paragraph' - catch 'em all
        if paragraphs:
            for p in paragraphs: # loop through paragraphs and add each one to text string, separated by double new-line
                text += (p.text + '\n\n')
        
        if text == '': # scraping probably went wrong because no text, so return None
            print("Rejected - likely bad scraping job (no article text)")
            return None
        else:
            article = Article(self.title,self.author,self.date,self.url,self.source,text.strip(),self.images)
            return article

    def nytimes(self,soup):
        if not self.title or self.title.split()[-1] == "...":
            t = soup.find("meta",property="og:title")
            if t:
                scrapedTitle = t.get("content").strip()
                if self.title:
                    self.title = replaceTitle(self.title,scrapedTitle)
                else:
                    self.title = scrapedTitle

        if not self.author:
            a = soup.find("meta", {"name":"byl"})
            if a:
                self.author = ' '.join(a['content'].split()[1:])
            
        if not self.date:
            d = soup.find("meta",{"name":"pdate"})
            if d:
                self.date = convertDate(d['content'],"%Y%m%d")

        if not self.images:
            i = soup.find(itemprop="image")
            if i:
                i = i.get("content")
                self.images.append(i)

        text = ''
        container = soup.find("section",{"name":"articleBody"})
        if container:
            #paragraphs = soup.select("p.css-1ebnwsw.e2kc3sl0")
            paragraphs = container.find_all("p")
            if paragraphs:
                for p in paragraphs:
                    text += (p.text + '\n\n')
        
        if text == '':
            print("Rejected - likely bad scraping job (no article text)")
            return None
        else:
            article = Article(self.title,self.author,self.date,self.url,self.source,text.strip(),self.images)
            return article

    def latimes(self,soup):
        if not self.title or self.title.split()[-1] == "...":
            t = soup.find("meta",property="og:title")
            if t:
                scrapedTitle = t.get("content").strip()
                if self.title:
                    self.title = replaceTitle(self.title,scrapedTitle)
                else:
                    self.title = scrapedTitle

        if not self.author:
            a = soup.find("meta", {"name":"author"})
            if a:
                if a['content'].strip() == '':
                    self.author = "Unknown Author"
                else:
                    authsplit = a['content'].split()
                    if authsplit[0].lower() == "by":
                        self.author = ' '.join(authsplit[1:])
                    else:
                        self.author = a['content']
        
        if not self.date:
            d = soup.find("meta", {"name":"date"})
            if d:
                self.date = convertDate(d['content'],"%Y-%m-%dT%H:%M:%SZ")

        if not self.images:
            i = soup.select_one("div.full-width.img-container.aspect-ratio-no-aspect > img")
            if i:
                self.images.append(i['src'])

        text = ''
        container = soup.select_one("div.collection.collection-cards")
        if container:
            paragraphs = container.find_all("p")
            if paragraphs:
                for p in paragraphs:
                    text += (p.text + '\n\n')
        
        if text == '':
            print("Rejected - likely bad scraping job (no article text)")
            return None
        else:
            article = Article(self.title,self.author,self.date,self.url,self.source,text.strip(),self.images)
            return article
            
    def jdsupra(self,soup):
        if not self.title or self.title.split()[-1] == "...":
            t = soup.select_one("h1.doc_name.f2-ns.f3.mv0")
            if t:
                scrapedTitle = t.text.strip()
                if self.title:
                    self.title = replaceTitle(self.title,scrapedTitle)
                else:
                    self.title = scrapedTitle

        if not self.author:
            a = soup.select_one("div.f6.silver.db.dn-l.mt2.tc-ns a")
            if a:
                self.author = a.text

        if not self.date:
            d = soup.find("time")
            if d:
                self.date = convertDate(d.text,"%B %d, %Y")

        text = ''
        container = soup.find("div",{"class":"jds-main-content"})
        if container:
            paragraphs = container.find_all(["p","h2"])
            if paragraphs:
                for p in paragraphs: # differentiating between paragraphs and headers - if <p>, separate by double newline; if <h2>, separate by single newline
                    if p.name == "p": 
                        text += (p.text.strip() + '\n\n')
                    else:
                        text += (p.text.strip() + '\n')
        
        if text == '':
            print("Rejected - likely bad scraping job (no article text)")
            return None
        else:
            article = Article(self.title,self.author,self.date,self.url,self.source,text.strip(),self.images)
            return article

    def politico(self,soup):
        if not self.title or self.title.split()[-1] == "...":
            t = soup.find("meta",property="og:title")
            if t:
                scrapedTitle = t.get("content").strip()
                if self.title:
                    self.title = replaceTitle(self.title,scrapedTitle)
                else:
                    self.title = scrapedTitle

        if not self.author:
            a = soup.select_one("div.story-intro div.summary p.byline")
            if a:
                self.author = a.text.strip()[3:]

        if not self.date:
            d = soup.find(itemprop="datePublished")
            if d:
                self.date = d.get("datetime").split()[0]

        if not self.images:
            i = soup.find("meta",property="og:image")
            if i:
                self.images.append(i.get("content"))

        text = ''
        container = soup.select_one("article.story-main-content")
        if container:
            junk = container.find_all(["div","p"],{"class":["footer__copyright","story-continued","story-intro","byline"]}) + container.find_all("aside")
            for j in junk:
                j.decompose()
            paragraphs = container.find_all("p")
            for p in paragraphs:
                text += (p.text.strip() + '\n\n')
        
        if text == '':
            print("Text is empty - likely bad scraping job (no article text)")
            return None
        else:
            article = Article(self.title,self.author,self.date,self.url,self.source,text.strip(),self.images)
            return article

    def thehill(self,soup):
        junk = soup.find_all("span",{"class":"rollover-people-block"}) # site contains links and headlines for related articles when you rollover a known person in the article - remove these
        for j in junk:
            j.decompose()

        if not self.title or self.title.split()[-1] == "...":
            t = soup.find("meta",property="og:title")
            if t:
                scrapedTitle = t.get("content").strip()
                if self.title:
                    self.title = replaceTitle(self.title,scrapedTitle)
                else:
                    self.title = scrapedTitle

        if not self.author:
            a = soup.find("meta",property="author")
            if a:
                self.author = a.get("content")

        if not self.date:
            d = soup.find("meta",property="article:published_time")
            if d:
                self.date = d.get("content").split("T")[0]

        if not self.images:
            i = soup.find("meta",property="og:image")
            if i:
                self.images.append(i.get("content"))

        text = ''
        paragraphs = soup.select("div.field-items p")
        if paragraphs:
            for p in paragraphs:
                text += (p.text.strip() + '\n\n')
                
        if text == '':
            print("Text is empty - likely bad scraping job (no article text)")
            return None
        else:
            article = Article(self.title,self.author,self.date,self.url,self.source,text.strip(),self.images)
            return article