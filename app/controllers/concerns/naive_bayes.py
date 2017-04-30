import numpy as np
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.externals import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
import os
import json
import string
from nltk import word_tokenize
import tempfile


class NaiveBayes(object):
    b2s = None

    # features we are going to use
    FEAT = ["property_type", "additional_house_rules", "bedrooms", "max_nights",
            "summary", "neighborhood", "space", "address", "square_feet",
            "check_out_time", "transit", "bathrooms", "amenities",
            "instant_bookable", "experiences_offered", "star_rating", "name",
            "max_nights", "check_in_time", "cancellation_policy",
            "person_capacity", "house_rules", "description", "bed_type",
            "beds", "room_type"]

    # feature vector size
    numFeat = 100
    strFeat = 2500
    clfDesc = None
    clfListing = None
    trainingVec = None
    id2listing = None

    def __init__(self, b2s):
        self.b2s = b2s

    # trains a naive bayes classifier on listings in /data/sensei
    def train_classifier_listing(self, begin, end):
        self.clfListing = GaussianNB()
        files = self.b2s.ls('data/training')
        X = np.zeros((len(files), self.numFeat))
        Y = np.zeros(len(files))
        for i, file in enumerate(files[begin:end+1]):
            f = file['fileName']
            # read json into feature vector
            if not f.endswith('.json'):
                continue
            textJson = self.b2s.download(f)
            listing = json.loads(textJson)
            X[i] = self.bundle_json_obj(listing)
            Y[i] = max(int(listing['price'] / 50), 10)
        self.clfListing.fit(X, Y)
        temp = tempfile.NamedTemporaryFile()
        joblib.dump(self.clfListing, temp.name)
        self.b2s.upload('classifiers/nb_listing.pkl',
                        temp.read(), 'application/octet-stream')
        return self.clfListing.score(X, Y)

    # train a classifier on description
    def train_classifier_desc(self, begin, end):
        self.clfDesc = MultinomialNB()
        files = self.b2s.ls('data/training')
        X = np.zeros((len(files), self.strFeat))
        Y = np.zeros(len(files))
        for i, file in enumerate(files[begin:end+1]):
            f = file['fileName']
            # read json into dict
            if not f.endswith('.json'):
                continue
            textJson = self.b2s.download(f)
            listing = json.loads(textJson)
            X[i] = self.parse_str('{} {} {}'.format(
                                  listing['description'],
                                  listing['name'],
                                  listing['house_rules']))
            Y[i] = max(int(listing['price'] / 50), 10)
        self.clfDesc.fit(X, Y)
        temp = tempfile.NamedTemporaryFile()
        joblib.dump(self.clfDesc, temp.name)
        self.b2s.upload('classifiers/nb_str.pkl',
                        temp.read(), 'application/octet-stream')
        return self.clfDesc.score(X, Y)

    # Input:
    # jsonObj: json object
    def predict_listing(self, jsonObj):
        test = self.bundle_json_obj(jsonObj)
        if self.clfListing is None:
            temp = tempfile.TemporaryFile()
            temp.write(self.b2s.downloadRaw(
                       'classifiers/nb_listing.pkl'))
            self.clfListing = joblib.load(temp)
        return self.clfListing.predict(test)[0]

    # Input:
    # strObj: input String
    def predict_str(self, strObj):
        test = self.doc2idf(strObj)
        if self.clfLinReg is None:
            temp = tempfile.TemporaryFile()
            temp.write(bytearray(self.b2s.downloadRaw(
                       'classifiers/lr_listing.pkl')))
            self.clfLinReg = joblib.load(temp)
        return self.clfLinReg.predict(test)[0]

    def doc2idf(self, doc):
        if self.tfIdfVec is None:
            temp = tempfile.TemporaryFile()
            temp.write(bytearray(self.b2s.downloadRaw(
                       'classifiers/tfidf.pkl')))
            self.tfIdfVec = joblib.load(temp)
        return self.tfIdfVec.transform([doc]).toarray()

    def find_similar(self, strObj):
        test = self.doc2idf(strObj)

        if self.docVec is None:
            temp = tempfile.TemporaryFile()
            temp.write(self.b2s.downloadRaw(
                       'classifiers/docVec.pkl'))
            self.docVec = joblib.load(temp)

        if self.id2listing is None:
            temp = tempfile.TemporaryFile()
            temp.write(bytearray(self.b2s.downloadRaw(
                       'classifiers/id2listing.pkl')))
            self.id2listing = joblib.load(temp)

        cosSim = self.docVec.toarray().dot(test.reshape((-1, 1)))
        res = np.argsort(cosSim[:, 0])[::-1]
        result = []
        for i in range(10):
            result.append(res[i])

        return result

    def getTopWords(self, doc):
        testVec = self.doc2idf(doc)
        i2w = joblib.load(os.path.join(
            self.assetsDir, 'classifiers', 'ind2Word.pkl'))
        logReg = joblib.load(os.path.join(
            self.assetsDir, 'classifiers', 'lr_listing.pkl'))
        rank = logReg.predict(testVec)

        coef = logReg.coef_[int(rank[0])]
        product = coef * testVec.reshape(-1)
        result = np.argsort(product)[::-1]
        topWords = ""
        for i in range(10):
            topWords += i2w[result[i]] + '     '
            topWords += str(product[result[i]]) + '\n'
        result = result[::-1]
        for i in range(10):
            topWords += i2w[result[i]] + '     '
            topWords += str(product[result[i]]) + '\n'
        return topWords

    # turning an opened json file into feature vector
    def bundle_json_file(self, f):
        X = np.zeros((1, self.numFeat))
        listing = json.load(f)
        # adding features
        for k in self.FEAT:
            if type(listing[k]) is str:
                X[0, hash(k) % self.numFeat] = 1
            elif type(listing[k]) is int or type(listing[k]) is float:
                X[0, hash(k) % self.numFeat] = float(listing[k])
            else:
                continue
        return X

    # turning an opened json file into feature vector
    def bundle_json_obj(self, listing):
        X = np.zeros((1, self.numFeat))
        # adding features
        for k in self.FEAT:
            if k in listing:
                if type(listing[k]) is str:
                    X[0, hash(k) % self.numFeat] = 1
                elif type(listing[k]) is int or type(listing[k]) is float:
                    X[0, hash(k) % self.numFeat] = float(listing[k])
                elif type(listing[k]) is list:
                    for item in listing[k]:
                        X[0, hash(k + str(item)) % self.numFeat] = 1
                else:
                    continue
            else:
                continue
        X = X.reshape(1, -1)
        return X

    # turning list of string (description) into feature vector
    # TODO tfidf
    def parse_str(self, s):
        X = np.zeros((1, self.strFeat))
        desc = word_tokenize(s)
        for item in desc:
            bucket = hash(item.lower()) % self.strFeat
            X[0, bucket] = X[0, bucket] + 1
        return X
