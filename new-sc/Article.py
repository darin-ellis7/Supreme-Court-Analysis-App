import newspaper

# class for article
# needs to add database/image/analysis functions
class Article:
    def __init__(self,title,author,date,url,source,text,images):
        self.title = title
        self.author = author
        self.date = date
        self.url = url
        self.source = source
        self.text = text
        self.images = images
        self.keywords = self.getKeywords()
    
    def printInfo(self):
        #print("Title:",self.title)
        #print("URL:",self.url,"(" + self.source.upper() + ")")
        print("Author:",self.author)
        print("Date:",self.date)
        print("Keywords:",self.keywords)
        print("Images:",self.images)
        print("Number of characters:",len(self.text))
        #print()
        #print(self.text)

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

    def isRelevant(self):
        # set everything to lowercase to standardize for checking
        title = self.title.lower()

        instantTerms = ["usa supreme court", "us supreme court", "u.s. supreme court", "united states supreme court", "scotus"] # dead giveaways for relevancy
        justices = ['john roberts', 'anthony kennedy', 'clarence thomas', 'ruth bader ginsburg', 'stephen breyer', 
        'samuel alito', 'sonia sotomayor', 'elena kagan', 'neil gorsuch', 'brett kavanaugh', 
        'roberts', 'kennedy', 'thomas', 'ginsburg', 'breyer', 'alito', 
        'sotomayor', 'kagan', 'gorsuch', 'kavanaugh'] # full names of justices, as well as their last names

        if any(term in title for term in (instantTerms + justices)): 
            return True

        # these are sources that seem to pop up often about the SC in India - kill anything from these websites
        avoidedSources = ['indiatimes','thehindu','liberianobserver']
        if self.source.lower() in avoidedSources:
            print("Rejected - from a known foreign source")
            return False

        # foreign supreme courts that appear most frequently
        '''foreignCountries = ['india','indian','kenya','kenyan','canada','canadian','spain','spanish','israel','israeli',"british","uk","u.k."]

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
            if 'state supreme court' in title or any(((state + ' supreme court') or (state + '\'s supreme court')) in title for state in states): # also accounting for "[state's] supreme court" (ex: "kentucky's supreme court")
                stateDetected = True

            for abv in state_abvs:
                if (abv + ' supreme court') in title or (abv + '. supreme court') in title: # also accounting for "[abv.] supreme court" (ex: "ky. supreme court")
                    if abv in title.split():
                        stateDetected = True

            if stateDetected:
                print("Rejected - Article likely about a state supreme court")
                return False
        
        # article needs supreme and court as keywords
        if not ('supreme' in self.keywords and 'court' in self.keywords) and not any(justice in self.keywords for justice in justices):
            print("Rejected - no relevant keywords in text")
            return False
        
        return True