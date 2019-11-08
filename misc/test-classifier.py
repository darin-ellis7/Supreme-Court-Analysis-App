# quick script for testing classifier accuracy

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import train_test_split
from nltk.corpus import stopwords
from scipy.sparse import hstack
import MySQLdb
import MySQLdb.cursors
import os

def get_training_data(c,binary):
    x = []
    y = []
    # get relevant training data
    c.execute("""SELECT article_text,title FROM article""")
    rows = c.fetchall()
    for r in rows:
        x.append([r["title"],r["article_text"]])
        y.append("R")
    # get irrelevant training data
    c.execute("""SELECT code,text,title FROM rejectedTrainingData""")
    rows = c.fetchall()
    for r in rows:
        x.append([r["title"],r["text"]])
        code = r["code"]
        if binary:
            if r["code"] != "R":
                code = "U"
        y.append(code)
    return x, y

def convertTextData(x,v_text,v_title,mode):
    Xtitle = []
    Xtext = []
    for row in x:
        Xtitle.append(row[0])
        Xtext.append(row[1])
    if mode == 'train':
        Xtitle = v_title.fit_transform(Xtitle)
        Xtext = v_text.fit_transform(Xtext)
    else:
        Xtitle = v_title.transform(Xtitle)
        Xtext = v_text.transform(Xtext)
    x = hstack([Xtext,Xtitle])
    return x

def prepare_data(training_texts,training_labels):
    Xtrain, Xtest, Ytrain, Ytest = train_test_split(training_texts,training_labels,test_size=0.33)
    v_text = TfidfVectorizer(stop_words=stopwords.words("english"),min_df=5)
    v_title = TfidfVectorizer(stop_words=stopwords.words("english"),ngram_range=(1,3))
    Xtrain = convertTextData(Xtrain,v_text,v_title,'train')
    Xtest = convertTextData(Xtest,v_text,v_title,'test')
    return Xtrain, Xtest, Ytrain, Ytest

def test(c,n,binary):
    scores = []
    x, y = get_training_data(c,binary)
    for i in range(n):
        Xtrain, Xtest, Ytrain, Ytest = prepare_data(x, y)
        clf = CalibratedClassifierCV(LinearSVC(),method='sigmoid',cv=3).fit(Xtrain,Ytrain)
        predict = clf.predict(Xtest)
        print(clf.classes_)
        accuracy = accuracy_score(Ytest,predict)
        scores.append(accuracy)
    avg = sum(scores) / len(scores)
    return avg * 100

def main():
    db = MySQLdb.connect(host=os.environ['DB_HOST'],port=int(os.environ['DB_PORT']),user=os.environ['DB_USER'],password=os.environ['DB_PASSWORD'],db="SupremeCourtApp",use_unicode=True,charset="utf8")
    db.autocommit(True)
    c = db.cursor(MySQLdb.cursors.DictCursor)
    n = 1
    binary_avg = test(c,n,True)
    print("binary avg",n,"runs:",str(binary_avg)+"%")
    multi_avg = test(c,n,False)
    print("multi avg",n,"runs:",str(multi_avg)+"%")

main()