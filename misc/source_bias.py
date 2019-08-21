# this script collects source bias data and inserts into the "source_bias" table in the database
# ideally this should be run from time to time to keep source bias data fresh
# however, at the moment it does assume the source_bias table is empty and starts from scratch so you may want to delete the current entries
from tqdm import tqdm
from bs4 import BeautifulSoup
import MySQLdb
import MySQLdb.cursors
import requests
import ssl
import tldextract
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import re

# custom class to handle checking whether media bias fact check has loaded shares yet
class element_has_initialized(object):
    def __init__(self, selector):
      self.selector = selector
  
    def __call__(self, driver):
        try:
            element = driver.find_element_by_css_selector(self.selector)
        except Exception as e:
            return False
        if len(element.text.strip()) > 0: # if element's text is non-empty, continue
            return True
        else:
            return False

# download a webpage using BeautifulSoup
# returns soup object we can parse
def downloadPage(url):
    #user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14'
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'
    try:
        request = requests.get(url,headers={'User-Agent':user_agent})
        page = request.content
        soup = BeautifulSoup(page, 'lxml')
    except Exception as e: # couldn't download page
        print("Error at",url,":",e)
        soup = None
    return soup

# intialize Chrome webdriver for selenium use (not being used at the moment)
def initializeDriver():
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options, executable_path='/Users/ecole96/Desktop/iMac_Backup/Desktop/scotusapp/misc/chromedriver')
    return driver

# alternate download function for getting media bias fact check data (because the shares metric is generated client side via JS so we need Selenium)
def alt_downloadPage(url,driver,element_to_wait_on):
    try:
        driver.get(url)
        if element_to_wait_on:
            wait = WebDriverWait(driver, 30) # timeout in 30 seconds
            wait.until(element_has_initialized(element_to_wait_on)) # wait until element is not empty to continue
        page = driver.page_source
        soup = BeautifulSoup(page, 'lxml') 
    except Exception as e: # couldn't download page
        print("Error at",url,":",e)
        soup = downloadPage(url)
    return soup

# download a webpage using BeautifulSoup
# returns soup object we can parse
def downloadPage(url):
    #user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14'
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'
    try:
        request = requests.get(url,headers={'User-Agent':user_agent})
        page = request.content
        soup = BeautifulSoup(page, 'lxml')
    except Exception as e: # couldn't download page
        print("Error at",url,":",e)
        soup = None
    return soup

# identical to getSource() in articleCollector - gets url domain name so we can match it up with sources in the database
def getDomain(url):
    ext = tldextract.extract(url)
    source = ext.domain
    return source

# class for gathering AllSides bias data
class AllSides:
    json_url = "http://www.allsides.com/download/allsides_data.json"

    def allsides(self,c):
        json = self.downloadJSON()
        if json:
            self.getData(json,c)

    # download up-to-date JSON of AllSides data from their website
    def downloadJSON(self):
        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'
        try:
            request = requests.get(self.json_url,headers={'User-Agent':user_agent})
            json = request.json()
        except Exception as e: # couldn't download page
            print("Error at",url,":",e)
            json = None
        return json

    def getData(self,json,c):
        bias = {71:"Left",72:"Center-Left",73:"Center",74:"Center-Right",75:"Right",2707:"Mixed"} # map bias number in JSON to categorical classification
        for j in tqdm(iterable=json,desc="AllSides Ratings"):
            row = {"source_name":None,"source":None,"bias":None,"confidence":None,"community_agree":None,"community_disagree":None, "allsides_id":None}
            bias_category = int(j["bias_rating"])
            if bias_category != 2690: # 2690 indicates a source that has not been rated yet
                row["source_name"] = j["news_source"]
                row["source"] = getDomain(j["url"])
                row["bias"] = bias[bias_category]
                 # because there's multiple instances of the same source (main site, editorials, certain authors, etc.), we want the id of the allsides page (taken from url)
                allsides_id = re.findall(r'\d+', j["allsides_url"])
                if allsides_id: row["allsides_id"] = int(allsides_id[0])
                self.scrape_allsides(j["allsides_url"],row)
                t = tuple(list(row.values()))
                # insert AllSides data into database (mbfs data in row will be null until that data is scraped later)
                c.execute("""INSERT INTO source_bias(source_name, source, allsides_bias, allsides_confidence, allsides_agree, allsides_disagree, allsides_id) VALUES (%s,%s,%s,%s,%s,%s,%s)""",t)

    # unfortunately the JSON doesn't have all the data we want so we still have to scrape a little more (community agreement / confidence data)
    def scrape_allsides(self,url,row):
        soup = downloadPage(url)
        if soup:
            community_agree = soup.select_one("span.agree")
            if community_agree: row['community_agree'] = int(community_agree.text.strip())
            community_disagree = soup.select_one("span.disagree")
            if community_disagree: row['community_disagree'] = int(community_disagree.text.strip())
            confidence = soup.select_one("div.confidence-level div.span8")
            if confidence: row['confidence'] = confidence.text.strip()

# class for Media Bias Fact Check scraping
class MBFS:
    baseURL = "https://mediabiasfactcheck.com/"

    def mbfs(self,c):
        #driver = initializeDriver()
        driver = None
        labels = {"left":"Left","leftcenter":"Center-Left","center":"Center","right-center":"Center-Right","right":"Right","fake-news":"Questionable Source"}
        for l in labels:
            url = self.baseURL + l + "/"
            source_urls = self.getSources(url)
            bias = labels[l]
            for url in tqdm(iterable=source_urls,desc=bias):
                data = self.getData(url,bias,driver)
                if data: self.addToDatabase(data,c)
        #driver.quit()

    # get source page URLs from category list pages
    def getSources(self,url):
        urls = []
        soup = downloadPage(url)
        if soup:
            rows = soup.select("td > a")
            urls = [r['href'] for r in rows]
        return urls

    # primary MBFS scraper
    def getData(self,url,bias,driver):
        data = {'source_name':None,'source':None,'bias':None,'bias_score':None,'shares':None}
        #soup = alt_downloadPage(url,driver,"span.a2a_count")
        soup = downloadPage(url)
        if soup:
            try:
                data['source_name'] = soup.select_one("h1.page-title").text.strip()
                if data['source_name'] == "Page not found (404)":
                    data = {}
                    return data
                source = None
                for p in soup.select("div.entry p"):
                    a = p.select_one("a")
                    text = p.text.lower().strip()
                    if a and text.startswith("source:"):
                        url = a['href']
                        source = getDomain(url)
                        data['source'] = source
                        break
                shares = soup.select_one("span.a2a_count") # this has to be collected via client side scraping, but this isn't working yet (if at all)
                if shares:
                    data['shares'] = int(shares.text.strip().replace(',',''))
                img = soup.select_one("div.entry img")
                if img and img['data-image-title'] and any(category in img['data-image-title'] for category in ['extremeleft','leftcenter','left','leastbiased','rightcenter','extremeright','right']):
                    img_title = img['data-image-title']
                    data['bias'] = self.deriveBiasFromImage(bias,img_title)
                    data['bias_score'] = self.bias_score(img_title)
                if data['bias'] is None:
                    data = {}
            except Exception as e:
                print(e)
        return data

    # MBFS rates sources on a spectrum from Extreme Left to Extreme Right - because AllSides only goes from Left to Right (no extremes), we need to standardize this data
    # On the category pages, some sources are mislabeled + the Questionable Sources category consists of many of the "Extreme" sources (but we don't know this until we visit the source page because until then it's only labeled as a Questionable Source)
    # To confirm the source's rating and standardize it, we check the image name associated with the bias range image on the source's page
    def deriveBiasFromImage(self,oldbias,img_title):
        categories = {'extremeleft':'Left','left':'Left','leftcenter':'Center-Left','leastbiased':'Center','rightcenter':'Center-Right','right':'Right','extremeright':'Right'}
        regex = re.findall(r'[a-z]+', img_title) # take only image name (not number)
        if regex: 
            bias = categories[regex[0]]
            if oldbias == 'Questionable Source': # if a Questionable Source, add that disclaimer
                bias += ' (Questionable Source)'
        else:
            bias = oldbias
        return bias

    # MBFS rates their sources on an arrow scale from Extreme Left to Right
    # each rating (a spot on the scale) is indicated by an image of the arrow scale and specific spot where that source is located. 
    # The image is named based on its spot on the scale (example: extremeleft01 is the farthest left you can go, and extremeright01 is the farthest right you can go)
    # Ranges of images: extremeleft [1,6], left [1,12], leftcenter [1,11], leastbiased [1,10], rightcenter [1,12], right [1,11], extremeright [1,6]
    # this function converts this system into a numerical scale ranging from -1 (most liberal) to 1 (most conservative)
    # honestly, MBFS's rating system is a little sketchy (midpoint is not directly in the middle of the overall scale, categories are not evenly divided, etc.) and this code seems ugly to me but it does seem to work
    def bias_score(self,img_title):
        score = None
        match = re.match(r"([a-z]+)([0-9]+)",img_title, re.I) # split image title into categorical and numerical portion
        if match:
            items = match.groups()
            category = items[0]
            n = int(items[1]) # initial value is the score within the source's category (ex: right06 = 6)
            # all of the "right" images are numbered from right to left (i.e right01 is farther from the center than right11) so we have to "reverse" the score so to speak to convert it into a "higher" = "righter" scale
            values = {'extremeleft':(n,6),'left':(n,12),'leftcenter':(n,11),'leastbiased':(n,10),'rightcenter':(-1*n+13,12),'right':(-1*n+12,11),'extremeright':(-1*n+7,6)}
            score = values[category][0] - 1 # scale starts at 0 for fractional purposes so subtract one
            for v in values: # add all category totals below the source's category + the category value
                if v == category:
                    break
                else:
                    score += values[v][1]
            midpoint = 35 # score is based on the distance from the "middle" of the scale (leastbiased07)
            if score <= midpoint: # under midpoint (left-leaning)
                start = 0
                distance_to_midpoint = midpoint - start
                if score != midpoint:
                    score  = -1 * (1 - ((score/distance_to_midpoint)))
                else:
                    score = (1 - ((score/distance_to_midpoint)))
            else: # above midpoint (right-leaning)
                end = 67
                distance_to_midpoint = end - midpoint
                score = ((score-midpoint)/distance_to_midpoint)
            score = round(score,3)
        return score

    # inserting MBFS into database
    def addToDatabase(self,data,c):
        # because we already have scraped AllSides data, check if the sources already exists in the database with AllSides data
        # if multiple rows have the same source, pick the one with the lowest allsides id (from what I can tell, the lowest is always the actual source rather than the editorials or a specific author)
        c.execute("""SELECT idSource FROM source_bias WHERE source = %s ORDER BY allsides_id LIMIT 1""",(data["source"],)) 
        if c.rowcount == 0: # source not in database, insert new row
            t = tuple(list(data.values()))
            c.execute("""INSERT INTO source_bias(source_name,source,mbfs_bias,mbfs_score,mbfs_shares) VALUES (%s,%s,%s,%s,%s)""",t)
        else: # source in database with AllSides data
            idSource = c.fetchone()['idSource']
            t = (data["bias"],data["bias_score"],data["shares"],idSource)
            c.execute("""UPDATE source_bias SET mbfs_bias=%s, mbfs_score=%s, mbfs_shares=%s WHERE idSource = %s""",t)

def main():
    ssl._create_default_https_context = ssl._create_unverified_context # monkey patch for getting past SSL errors (this might be a system-specific issue)

    db = MySQLdb.connect(host=os.environ['DB_HOST'],port=int(os.environ['DB_PORT']),user=os.environ['DB_USER'],password=os.environ['DB_PASSWORD'],db="SupremeCourtApp",use_unicode=True,charset="utf8")
    db.autocommit(True)
    c = db.cursor(MySQLdb.cursors.DictCursor)

    AllSides().allsides(c)
    MBFS().mbfs(c)
main()