# Supreme Court Analysis App (SCAA)

SCAA is an academic tool designed to collect, store, and analyze online articles about the Supreme Court of the United States.
It has three major parts:

###The Scraper (/scraper/\*.py)

The Scraper is the part the does the bulk of the collection, storage, and analysis. It consists of a python script (broken into 
multiple files for clarity) that leverages three primary sources of articles: custom Google Alerts RSS feeds, News API, and topic sites
scrapers. These sources are described in more detail in the "scrapers" directory. Upon scraping and processing the article, the article
contents are stored into The Database.

###The Database (/scraper/SupremeCourt.sql)

The Database is where all the article content and analysis information is stored. Tied to this is a folder for images keyed to the id
of their associated articles.

###The Web App (/webapp)

The Web App is the collection of web pages that allows easy viewing and downloading of the articles stored in The Database. They
are written mostly in php, with some javascript.
