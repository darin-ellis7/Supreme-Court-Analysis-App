# CS499 Spring 2018 Supreme Court Application John Tompkins, Jonathan Dingess, Mauricio Sanchez
#News API library. Queries from the newsAPI
from newsapi import NewsApiClient
from math import ceil

# fetches urls from NewsAPI of Latest and Most relevant articles regarding supreme court
def getLatestNewsAPI():
    articles = []
    newsapi = NewsApiClient(api_key='43fe19e9160d4a178e862c796a06aea8')
    newsAPIResult = newsapi.get_everything(q='United States Supreme Court', language='en', page_size=100, sort_by='relevancy')
    #add articles to list of urls
    for headline in newsAPIResult['articles']:
        articles.append(headline['url'])
    #loop through and request remaining pages
    for i in range(2, 6):
        newsAPIResult = newsapi.get_everything(q='United States Supreme Court', language='en', page=i, page_size=100, sort_by='relevancy')
        for headline in newsAPIResult['articles']:
            articles.append(headline['url'])

    return articles
