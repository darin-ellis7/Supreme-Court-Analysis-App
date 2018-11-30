# Data collection script for the Supreme Court Coverage & Analytics Application, version 2.0, November 2018 - for the UK Political Science department, Drs. Zilis and Wedeking
# written by Evan Cole and Darin Ellis, with some past contributions from John Tompkins, Jonathan Dingess, and Alec Gilbert
# scrapes articles from Google Alerts RSS feeds, NewsAPI search results, and Supreme Court topic pages (from major news sources), analyzes them using the Google Cloud API, and stores them in a MySQL database
# Ideally, a cronjob should be set to run this script every few hours for continuous data collection

import ssl
from collectionSources import *
import MySQLdb
import MySQLdb.cursors
import os

def main():
    ssl._create_default_https_context = ssl._create_unverified_context # monkey patch for getting past SSL errors (this might be a system-specific issue)

    # database credentials need to be set as these environment variables
    db = MySQLdb.connect(host=os.environ['DB_HOST'],port=int(os.environ['DB_PORT']),user=os.environ['DB_USER'],password=os.environ['DB_PASSWORD'],db="SupremeCourtApp",use_unicode=True,charset="utf8")
    db.autocommit(True)
    c = db.cursor(MySQLdb.cursors.DictCursor)

    # check for new billing cycle before running
    try:
        if isNewBillingCycle(c):
            resetRequests(c)
            print("New billing cycle - sentiment requests reset")
            print()
    except MySQLdb.Error as e:
        print("Database error - ",e)
        print("Script aborted.")
        return

    # RSS feeds
    feed_urls = ['https://www.google.com/alerts/feeds/16607645132923191819/10371748129965602805', 'https://www.google.com/alerts/feeds/16607645132923191819/14723000309727640285', 'https://www.google.com/alerts/feeds/16607645132923191819/1276985364450614174', 'https://www.google.com/alerts/feeds/16607645132923191819/1276985364450612172']
    feeds = RSSFeeds(feed_urls)
    feeds.parseFeeds(c)

    # newsAPI results
    queries  = ["USA Supreme Court","US Supreme Court", "United States Supreme Court","SCOTUS"]
    newsapi = NewsAPICollection(queries)
    newsapi.parseResults(c)

    # topic sites
    t = TopicSites()
    t.collect(c)

main()
