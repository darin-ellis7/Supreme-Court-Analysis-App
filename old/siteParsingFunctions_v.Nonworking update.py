#Last edited 9/7/2018

#Added Summer 2018 by Alec Gilbert
#These functions help parse websites that newspaper doesn't parse well.
#They are a little fragile in that they depend on the layout of that website
#staying the way it is.

from newspaper import *
import tldextract
import os
import io
from urllib import parse as urlparse
from bs4 import BeautifulSoup
from bs4 import Comment
import json
#import re #regular expressions
from collections import OrderedDict

#Grabs the html of the webpage and returns a BeautifulSoup Object for scraping tags
def grabPage(url):
    page = urllib.request.urlopen(url, cafile=certifi.where())
    try:
        soup = BeautifulSoup(page, 'html.parser')
        return soup
    #Sometimes will get 404 from HTTPs pages
    except Exception as e:
        print("Could not retrieve: " + url)
        return "<html></html>"


def parseLATimes(a):
    a.download()


    print(a.title)

    HTML=a.html

    soup = grabPage(HTML)

    jText = soup.find('script', type='application/ld+json').text

    extraPos= jText.find("// will be empty for branded publishing")
    jsonEndPos = jText.find("},",extraPos-20)
    jText = jText[:jsonEndPos+1]
    stuff = json.loads(jText)
    body = stuff["articleBody"]



    import html.parser
    h = html.parser.HTMLParser()
    body = h.unescape(body)
    body = h.unescape(body) # It took me a long time to figure out I needed to use this twice!
                            # I had many more lines of code to try to replicate the work of this line.

    #body is the article with no line breaks.

    paragraphs = soup.find_all('div', {'class':' card-content '})
    for p in paragraphs:
        para = p.get_text()
        para = para.strip()
        x =body.find(para)
        if x not in (-1,0):
            bodylen = len(body)
            body = body[0:x] + "\n\n" + body[x:bodylen]
                            
    #An attempt to reconstitute the paragraphs using regex.
    #import re
    #body = re.sub(r'([\.\?\!]”)([^ ])', r'\1\n\n\2', body)
    #body = re.sub(r'([\.\?\!])([^ ”(com)(\.\.),\!\?])', r'\1\n\n\2', body)
    #body = re.sub(r'www\.\n', r'www.', body)

    return body

def parseJDSUPRA(a):
    a.download()

    html=a.html
    soup = grabPage(html)

    soup.find('div', id="policy-blk").decompose()

    a.html = str(soup)

    a.parse()
    text=a.text

    return text

#The new version is much cleaner.
def parseNYTimes(a):
    a.download()
    html=a.html

    if('css-18sbwfn StoryBodyCompanionColumn' in html):
        soup = grabPage(html)

        body=""
        for section in soup.findAll('div', {'class':'css-18sbwfn StoryBodyCompanionColumn'}):
        for para in section.findAll('p'):
            body+=para.get_text()
            body+="\n\n"

        final = body[0:len(body)-2]

        return final
    else:
        return altParseNYTimes(a)

#This was the original version of the function.
#Used as a back up now.
def altParseNYTimes(a):
    a.download()

    passages = {}

    html=a.html

    soup = grabPage(html)


    ##these loops remove links, bold, italics, and comments
    for link in soup.findAll('a'):
        link.replaceWithChildren()

    for b in soup.findAll('b'):
        b.replaceWithChildren()
        
    for i in soup.findAll('i'):
        i.replaceWithChildren()

    for strong in soup.findAll('strong'):
        strong.replaceWithChildren()

    for element in soup.find_all(string=lambda text:isinstance(text,Comment)):
        element.extract()

    for capt in soup.findAll('figcaption'):
        capt.extract()


    htmlClassic=str(soup)

    a.html=htmlClassic

    html =htmlClassic

    a.parse()
    text=a.text

    try:
        while text!="":
            
            first20chars=text[0:20]
            
            last20chars= text[len(text)-20:]

            

            start=html.find(first20chars)
            position = htmlClassic.find(first20chars)
            end= html.find(last20chars) + 20

            toRemove=html[start:end]

            a.html = html.replace(toRemove,"")
            html = a.html
            
            #wait = input("PRESS ENTER TO CONTINUE.")
            passages[position]=text
            
            a.parse()
            if(a.text==text):
                text=""
            else:
                text = a.text

    except:
        pass

    if len(passages)>1:
        last = passages.popitem()
        ##print(last)
        ##print("^this is lopped off")

    finalText=""
    first=True
    for key in sorted(OrderedDict(sorted(passages.items()))):
        #print (key)
        if (not first):
            print("\n")
        finalText+=passages[key]
        first = False

    return finalText

def parseChiTribune(a):
    a.download()

    a.parse()
    text=a.text

    totalText=""

    try:
            totalText +=text

            endmatter = totalText.find("RELATED:")

            if endmatter!=-1:
                arrows = totalText.find("»")
                print(arrows)
                if arrows>endmatter:
                    totalText= totalText[:endmatter]
                    print(totalText)
            

    except:
        pass

    return totalText
