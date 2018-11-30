from utilityFunctions import *
import shutil
import MySQLdb
import os

# this is a script I wrote to merge the databases from my local computer to the one on the server
# not cut and dry though, it assumes you've imported the server db to your local machine and titled it SupremeCourtApp2
# Any article in SupremeCourtApp (the local copy), but not in SupremeCourtApp2 (the server copy), will be imported into it (and then you can import the merged .sql file to the server but renamed SupremeCourtApp)
# Images also follow a very specific file structure that likely won't be used by the time anyone reads this (too lazy to describe)
# Basically, don't use this script - but if you do want to merge the databases, the concepts are here so you can personalize it, this was very quick and dirty

def insertKeywords(local,server,oldID,newID):
    local.execute("""SELECT keyword from article_keywords natural join keyword_instances natural join article where idArticle=(%s)""",(oldID,))
    krows = local.fetchall()
    keywords = []
    for k in krows:
        keywords.append(k['keyword'])
    addKeywords(newID,server,keywords)

def keywordIsDuplicate(key, c):
        c.execute("""SELECT idKey FROM article_keywords WHERE keyword = %s""",(key,))
        if c.rowcount == 0:
            return False
        else:
            return True

# inserts keywords from the Article keyword array into the database one-by-one 
def addKeywords(idArticle,c,keywords):
    # if keyword is a first occurrence, insert it into article_keywords
    for key in keywords:
        if not keywordIsDuplicate(key,c):
            c.execute("""INSERT INTO article_keywords(keyword) VALUES (%s)""",(key,))
            idKey = c.lastrowid
        else:
            c.execute("""SELECT idKey FROM article_keywords WHERE keyword = %s""",(key,))
            row = c.fetchone()
            idKey = row['idKey']
        c.execute("""INSERT INTO keyword_instances(idArticle,idKey) VALUES (%s,%s)""",(idArticle,idKey))

def insertImages(local,server,oldArticleID,newArticleID):
    local.execute("""SELECT * FROM image WHERE idArticle = %s""",(oldArticleID,))
    rows = local.fetchall()
    for r in rows:
        oldImageID = r['idImage']

        split = r['path'].split("-")
        newFilename = "id" + str(newArticleID)
        if len(split) > 1:
            newFilename += ("-" + split[1])
        newFilename += ".jpg"

        server.execute("""INSERT INTO image(idArticle, path, url) VALUES (%s,%s,%s)""",(newArticleID, newFilename, r['url']))
        newImageID = server.lastrowid
        addEntities(local,server,oldImageID,newImageID)
        saveImages(r['path'],newFilename)

def addEntities(local,server,oldImageID,newImageID):
    local.execute("""SELECT entity,score from image natural join image_entities natural join entity_instances where idImage = %s""",(oldImageID,))
    erows = local.fetchall()
    for er in erows:
        entity =  er['entity']
        score = er['score']
        if not entityIsDuplicate(entity,server):
            server.execute("""INSERT INTO image_entities(entity) VALUES (%s)""", (entity,))
            idEntity = server.lastrowid
        else:
            server.execute("""SELECT idEntity FROM image_entities WHERE entity = %s""",(entity,))
            row = server.fetchone()
            idEntity = row['idEntity']
        server.execute("""INSERT INTO entity_instances(idEntity,score,idImage) VALUES (%s,%s,%s)""",(idEntity,score,newImageID))

def saveImages(oldFilename,newFilename):
    try:
        oldpath = "./images/" + oldFilename
        newpath = "./mergedImages/" + newFilename
        shutil.copyfile(oldpath,newpath)
    except Exception as e:
        print(e)

# checks whether a specific image entity is already in the database
def entityIsDuplicate(entity, c):
    c.execute("""SELECT idEntity FROM image_entities WHERE entity = %s""",(entity,))
    if c.rowcount == 0:
        return False
    else:
        return True


def merge(local,server):
    print("Collecting local database...")
    local.execute("""SELECT * from article ORDER BY idArticle DESC""")
    rows = local.fetchall()
    i = 0
    for r in rows:
        #if i > 1:
            #break

        oldID = r['idArticle']
        print(r['source'],':',r['title'])
        if not articleIsDuplicate(r['title'],server):
            # insert Article
            t = (r['url'],r['source'],r['author'],r['date'],r['article_text'],r['title'],r['score'],r['magnitude'])
            server.execute("""INSERT INTO article(url, source, author, date, article_text, title, score, magnitude) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",t)
            newID = server.lastrowid
        
            print(oldID,'->',newID,':','article inserted')

            #then keywords
            insertKeywords(local,server,oldID,newID)
            print("Keywords inserted")

            #then images ()
            insertImages(local,server,oldID,newID)
            print("Images inserted/saved")

            i += 1
        print("==========================================")
    print(i,"inserts")

def main():
    db1 = MySQLdb.connect(host=os.environ['DB_HOST'],port=int(os.environ['DB_PORT']),user=os.environ['DB_USER'],password=os.environ['DB_PASSWORD'],db="SupremeCourtApp",use_unicode=True,charset="utf8")
    local = db1.cursor(MySQLdb.cursors.DictCursor)

    db2 = MySQLdb.connect(host=os.environ['DB_HOST'],port=int(os.environ['DB_PORT']),user=os.environ['DB_USER'],password=os.environ['DB_PASSWORD'],db="SupremeCourtApp2",use_unicode=True,charset="utf8")
    db2.autocommit(True)
    server = db2.cursor(MySQLdb.cursors.DictCursor)

    merge(local,server)

main()



    

