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