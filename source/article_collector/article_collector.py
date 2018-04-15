# CS499 Fall 2018 Supreme Court Application John Tompkins, Jonathan Dingess, Mauricio Sanchez. Modified from Fall 2017 Supreme Court Coverage/Analytics Application - Evan Cole, Darin Ellis, Connor Martin, Abdullah Alosail
#Article collection script - ideally, this should be scheduled to run on the hosting server periodically in order to collect new articles
# Data is collected by checking and parsing two custom RSS feeds we have 
# To-do: perhaps refine the relevancy check a little more
# TODO: Fix image downloading to download more images
# Known defects: 
        # Only one image (if there) is added to database per article - this isn't a "defect" per se, more a limitation - Newspaper can scrape all the images from an article but it often results in multiple irrelevant or duplicate images - we take the article's top image, which is usually the headline image and generally the one we want (and reasonably speaking, most articles won't have more than a headline image)

# ==============================================================
# DEPENDENCIES

# libraries that need to be downloaded (preferably using pip)
from feedparser import *
from newspaper import *
import siteScraperFunctions as scraper
import newsAPI as newsAPIClient
import MySQLdb
import MySQLdb.cursors
import tldextract
from PIL import Image
from google.cloud import vision
from google.cloud.vision import types
import io

from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types

# libraries that should be built into Python (don't need to be downloaded)
from sys import argv
from urllib import parse as urlparse
import re
import html
import ssl

# ==============================================================
# STUFF TO MAKE THIS SCRIPT WORK

# other than knowing it has to do with SSL certifications, I have no idea what this is or what it does but it makes this script work on Python 3.6
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

# set user header for image requests (cuts down on 403 errors)
opener=urllib.request.build_opener()
opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
urllib.request.install_opener(opener)

# ==============================================================
# FEED PARSING FUNCTIONS

# Links in the RSS feed are generated by google, and the actual URL of the article is stored as the 'url' parameter in this link
# this function gets us the actual URL
def getURL(RSS_url):
    parsed = urlparse.urlparse(RSS_url)
    url = urlparse.parse_qs(parsed.query)['url'][0]
    return url

# 'Supreme Court' appears in the titles of the RSS feed with bold tags around them
# this function strips the HTML and returns a text-only version of the title
def cleanTitle(original_title):
    cleanr = re.compile('<.*?>')
    cleanTitle = html.unescape(re.sub(cleanr, '', original_title))
    return cleanTitle

# original date is a long date/time string
# for our purposes, we really only need date, not time - so this function extracts the date and converts it into a year/month/day format (how MySQL stores dates)
def convertDate(orig_date):
    convertedDate = datetime.datetime.strptime(orig_date,"%Y-%m-%dT%H:%M:%SZ").strftime('%Y-%m-%d')
    return convertedDate

# parses URL to get the domain name of each article's link - the source
# one defect in handling the source is that, as of now, we don't know how to handle multiple-word sources beyond just storing it all as one string (so Fox News would just be stored as foxnews)
def getSource(url):
    ext = tldextract.extract(url)
    source = ext.domain
    return source

# ==============================================================
# IMAGE FUNCTIONS

# inserts an article's headline image into the database
def addImage(image_url,idArticle,c):
    # insert preliminary image entry (no image yet)
    c.execute("""INSERT INTO image(idArticle, url) VALUES (%s,%s)""",(idArticle, image_url))
    idImage = c.lastrowid
    imageDownloaded = download_image(image_url,idImage)

    # if image is successfully downloaded, update prelim entry to a permanent entry with image included
    if imageDownloaded != None:
        path = imageDownloaded
        c.execute("""UPDATE image SET path = (%s) WHERE idArticle = (%s) AND idImage = (%s)""",(path, idArticle,idImage))
        analyzeImage(path,idImage,c) # do image analysis
        print("Image successfully downloaded & analyzed")

    else:
        # if file can't be downloaded, delete prelim entry
        c.execute("""DELETE FROM image WHERE idImage = (%s)""",(idImage, ))
        print('Image couldn\'t be downloaded')

# goes to image url and downloads the image (unless it doesn't)
# if image is downloaded, the image filename (formatted as id{idImage}.jpg) is returned
# if error occurs during download, return None
def download_image(url,idImage):
    try:
        path = "./images/" # for this to work the images folder must be in the same directory as this script
        filename = "id" + str(idImage) + ".jpg" # image file is named according to its idImage in the database
        full = path + filename
        urllib.request.urlretrieve(url,full) # save image as a jpg even if it isn't (this probably isn't ideal but it seems to work) 
        im = Image.open(full)
        im.convert('RGB').save(full,"JPEG",quality=85,optimize=True) # then convert the image to an actual jpg
        return filename
    except (urllib.error.HTTPError, OSError) as error: # check if any errors occur (problem retrieving image or OSError) - the OSError has only occurred once, doesn't seem to be frequent, not sure why it happened but it's handled
        print(error)
        return None

# uses Google Cloud Vision API to detect entities in the image
# should get entity descriptions and their respective score (higher = more likely to be relevant to the image)
def analyzeImage(filename,idImage,c):
    client = vision.ImageAnnotatorClient() # start API

    # read image and detect web entities on the image
    path = "./images/" + filename
    with io.open(path,'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)
    web_detection = client.web_detection(image=image).web_detection

    # if there are entities, do the appropriate databases inserts one-by-one (this process is very similar to the one done with article keywords)
    if web_detection.web_entities:
        for entity in web_detection.web_entities:
            # check whether entity is already in database - if not, insert it
            if not EntityIsDuplicate(entity.description,c):
                c.execute("""INSERT INTO image_entities(entity) VALUES (%s)""", (entity.description,))

            # connect entity to image by inserting entity_instances entry
            c.execute("""SELECT idEntity FROM image_entities WHERE entity = %s""",(entity.description,))
            row = c.fetchone()
            idEntity = row['idEntity']
            c.execute("""INSERT INTO entity_instances(idEntity,score,idImage) VALUES (%s,%s,%s)""",(idEntity,entity.score,idImage))

# checks whether a specific image entity is already in the database
def EntityIsDuplicate(entity, c):
    c.execute("""SELECT * FROM image_entities WHERE entity = %s""",(entity,))
    if c.rowcount == 0:
        return False
    else:
        return True

# a sort of "relevancy" check for article images, since publication logos often show up if an article does not have any images
# checks image link against list of known logo links, or strings that most likely give away that an image is a logo
def isLogo(image):
    image = image.lower()
    knownLogos = ['https://s4.reutersmedia.net/resources_v2/images/rcom-default.png','https://www.usnews.com/static/images/favicon.ico'] # usnews and reuters often pop up in the feed, sometimes with these default image links (so we can filter them out)

    if image in knownLogos or '.ico' in image or 'favicon' in image or 'default' in image or 'logo' in image: # .ico and favicon are terms usually associated with site icons, and chances are that a link with "default" in it is a generic site image
        return True
    else:
        return False

# ==============================================================
# ARTICLE FUNCTIONS

# uses Google Natural Language API to analyze article text, returning an overall sentiment score and its magnitude
# sentiment scores correspond to the "emotional leaning of the text" according to Google - scores above 0 are considered positive sentiment, below are negative
# magnitude is the "strength" of the sentiment
def analyzeText(text):
    client = language.LanguageServiceClient() # initialize API
    document = language.types.Document(content=text,type=enums.Document.Type.PLAIN_TEXT)
    annotations = client.analyze_sentiment(document=document) # call to analyze sentiment

    # get necessary values
    score = annotations.document_sentiment.score
    magnitude = annotations.document_sentiment.magnitude
    return score, magnitude

# Newspaper library can get grab keywords from articles in conjunction with the nltk (natural language toolkit) library
# this function prepares the article for language processing and returns an array of keywords from the article
def getKeywords(article):
    article.nlp()
    return article.keywords

# inserts keywords from the Article keyword array into the database one-by-one 
def addKeywords(keywords,idArticle,c):
    # if keyword is a first occurrence, insert it into article_keywords
    for key in keywords:
        if not KeywordIsDuplicate(key,c):
            c.execute("""INSERT INTO article_keywords(keyword) VALUES (%s)""",(key,))

        # connect the keyword to an article by inserting a keyword_instances entry    
        c.execute("""SELECT idKey FROM article_keywords WHERE keyword = %s""",(key,))
        row = c.fetchone()
        idKey = row['idKey']
        c.execute("""INSERT INTO keyword_instances(idArticle,idKey) VALUES (%s,%s)""",(idArticle,idKey))

# checks whether a keyword is already in the database
# same implementation as the article check, just specific to keywords
def KeywordIsDuplicate(key, c):
    c.execute("""SELECT * FROM article_keywords WHERE keyword = %s""",(key,))
    if c.rowcount == 0:
        return False
    else:
        return True

# wrapper function
# adds all of an article's information to the database
def addToDatabase(url,source,author,date,text,title,keywords,image,c):
    score, magnitude = analyzeText(text) # do text analysis

    # insert new Article row
    t = (url, source, author, date, text, title, score, magnitude)
    c.execute(
        """INSERT INTO article(url, source, author, date, article_text, title, score, magnitude)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",t)

    # then insert the other stuff (keywords and images)
    idArticle = c.lastrowid
    addKeywords(keywords,idArticle,c)
    if image != None:
        addImage(image,idArticle,c)

    # finally, insert a success into statistics
    # Check if statistics exist for this date and source already:
    c.execute("""SELECT * FROM source_statistics WHERE source = %s AND date = %s""",(source, datetime.date.today()))
    if c.rowcount == 0:
        #TODO: Insert new row into source_statistics
        pass
    else:
        #TODO: Increment successed attribute of selection
        pass

# checks whether the title of an article is already in the database, avoiding duplicates
# we only check for title because the likeliness of identical titles is crazy low, and it cuts down on reposts from other sites
def ArticleIsDuplicate(title,c):
    c.execute("""SELECT * FROM article WHERE title = %s""",(title,))
    if c.rowcount == 0:
        return False
    else:
        return True

# determines whether article is behind a paywall, since such sites often don't give the full article text (or none at all)
# honestly there's not much of an automatic way to do this - known paywalled sources should be added to this list (though some like NYTimes seem to give full content)
def hasPaywall(source):
    knownPaywalls = ['law360','law'] 
    if source in knownPaywalls:
        return True
    else:
        return False

# barebones check for relevancy because local and international news are starting to creep into the database
# seems to get pretty good results (it's quite selective)
def relevant(keywords, title,source):
    # set everything to lowercase to standardize for checking
    title = title.lower()

    # these are sources that seem to pop up often about the SC in India - kill anything from these websites
    avoidedSources = ['indiatimes','thehindu','liberianobserver']

    # foreign supreme courts that appear most frequently
    foreignCountries = ['india','kenya','canada','spain']

    # use these lists of states & abbreviations to filter out state supreme courts
    states = ["Alabama","Alaska","Arizona","Arkansas","California","Colorado",
              "Connecticut","Delaware","Florida","Georgia","Hawaii","Idaho","Illinois",
              "Indiana","Iowa","Kansas","Kentucky","Louisiana","Maine","Maryland",
              "Massachusetts","Michigan","Minnesota","Mississippi","Missouri","Montana",
              "Nebraska","Nevada","New Hampshire","New Jersey","New Mexico","New York",
              "North Carolina","North Dakota","Ohio","Oklahoma","Oregon","Pennsylvania",
              "Rhode Island","South Carolina","South Dakota","Tennessee","Texas","Utah",
              "Vermont","Virginia","Washington","West Virginia","Wisconsin","Wyoming"]

    stateAbbreviations = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", 
                          "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
                          "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
                          "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
                          "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]

    # these are giveaways that an article is relevant
    if 'us supreme court' in title or 'u.s. supreme court' in title or 'scotus' in title:
        return True

    # article needs supreme and court as keywords
    if 'supreme' not in keywords or 'court' not in keywords:
        return False

    # drop any article that relates to an avoided source or foreign country (most likely about foreign supreme courts)
    if source.lower() in avoidedSources:
        return False

    for country in foreignCountries:
        if country in title or country in keywords:
            return False

    # check if the string "[state] Supreme Court" is in the title ([state] can be the word "state", a state name, or a state abbreviation) - this is generally a give away that this is a local Supreme Court
    if 'supreme court' in title:
        if 'state supreme court' in title:
            return False

        for state in states:
            if state.lower() + ' supreme court' in title:
                return False

        for abv in stateAbbreviations:
            if abv.lower() + ' supreme court' in title:
                split = title.split()
                if abv.lower() in split:
                    return False

    return True

# ==============================================================
# DRIVER FUNCTIONS

# goes through each entry in a given feed, check it for relevancy, and if relevant, add it to the database
# if we can't get the data from the website (403/404 errors, whatever) - an exception occurs, and we move to the next article
def parseFeed(RSS,c):
    # config info for Newspaper - keep article html for user-friendly display, set browser user agent to a desktop computer header to help fight 403 errors
    config = Config()
    config.keep_article_html = False
    config.browser_user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9'

    # begin parsing
    feed = parse(RSS)
    total = len(feed.entries)
    successes = 0
    for post in feed.entries:
        url = getURL(post['link'])
        title = cleanTitle(post['title'])
        date = convertDate(post['date'])
        source = getSource(url)

        print('URL:',url)
        print('Title:',title)
        print('Source:',source)

        # check for duplicates - otherwise, add to database
        if ArticleIsDuplicate(title,c):
            print("Rejected - already in database")
        else: 
            a = Article(url,config) # use Newspaper to grab article text + info
            try:
                a.download()
                a.parse()

                # since tiny articles are generally useless, we check for length here
                # this also helps us weed out paywalls, snippets, maybe even some local news sources
                text = a.text
                if len(text) > 500:
                    if(len(a.authors) > 0):
                        author = a.authors[0]
                    else:
                        author = 'Unknown'

                    keywords = getKeywords(a)
                    if a.top_image == '':
                        image = None
                    else:
                        image = a.top_image
                        if isLogo(image):
                            print('Image rejected - most likely a logo')
                            image = None

                    if hasPaywall(source):
                        print('Article rejected - source known to have a paywall')
                    else:
                        if not relevant(keywords,title,source):
                            print('Article rejected - deemed irrelevant')
                        else:
                            addToDatabase(url,source,author,date,text,title,keywords,image,c)
                            successes += 1
                            print('Article successfully analyzed & added to database')                        
                else:
                    print('Article rejected - too short')

            except ArticleException: # article couldn't download (throw this message and move on)
                print('Rejected - couldn\'t download article ')
        print()


    print(successes,"/",total,"articles added to database.")
    print('=======================================================')

#CS499s2018 this whole function
#Processes URLs returned by scraper functions
#Doesn't check for relevancy because every URL from a scraper function is assumed relevant.
def parseURL(URL, c, checkRelevancy=False):
    #config (see above in parseFeed)
    config = Config()
    config.keep_article_html = False
    config.browser_user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9'

    print('URL:', URL)

    a = Article(URL, config) #Use newspaper to grab article
    try:
        a.download()
        a.parse()

        title = a.title
        source = getSource(URL)
        date = a.publish_date

        #need date to save to database. if date not present, save as today's date
        if date is None:
            date = datetime.date.today()
        print('Title:', title)
        print('Source:', source)
        
        #Check for duplicate using title
        if ArticleIsDuplicate(title, c):
            print("Rejected - already in database")
        else:
            
            #exclude small articles (See justification above in ParseFeed)
            text = a.text
            if len(text) < 500:
                #TODO: Add Statistics
                print("Rejected - article too short")
            else:
                if(len(a.authors) > 0):
                    author = a.authors[0]
                else:
                    author = 'Unknown'
                
                keywords = getKeywords(a)
                if a.top_image == '':
                    image = None
                else:
                    image = a.top_image
                    if isLogo(image):
                        print('Image rejected - most likely a logo')
                        image = None

                if hasPaywall(source):
                    print('Article rejected - source known to have a paywall')
                else:
                    if checkRelevancy and not relevant(keywords, title, source):
                        #TODO: Add statistics
                        print('Article rejected - deemed irrelevant')
                    else:
                        addToDatabase(URL,source,author,date,text,title,keywords,image,c)
                        print('Article successfully analyzed & added to database')
                
    except:
        print('Rejected - couldn\'t download article')

def main():
    
    # connect to database
    db = MySQLdb.connect(host="127.0.0.1",port=3306,user="root",password="cs499",db="SupremeCourtApp",use_unicode=True,charset="utf8")
    db.autocommit(True)
    c = db.cursor(MySQLdb.cursors.DictCursor)

    if (len(argv) == 1):

        # Google Alert custom feed links
        feeds = ['https://www.google.com/alerts/feeds/16607645132923191819/10371748129965602805', 'https://www.google.com/alerts/feeds/16607645132923191819/14723000309727640285', 'https://www.google.com/alerts/feeds/16607645132923191819/1276985364450614174', 'https://www.google.com/alerts/feeds/16607645132923191819/1276985364450612172']
        i = 1 # counter to show which feed is being scanned
        for feed in feeds:
            print("RSS Feed " + str(i))
            print()
            parseFeed(feed,c)
            i += 1

    #CS499s2018 from here down has been added
        #Scrape articles from trusted news sections
        scrapedURLs = scraper.scrapeAll()

        #Sift through articles; Do not check relevancy because from trusted sources
        for url in scrapedURLs:
            parseURL(url,c, False)

        #get newsAPI articles
        newsAPIURLs = newsAPIClient.getLatestNewsAPI()

        #Sift through NewsAPI; Do check relevancy
        for url in newsAPIURLs:
            parseURL(url, c, True)

    
    else:
        for url in argv[1:]:
            parseURL(url, c, True)
    

    #Cleanup
    c.close()
    db.close()


main()
# *** END OF SCRIPT ***
