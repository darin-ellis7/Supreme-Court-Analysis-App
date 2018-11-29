from scrapers import *
import MySQLdb
import MySQLdb.cursors
import os

# script to "clean up" the current database
# there are articles from certain sources that have been badly scraped in the past, by Newspaper or outdated scraper functions
# this script scrapes the correct text from these articles (assuming a specific scraper function has been written in scrapers.py)
# like mergeDB, also quick and dirty, but you probably could use this (though be careful)

def populate(c):
    c.execute("""SELECT idArticle,url,title,author,date,article_text FROM article WHERE source in ("cnn","nytimes","latimes","jdsupra")""")
    rows = c.fetchall()
    count = 0
    for index,r in enumerate(rows):
        #if index > 5:
            #break
    
        s = Scraper(r['url'],r['title'],None,r['date'],["placeholder.jpg"]) # don't want to mess with images so just setting a placeholder image so no images are attempted to be scraped
        article = s.scrape()

        idArticle = r['idArticle']
        print(idArticle,':',r['date'],"-",r['title'],"[",r['url'],"]")
        if article:
            oldAuthor = r['author']
            newAuthor = article.author
            oldCharCount = len(r['article_text'])
            newCharCount = len(article.text)

            # only "cleaning" articles where the full articles aren't scraped (meaning the character count in the db is less than the character count using current scraping methods)
            # or JDSUPRA articles that scraped the privacy policy instead
            # authors also cleaned too
            editsNeeded = (oldAuthor.lower() != newAuthor.lower()) or (oldCharCount < newCharCount) or article.source == "jdsupra" 
            if editsNeeded:
                if oldAuthor.lower() != newAuthor.lower():
                    c.execute("""UPDATE article SET author = (%s) WHERE idArticle = (%s)""",(newAuthor,idArticle,))
                    print("Author changed from",r['author'],'to',article.author)
                if oldCharCount < newCharCount or article.source == "jdsupra":
                    c.execute("""UPDATE article SET article_text = (%s) WHERE idArticle = (%s)""",(article.text,idArticle,))
                    print("Text re-scraped, old character count:",oldCharCount,"/ new character count:",newCharCount)
                    #print("=========================================")
                    #print()
                    #print(article.text)
                count += 1
            else:
                print("No edits")
        else:
            print("Bad scrape, no edits")
        print("=========================================")
    print(count,"articles edited")

def main():
    db = MySQLdb.connect(host=os.environ['DB_HOST'],port=int(os.environ['DB_PORT']),user=os.environ['DB_USER'],password=os.environ['DB_PASSWORD'],db="SupremeCourtApp",use_unicode=True,charset="utf8")
    c = db.cursor(MySQLdb.cursors.DictCursor)
    db.autocommit(True)
    populate(c)

main()