import numpy as np
import json
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.externals import joblib
import tempfile
import string
from nltk import word_tokenize


class TfIdf(object):
    b2s = None

    priceVec = None
    docVec = None
    tfidf = None
    word2Ind = None
    ind2Word = None
    logReg = None

    def __init__(self, b2s):
        self.b2s = b2s

    # traing logistic regression on self.tfidf vector
    # There's also a price vector that's outputed during self.tfidf building
    def train_regression(self, begin, end):
        if self.priceVec is None or self.docVec is None:
            self.build_tfidf(begin,end)

        self.logReg = LogisticRegression()
        self.logReg.fit(self.docVec, self.priceVec)
        temp = tempfile.NamedTemporaryFile()
        joblib.dump(self.logReg, temp.name)
        self.b2s.upload('classifiers/lr_listing.pkl',
                        temp.read(), 'application/octet-stream')
        return self.logReg.score(self.docVec, self.priceVec)

    # build TFIDF and word/index translation
    # WATCH OUT the docRaw size, might explode on heroku
    def build_tfidf(self, begin, end):
        docRaw = []
        files = self.b2s.ls('data/training')
        self.priceVec = np.zeros(len(files))
        for i, file in enumerate(files[begin:end+1]):
            f = file['fileName']
            # read json into dict
            if not f.endswith('.json'):
                continue
            textJson = self.b2s.download(f)
            listing = json.loads(textJson)
            raw = listing['description'] + ' ' + listing['name']
            docRaw.append(raw.translate(str.maketrans(
                {key: None for key in string.punctuation})))
            self.priceVec[i] = min(int(listing['price'] / 50), 10)
        self.tfidf = TfidfVectorizer(
            stop_words='english', max_df=0.7, min_df=5, norm='l2', tokenizer=word_tokenize)
        self.docVec = self.tfidf.fit_transform(docRaw)
        self.word2Ind = {}
        self.ind2Word = {}
        for i, v in enumerate(self.tfidf.get_feature_names()):
            self.word2Ind[v] = i
            self.ind2Word[i] = v

        self.b2s.dumpAndUploadRaw(self.priceVec, 'classifiers/priceVec.pkl')
        self.b2s.dumpAndUploadRaw(self.docVec, 'classifiers/docVec.pkl')
        self.b2s.dumpAndUploadRaw(self.tfidf, 'classifiers/tfidf.pkl')
        self.b2s.dumpAndUploadRaw(self.word2Ind, 'classifiers/word2Ind.pkl')
        self.b2s.dumpAndUploadRaw(self.ind2Word, 'classifiers/ind2Word.pkl')

        return True
