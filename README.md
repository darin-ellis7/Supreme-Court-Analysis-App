# Supreme Court Coverage & Analysis Application (SCOTUSApp)

SCOTUSApp is an academic tool designed to collect, store, and analyze online articles about the Supreme Court of the United States.
It consists of three major parts:

### Article Collector Python Script (/articleCollector/)
The Article Collector does the bulk of the collection, storage, and analysis. It consists of a python script (broken into 
multiple files of classes and procedures) that leverages three primary sources of articles: custom Google Alerts RSS feeds, News API, and Supreme Court-specific news pages from various major news sources (referred to as Topic Sites). Upon scraping and processing these sources into article texts, metadata, and text sentiment and image analysis results, the information is stored in the MySqlDatabase

### SupremeCourtApp MySQL Database (/backups/)
The MySQL Database is where all the article content and analysis information is stored. This includes images relating to the articles - however, the actual images are not stored; rather, the filenames are (the actual images are located in the /images/ directory). The /backups/ directory is where any database dumps should go.

### PHP Web Application (/webapp/)
The Web Application is a collection of web pages that allow easy viewing and downloading of the articles stored in the database.


Here is a rundown of the other directories in this repo:

### Images (/images/)
As described above, this is where any scraped article images go. Up until recently, images were titled based on the Image ID in the database - now, they are titled based on the Article ID they belong to (older images have not been renamed).

### Documentation (/docs/)
A collection of text files and PDF manuals on how to run and manage the application. Basically, more detailed READMEs and developer notes.

### Install (/install/)
Files relating to the installation and maintenance of the application, such as credentials and backup/cronjob shell scripts. Most of the files in this directory aren't uploaded to Github, as they have sensitive information.

### Miscellaneous Scripts (/misc/)
Some scripts written during development to make some tasks easier, like merging two copies of the database together, or rescraping articles from the past that were previously scraped poorly. It's not recommended to run these as they were very one-time-use; they're better off to be rewritten and generalized at some point. If you do use them, be very careful.
