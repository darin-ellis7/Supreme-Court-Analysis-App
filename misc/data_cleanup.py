# this script goes through our training data spreadsheet and moves false positives into the rejectedTrainingData table of our database, rather than the primary front-facing one

import csv
import MySQLdb
import MySQLdb.cursors
import os
from tqdm import tqdm

def main():
    db = MySQLdb.connect(host=os.environ['DB_HOST'],port=int(os.environ['DB_PORT']),user=os.environ['DB_USER'],password=os.environ['DB_PASSWORD'],db="SupremeCourtApp",use_unicode=True,charset="utf8")
    db.autocommit(True)
    c = db.cursor(MySQLdb.cursors.DictCursor)
    with open('./misc/training_data_09_30_2019.csv') as csvfile: # change filename appropriately here
        reader = csv.DictReader(csvfile)
        total = len(list(reader))
        csvfile.seek(0,0)
        reader = csv.DictReader(csvfile)
        for row in tqdm(iterable=reader,desc='Training Data',total=total):
            try:
                ID = row['Article ID'].strip()
                c.execute("""SELECT url, title, date, article_text FROM article WHERE idArticle=%s LIMIT 1""",(ID,))
                if c.rowcount == 1:
                    article = c.fetchone()
                    t = (article['url'],article['date'],article['title'],article['article_text'],row['Code'].strip())
                    c.execute("""INSERT INTO rejectedTrainingData(url,date,title,text,code) VALUES (%s,%s,%s,%s,%s)""",t)
                    c.execute("""DELETE FROM article WHERE idArticle=%s LIMIT 1""",(ID,))
            except Exception as e:
                print(e)
                continue
main()
