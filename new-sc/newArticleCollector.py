# this is functional now (though no database/analysis stuff yet)
# ==============================================================
# DEPENDENCIES
#import MySQLdb
#import MySQLdb.cursors
#from PIL import Image
#from google.cloud import vision
#from google.cloud.vision import types
#import io
#from google.cloud import language
#from google.cloud.language import enums
#from google.cloud.language import types
#from sys import argv

import ssl
from collectionSources import *

def main():
    ssl._create_default_https_context = ssl._create_unverified_context # monkey patch for getting past SSL errors (this might be a system-specific issue)
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14'

    # RSS feeds
    feed_urls = ['https://www.google.com/alerts/feeds/16607645132923191819/10371748129965602805', 'https://www.google.com/alerts/feeds/16607645132923191819/14723000309727640285', 'https://www.google.com/alerts/feeds/16607645132923191819/1276985364450614174', 'https://www.google.com/alerts/feeds/16607645132923191819/1276985364450612172']
    feeds = RSSFeeds(feed_urls)
    feeds.parseFeeds()

    # newsAPI results
    queries  = ["USA Supreme Court","US Supreme Court", "United States Supreme Court","SCOTUS"]
    newsapi = NewsAPICollection(queries)
    newsapi.parseResults()

    # topic sites
    t = TopicSites()
    t.collect()

main()
