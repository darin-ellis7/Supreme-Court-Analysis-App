import newspaper
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from Image import Image
import math
import datetime

# class for article
# needs to add database/image/analysis functions
class Article:
    def __init__(self,title,author,date,url,source,text,imageURLs):
        if title:
            self.title = title
        else:
            self.title = "Untitled"

        if author:
            self.author = author
        else:
            self.author = "Unknown Author"

        if date:
            self.date = date
        else:
            # set to current date
            self.date = datetime.datetime.now().strftime("%Y-%m-%d")

        self.url = url
        self.source = source
        self.text = text
        self.keywords = self.getKeywords()
        self.sentimentScore = None
        self.magnitude = None
        self.images = []
        for imageURL in imageURLs:
            image = Image(imageURL)
            self.images.append(image)

    # prints Article info to script output
    # title and URL are located in printBasicInfo() in UtilityFunctions.py, because we need to check those before we ever create an Article object
    def printInfo(self):
        print("Author:",self.author)
        print("Date:",self.date)
        print("Keywords:",self.keywords)
        print("Number of characters:",len(self.text))

    # prints analysis data to script output
    def printAnalysisData(self):
        if self.sentimentScore is not None and self.magnitude is not None:
            print("Sentiment Score & Magnitude:",str(round(self.sentimentScore,3)) + ",",round(self.magnitude,3))
            print()
        for index, image in enumerate(self.images):
            if image.filename:
                filestr = "Saved as " + image.filename
            else:
                filestr = "Not saved"
            
            if image.entities:
                entities = image.entities
            else:
                entities = "Not analyzed"
            print("* Image",str(index+1),"entities ( " + image.url + " / " + filestr + " ):",entities)

    # Newspaper library can get grab keywords from articles in conjunction with the nltk (natural language toolkit) library
    # this function prepares the article for language processing and returns an array of keywords from the article
    def getKeywords(self):
        # UGLY HACK WARNING
        # if a site has a specific scraper written for it, Newspaper is never involved - but Newspaper's keyword functionality is really good and I don't want to write my own function for it
        # so I'm creating a newspaper.Article object and forcibly setting attributes to allow the natural language processing to work and give me keywords
        a = newspaper.Article(self.url)
        a.text = self.text
        a.title = self.title
        a.download_state = 2 # nlp() function below uses direct comparisons to check for download state so I'm getting away with setting it to something arbitrary
        a.is_parsed = True
        a.nlp()
        return a.keywords

    # inserts keywords from the Article keyword array into the database one-by-one 
    def addKeywords(self,idArticle,c):
        # if keyword is a first occurrence, insert it into article_keywords
        for key in self.keywords:
            if not self.keywordIsDuplicate(key,c):
                c.execute("""INSERT INTO article_keywords(keyword) VALUES (%s)""",(key,))
                idKey = c.lastrowid
            else:
                c.execute("""SELECT idKey FROM article_keywords WHERE keyword = %s""",(key,))
                row = c.fetchone()
                idKey = row['idKey']
            c.execute("""INSERT INTO keyword_instances(idArticle,idKey) VALUES (%s,%s)""",(idArticle,idKey))

    # checks whether a keyword is already in the database
    # same implementation as the article check, just specific to keywords
    def keywordIsDuplicate(self,key, c):
        c.execute("""SELECT idKey FROM article_keywords WHERE keyword = %s""",(key,))
        if c.rowcount == 0:
            return False
        else:
            return True

    # uses Google Natural Language API to analyze article text, returning an overall sentiment score and its magnitude
    # sentiment scores correspond to the "emotional leaning of the text" according to Google - scores above 0 are considered positive sentiment, below are negative
    # magnitude is the "strength" of the sentiment
    def analyzeSentiment(self,c):
        # verify that sentiment analysis does not exceed 8000 call monthly limit
        c.execute("""SELECT * from analysisCap""")
        row = c.fetchone()
        currentSentimentRequests = row['currentSentimentRequests']
        expectedSentimentRequests = math.ceil(len(self.text) / 1000)
        if currentSentimentRequests + expectedSentimentRequests > 8000:
            print("Can't analyze sentiment score - API requests exceed limit of 8000")
        else:
            try:
                client = language.LanguageServiceClient() # initialize API
                document = language.types.Document(content=self.text,type=enums.Document.Type.PLAIN_TEXT)
                annotations = client.analyze_sentiment(document=document) # call to analyze sentiment
                # get necessary values
                self.sentimentScore = annotations.document_sentiment.score
                self.magnitude = annotations.document_sentiment.magnitude
                self.updateSentimentRequests(expectedSentimentRequests,c)
            except Exception as e:
                print("Sentiment analysis failed:",e)

    # adds all of an article's information to the database
    def addToDatabase(self,c):
        self.analyzeSentiment(c)
        # insert new Article row
        t = (self.url, self.source, self.author, self.date, self.text, self.title, self.sentimentScore, self.magnitude)
        c.execute("""INSERT INTO article(url, source, author, date, article_text, title, score, magnitude) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",t)

        # then insert the other stuff (keywords and images)
        idArticle = c.lastrowid # article id needed for keywords and images
        self.addKeywords(idArticle,c)
        self.addImages(idArticle,c)

    # driver function for downloading, saving, and analyzing each of an article's images
    def addImages(self,idArticle,c):
        for index, image in enumerate(self.images):
            if image.isLogo():
                print("Image at",image.url,"is likely a logo - it will not be downloaded or analyzed")
            else:
                imageDownloaded = image.downloadImage()
                if imageDownloaded:
                    # images are titled {idArticle}.jpg
                    filename = "id" + str(idArticle)
                    if index > 0: # but if an article has more than one image, any additional image is titled {idArticle-N}.jpg
                        filename += "-" + str(index + 1)
                    filename += ".jpg"
                    imageSaved = image.saveImage(filename)
                    if imageSaved:
                        image.analyzeImage(c)
                        image.addImageToDatabase(idArticle,c)
    
    # checks whether an article pertains to the US Supreme Court
    def isRelevant(self):
        # set everything to lowercase to standardize for checking
        title = self.title.lower()

        instantTerms = ["usa supreme court", "us supreme court", "u.s. supreme court", "united states supreme court", "scotus"] # dead giveaways for relevancy
        justices = ['john roberts', 'anthony kennedy', 'clarence thomas', 'ruth bader ginsburg', 'stephen breyer', 
        'samuel alito', 'sonia sotomayor', 'elena kagan', 'neil gorsuch', 'brett kavanaugh', 
        'roberts', 'kennedy', 'thomas', 'ginsburg', 'breyer', 'alito', 
        'sotomayor', 'kagan', 'gorsuch', 'kavanaugh'] # full names of justices, as well as their last names

        # check for the "dead giveaways"
        if any(term in title for term in (instantTerms + justices)): 
            return True

        # these are sources that seem to pop up often with articles about foreign supreme courts - kill anything from these websites
        foreignSources = ['indiatimes','thehindu','liberianobserver','allafrica']
        if self.source.lower() in foreignSources or ('india' in self.source.lower() and 'indiana' not in self.source.lower()): # indian supreme court pops ups a lot, so block any source with "india" in it ("indiana" still passes)
            print("Rejected - from a known foreign source")
            return False

        # list of every country in the world with a supreme court
        countries = [
                        'afghanistan', 'albania', 'algeria', 'andorra', 'angola', 'antigua and barbuda', 'argentina', 'armenia', 'australia', 'austria', 'azerbaijan', 'bahamas', 
                        'bahrain', 'bangladesh', 'barbados', 'belarus', 'belgium', 'belize', 'benin', 'bhutan', 'bolivia', 'bosnia and herzegovina', 'botswana', 'brazil', 'brunei', 
                        'bulgaria', 'burkina faso', 'burundi', 'cambodia', 'cameroon', 'canada', 'cape verde', 'central african republic', 'chad', 'chile', 'china', 'colombia', 
                        'comoros', 'congo-brazzaville', 'congo-kinshasa', 'costa rica', 'croatia', 'cuba', 'cyprus', 'czech republic', 'denmark', 'djibouti', 'dominica', 
                        'dominican republic', 'east timor', 'ecuador', 'egypt', 'el salvador', 'equatorial guinea', 'eritrea', 'estonia', 'ethiopia', 'fiji', 'finland', 'france', 'gabon', 'gambia', 
                        'georgia', 'germany', 'ghana', 'greece', 'grenada', 'guatemala', 'guinea-bissau', 'guinea-conakry', 'guyana', 'haiti', 'honduras', 'hungary', 'iceland', 'india', 'indonesia', 
                        'iran', 'iraq', 'ireland', 'israel', 'italy', 'ivory coast', 'jamaica', 'japan', 'jordan', 'kazakhstan', 'kenya', 'kiribati', 'kuwait', 'kyrgyzstan',
                        'laos', 'latvia', 'lebanon', 'lesotho', 'liberia', 'libya', 'liechtenstein', 'lithuania', 'luxembourg', 'macedonia', 'madagascar', 'malawi', 'malaysia', 'maldives', 'mali', 'malta', 
                        'marshall islands', 'mauritania', 'mauritius', 'mexico', 'micronesia', 'moldova', 'monaco', 'mongolia', 'montenegro', 'morocco', 'mozambique', 'myanmar', 'namibia', 'nauru', 'nepal', 
                        'netherlands', 'new zealand', 'nicaragua', 'niger', 'nigeria', 'north korea', 'norway', 'oman', 'pakistan', 'palau', 'palestine', 'panama', 'papua new guinea', 'paraguay', 'peru', 
                        'philippines', 'poland', 'portugal', 'qatar', 'romania', 'russia', 'rwanda', 'saint kitts and nevis', 'saint lucia', 'saint vincent and the grenadines', 
                        'samoa', 'san marino', 'são tomé and príncipe', 'saudi arabia', 'senegal', 'serbia', 'seychelles', 'sierra leone', 'singapore', 'slovakia', 'slovenia', 'solomon islands', 'somalia', 
                        'south africa', 'south korea', 'south sudan', 'spain', 'sri lanka', 'sudan', 'suriname', 'swaziland', 'sweden', 'switzerland', 'syria', 'tajikistan', 'tanzania', 'thailand', 'togo', 
                        'tonga', 'trinidad and tobago', 'tunisia', 'turkey', 'turkmenistan', 'tuvalu', 'uganda', 'ukraine', 'united arab emirates', 'united kingdom', 'uruguay', 'uzbekistan', 
                        'vanuatu', 'vatican city', 'venezuela', 'vietnam', 'yemen', 'zambia', 'zimbabwe'
                    ]

        if any(country + ' supreme court' in title or country + '\'s supreme court' in title for country in countries):
            return False

        # NOTE: this was the old way for checking for foreign supreme courts - it was really limited, only included a few countries and specific keywords.
        # Prone to false negatives so using the broader method above instead - perhaps could be tweaked at a later date
        '''
        # foreign supreme courts that appear most frequently
        foreignCountries = ['india','indian','kenya','kenyan','canada','canadian','spain','spanish','israel','israeli',"british","uk","u.k."]

        # drop any article that relates to an avoided source or foreign country (most likely about foreign supreme courts)
                                                                                                                            
        for country in foreignCountries:
            if country in title or country in keywords:
                return False'''

        # use these lists of states & abbreviations to filter out state supreme courts
        states = ['alabama', 'alaska', 'arizona', 'arkansas', 'california', 'colorado', 'connecticut', 'delaware', 'florida', 'georgia', 
            'hawaii', 'idaho', 'illinois', 'indiana', 'iowa', 'kansas', 'kentucky', 'louisiana', 'maine', 'maryland', 
            'massachusetts', 'michigan', 'minnesota', 'mississippi', 'missouri', 'montana', 'nebraska', 'nevada', 
            'new hampshire', 'new jersey', 'new mexico', 'new york', 'north carolina', 'north dakota', 'ohio', 'oklahoma', 
            'oregon', 'pennsylvania', 'rhode island', 'south carolina', 'south dakota', 'tennessee', 'texas', 'utah', 
            'vermont', 'virginia', 'washington', 'west virginia', 'wisconsin', 'wyoming']
        state_abvs = ['al', 'ak', 'az', 'ar', 'ca', 'co', 'ct', 'dc', 'de', 'fl', 'ga', 'hi', 'id', 'il', 'in', 'ia', 'ks', 'ky', 'la', 
            'me', 'md', 'ma', 'mi', 'mn', 'ms', 'mo', 'mt', 'ne', 'nv', 'nh', 'nj', 'nm', 'ny', 'nc', 'nd', 'oh', 'ok', 'or', 
            'pa', 'ri', 'sc', 'sd', 'tn', 'tx', 'ut', 'vt', 'va', 'wa', 'wv', 'wi', 'wy', 'wyo', 'ala', 'ariz']

        # check if the string "[state] Supreme Court" is in the title ([state] can be the word "state", a state name, or a state abbreviation) - this is generally a give away that this is a local Supreme Court
        if 'supreme court' in title:
            stateDetected = False
            if 'state supreme court' in title or any((state + ' supreme court' in title or state + '\'s supreme court' in title) for state in states): # also accounting for "[state's] supreme court" (ex: "kentucky's supreme court")
                stateDetected = True

            for abv in state_abvs:
                if (abv + ' supreme court') in title or (abv + '. supreme court') in title: # also accounting for "[abv.] supreme court" (ex: "ky. supreme court")
                    if abv in title.split():
                        stateDetected = True

            if stateDetected:
                print("Rejected - Article likely about a state supreme court")
                return False
        
        # article needs supreme and court as keywords, or a Supreme Court justice
        if not ('supreme' in self.keywords and 'court' in self.keywords) and not any(justice in self.keywords for justice in justices):
            print("Rejected - no relevant keywords in text")
            return False
        
        return True
    
    # increment sentiment requests counter in database
    def updateSentimentRequests(self,n,c):
        c.execute("""UPDATE analysisCap SET currentSentimentRequests=currentSentimentRequests+(%s)""",(n,))
