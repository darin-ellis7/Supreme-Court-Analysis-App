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
        specialSources = ["cnn","nytimes","jdsupra","latimes"]
        if self.source in specialSources:
            article = self.specificScraper()
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

        a = newspaper.Article(self.url,config=config)
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
        if not self.title:
            if a.title:
                self.title = a.title
            else:
                self.title = "Untitled"

        if not self.author:
            if a.authors:
                self.author = a.authors[0]
            else:
                self.author = "Unknown Author"

        if not self.date:
            if a.publish_date:
                self.date = a.publish_date
            else:
                # set to current date
                self.date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        if not self.images:
            if a.top_image:
                self.images.append(a.top_image)

        article = Article(self.title,self.author,self.date,self.url,self.source,text.strip(),self.images)
        return article

    # scraper for CNN
    # all of these scraping functions are pretty similar, so I'm not commenting on the others unless there's a noticable difference (read the BeautifulSoup docs too)
    def cnn(self,soup):
        if "cnn.com/videos/" in self.url: # video link - no text to be scraped, DROPPED
            print("Rejected - CNN video link")
            return None

        if not self.author:
            a = soup.find(itemprop="author").get("content")
            if a:
                self.author = a
        
        if not self.date:
            d = soup.find(itemprop="datePublished").get("content")
            if d:
                self.date = convertDate(d,"%Y-%m-%dT%H:%M:%SZ")

        if not self.images:
            i = soup.find(itemprop="image").get("content")
            if i:
                self.images.append(i)

        text = ''
        paragraphs = soup.find_all(["div","p"],{"class":"zn-body__paragraph"}) # paragraphs are contained in <div> and <p> tags with the class 'zn-body__paragraph' - catch 'em all
        if paragraphs:
            for p in paragraphs: # loop through paragraphs and add each one to text string, separated by double new-line
                text += (p.text + '\n\n')
        
        if text == '': # scraping probably went wrong because no text, so return None
            print("Rejected - likely bad scraping job")
            return None
        else:
            article = Article(self.title,self.author,self.date,self.url,self.source,text.strip(),self.images)
            return article

    def nytimes(self,soup):
        if not self.author:
            a = soup.find("meta", {"name":"byl"})
            if a:
                self.author = ' '.join(a['content'].split()[1:])
            
        if not self.date:
            d = soup.find("meta",{"name":"pdate"})
            if d:
                self.date = convertDate(d['content'],"%Y%m%d")

        if not self.images:
            i = soup.find(itemprop="image").get("content")
            if i:
                self.images.append(i)

        text = ''
        paragraphs = soup.select("p.css-1xl4flh.e2kc3sl0")
        if paragraphs:
            for p in paragraphs:
                text += (p.text + '\n\n')
        
        if text == '':
            print("Rejected - likely bad scraping job")
            return None
        else:
            article = Article(self.title,self.author,self.date,self.url,self.source,text.strip(),self.images)
            return article

    def latimes(self,soup):
        if not self.author:
            a = soup.find("meta", {"name":"author"})
            if a:
                if a['content'].strip() == '':
                    self.author = "Unknown Author"
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
            print("Rejected - likely bad scraping job")
            return None
        else:
            article = Article(self.title,self.author,self.date,self.url,self.source,text.strip(),self.images)
            return article
            
    def jdsupra(self,soup):
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
            print("Text is empty - likely bad scraping job")
            return None
        else:
            article = Article(self.title,self.author,self.date,self.url,self.source,text.strip(),self.images)
            return article


'''def main():
    ssl._create_default_https_context = ssl._create_unverified_context # monkey patch for getting past SSL errors (this might be a system-specific issue)
    cnn = Scraper("https://www.cnn.com/2018/10/08/politics/cnn-poll-kavanaugh-confirmation/index.html","CNN Poll: Majority oppose Kavanaugh, but his popularity grows with GOP",None,None,[])
    a = cnn.scrape()
    if a:
        a.printInfo()


main()'''

'''# tests for scraper - delete this once we're golden       
def main():
    ssl._create_default_https_context = ssl._create_unverified_context # monkey patch for getting past SSL errors (this might be a system-specific issue)

    lat = Scraper("http://www.latimes.com/local/lanow/la-me-san-diego-pension-supreme-court-20181011-story.html","San Diego will appeal costly pension ruling to U.S. Supreme Court, citing former mayor's free-speech rights",None,None,[])
    cnn = Scraper("https://www.cnn.com/2018/10/12/politics/north-dakota-voter-id-native-americans/index.html","A voter ID decision could impact Native Americans -- and the Senate race -- in North Dakota",None,None,[])
    nyt = Scraper("https://www.nytimes.com/2018/10/11/opinion/should-supreme-court-matter.html?rref=collection%2Ftimestopic%2FU.S.%20Supreme%20Court","Should the Supreme Court Matter So Much?",None,None,[])
    jd = Scraper("https://www.jdsupra.com/legalnews/the-supreme-court-march-5-2018-61650/","The Supreme Court - March 5, 2018",None,None,[])
    slate_genericTest = Scraper("https://slate.com/news-and-politics/2018/10/west-virginia-supreme-court-impeachment-constitutional-crisis.html","West Virginia’s Absurd, Dangerous Supreme Court Impeachment Crisis",None,None,[])
    pages = [lat,cnn,nyt,jd,slate_genericTest]
    for page in pages:
        article = page.scrape()
        if article:
            print(article.title)
            print(article.author)
            print(article.date)
            print(article.images)
            print()
            print(article.text)
            print("===========================")
main()'''