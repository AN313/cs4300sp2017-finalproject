import numpy as np
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn.externals import joblib
import os
import json
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

    def __init__(self, b2s):
        self.b2s = b2s

    # trains a naive bayes classifier on listings in /data/sensei
    def train_classifier_listing(self):
        clf = GaussianNB()
        files = self.b2s.ls('data/training')
        X = np.zeros((len(files), self.numFeat))
        Y = np.zeros(len(files))
        for i, file in enumerate(files):
            f = file['fileName']
            # read json into feature vector
            if not f.endswith('.json'):
                continue
            raw = self.b2s.download(f)
            listing = json.loads(raw)
            X[i] = self.bundle_json_obj(listing)
            Y[i] = int(listing['price'] / 50)
        clf.fit(X, Y)
        temp = tempfile.NamedTemporaryFile()
        joblib.dump(clf, temp.name)
        self.b2s.upload('classifiers/nb_listing.pkl',
                        temp.read(), 'application/octet-stream')
        return clf.score(X, Y)

    # train a classifier on description
    def train_classifier_desc(self):
        clf = MultinomialNB()
        files = self.b2s.ls('data/training')
        X = np.zeros((len(files), self.strFeat))
        Y = np.zeros(len(files))
        for i, file in enumerate(files):
            f = file['fileName']
            # read json into dict
            if not f.endswith('.json'):
                continue
            raw = self.b2s.download(f)
            listing = json.loads(raw)
            X[i] = self.parse_str('{} {} {}'.format(
                                  listing['description'],
                                  listing['name'],
                                  listing['house_rules']))
            Y[i] = int(listing['price'] / 50)
        clf.fit(X, Y)
        temp = tempfile.NamedTemporaryFile()
        joblib.dump(clf, temp.name)
        self.b2s.upload('classifiers/nb_str.pkl',
                        temp.read(), 'application/octet-stream')
        return clf.score(X, Y)

    # Input:
    # jsonObj: json object
    def predict_listing(self, jsonObj):
        test = self.bundle_json_obj(jsonObj)
        temp = tempfile.TemporaryFile()
        json.dump(self.b2s.download('classifiers/nb_listing.pkl'), temp)
        clf = joblib.load(temp)
        return clf.predict(test)

    # Input:
    # strObj: input String
    def predict_str(self, strObj):
        test = self.parse_str(strObj)
        temp = tempfile.TemporaryFile()
        json.dump(self.b2s.download('classifiers/nb_str.pkl'), temp)
        clf = joblib.load(temp)
        return clf.predict(test)

    def find_similar(self, strObj):
        test = self.parse_str(strObj)

        temp = tempfile.TemporaryFile()
        json.dump(self.b2s.download('classifiers/listing_vecs.pkl'), temp)
        trainingVec = joblib.load(temp)

        temp = tempfile.TemporaryFile()
        json.dump(self.b2s.download('classifiers/listing_vecs.pkl'), temp)
        id2listing = joblib.load(temp)

        cosSim = trainingVec.dot(test.reshape((-1, 1)))
        res = np.argsort(cosSim[:, 0])[::-1]
        result = []
        for i in range(10):
            result.append(str(id2listing[res[i]]))
        return result

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
