import numpy as np
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.externals import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
import os, json, string
from nltk import word_tokenize

class NaiveBayes(object):
    dataDir = ''
    assetsDir = ''

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

    def __init__(self, dataDir, assetsDir):
        self.dataDir = dataDir
        self.assetsDir = assetsDir

    # Input:
    # jsonObj: json object
    def predict_listing(self, jsonObj):
        priceRange = []
        similar = []
        test = self.bundle_json_obj(jsonObj)
        clf = joblib.load(os.path.join(
<<<<<<< HEAD
            self.assetsDir, 'classifiers', 'knn_listing.pkl'))
        id2listing = joblib.load(os.path.join(
            self.assetsDir, 'classifiers', 'id2listing.pkl'))
        neighbs = clf.kenighbours(test, n_neighbors=10, return_distance=False)
        probs = clf.predict_proba(test)[0]
        res = np.argsort(probs)[::-1]
        for i in range(2):
            priceRange.append({'priceRange':self.int2Price(res[i]),
                        'prob':str(float("{0:.2f}".format(probs[res[i]])))})
        for i in range(10):
            similar.append(self.getListingInfo(str(id2listing[neighbs[0][i]])))
        return priceRange, similar
=======
            self.assetsDir, 'classifiers', 'nb_listing.pkl'))
        # print(clf.predict(test)[0])
        return clf.predict(test)[0]
>>>>>>> f65dbd8fe9c1e65e99730b20fc500533814acd25

    def int2Price(self, rank):
        return str(rank*25)+' ~ '+str((rank+1)*25-1)

    # Input:
    # strObj: input String
    def predict_str(self, strObj):
        result = []
        test = self.doc2idf(strObj)
        clf = joblib.load(os.path.join(
            self.assetsDir, 'classifiers', 'lr_listing.pkl'))
        probs = clf.predict_proba(test)[0]
        res = np.argsort(probs)[::-1]
        for i in range(3):
            result.append({'priceRange':self.int2Price(res[i]),
                            'prob':str(float("{0:.2f}".format(100*probs[res[i]])))+'%'})
        return result

    def doc2idf(self, doc):
        tfidf_vec = joblib.load(os.path.join(
            self.assetsDir, 'classifiers', 'tfidf.pkl'))
        return tfidf_vec.transform([doc]).toarray()

    def find_similar(self,strObj):
        test = self.doc2idf(strObj)
        docVec = joblib.load(os.path.join(
            self.assetsDir, 'classifiers', 'docVec.pkl'))
        id2listing = joblib.load(os.path.join(
            self.assetsDir, 'classifiers', 'id2listing.pkl'))
        cosSim = docVec.toarray().dot(test.reshape((-1, 1)))
        res = np.argsort(cosSim[:,0])[::-1]
        result = []
        for i in range(10):
            result.append(self.getListingInfo(str(id2listing[res[i]])))
        return result

    def getListingInfo(self, listing):
        result = {}
        path = os.path.join(self.dataDir,listing+'.json')
        with  open(path,'r') as f:
            fileJson = json.load(f)
            result.update({'description':fileJson['description']})
            result.update({'name':fileJson['name']})
            result.update({'picture_url':fileJson['picture_url']})
            result.update({'url':"airbnb.com/rooms/"+listing})
            result.update({'id':listing})
            result.update({'price':fileJson['price']})
        return result

    def getTopWords(self, doc):
        testVec = self.doc2idf(doc)
        i2w = joblib.load(os.path.join(
            self.assetsDir, 'classifiers','ind2Word.pkl'))
        logReg = joblib.load(os.path.join(
            self.assetsDir, 'classifiers', 'lr_listing.pkl'))
        rank = logReg.predict(testVec)

        coef = logReg.coef_[int(rank[0])]
        product = coef*testVec.reshape(-1)
        result = np.argsort(product)[::-1]
        topWords = []
        lowWords = []
        for i in range(10):
            if product[result[i]] > 0:
                topWords.append({'word':i2w[result[i]],
                            'val':str(float("{0:.2f}".format(product[result[i]])))})
            else:
                break
        result = result[::-1]
        for i in range(10):
            if product[result[i]] > 0:
                lowWords.append({'word':i2w[result[i]],
                            'val':str(float("{0:.2f}".format(product[result[i]])))})
            else:
                break
        return topWords, lowWords

    def getReviewWords(self, doc, similar):
        i2w = joblib.load(os.path.join(
                self.assetsDir, 'classifiers','ind2Word.pkl'))
        review = ""
        res = []
        for s in similar:
            listing = s['id']
            path = os.path.join(self.dataDir,listing+'.json')
            with open(path,'r') as f:
                fileJson = json.load(f)
                if 'review' in fileJson:
                    review += ' '+(fileJson['review'])

        tfidf = self.doc2idf(review)[0]
        result = np.argsort(tfidf)[::-1]
        for i in range(10):
            res.append({'word':i2w[result[i]],
                        'val':str(float("{0:.2f}".format(tfidf[result[i]]*100)))})
        return res

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
        i = 0
        for k in self.FEAT:
            if type(listing[k]) is str:
                X[0,i] = abs(hash(listing[k])%10000)
            elif type(listing[k]) is int or type(listing[k]) is float:
                X[0,i] = float(listing[k])
            elif type(listing[k]) is list:
                for item in listing[k]:
                    X[0,i] = abs(hash(item)%10000)
            else:
                continue
            i = i + 1
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
