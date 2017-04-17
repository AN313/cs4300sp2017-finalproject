import numpy as np
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn.externals import joblib
import os, json, nltk

#Assuming the training files are at /data/sensei

#features we are going to use
FEAT = "property_type, additional_house_rules, bedrooms, max_nights, summary, neighborhood, space, address, square_feet, check_out_time, transit, bathrooms, amenities, instant_bookable, experiences_offered, star_rating, price_native, max_nights, check_in_time, cancellation_policy, person_capacity, house_rules, description, bed_type, beds, room_type".split(', ')
# feature vector size
numFeat = 100
strFeat = 10000

# CHANGE this for training file directory
trainFile = "data/sensei"
#training directory
curDir = os.getcwd()
training_dir = os.path.join(curDir, trainFile)

# trains a naive bayes classifier on listings in /data/sensei
def train_classifier_listing():
    clf = GaussianNB()
    trail = os.walk(training_dir)
    for _,_,files in trail:
        X = np.zeros((len(files),numFeat))
        Y = np.zeros(len(files))
        for i, f in enumerate(files):
            #read json into dict
            raw = open(os.path.join(training_dir,f),'r')
            listing = json.load(raw)
            #adding features
            for k in FEAT:
                if type(listing[k]) is unicode:
                    X[i,hash(k)%numFeat] = 1
                elif type(listing[k]) is int or type(listing[k]) is float:
                    X[i,hash(k)%numFeat] = float(listing[k])
                else:
                    continue
            Y[i] = int(listing['price']/50)
    clf.fit(X,Y)
    joblib.dump(clf,'nb_listing.pkl')
    return clf.score(X,Y)

#train a classifier on description
def train_classifier_desc():
    clf = MultinomialNB()
    trail = os.walk(training_dir)
    for _,_,files in trail:
        X = np.zeros((len(files),strFeat))
        Y = np.zeros(len(files))
        for i, f in enumerate(files):
            #read json into dict
            raw = open(os.path.join(training_dir,f),'r')
            listing = json.load(raw)
            #tokenize description
            desc = nltk.word_tokenize(listing['description'])
            X[i] = parse_str(listing['description'])
        Y[i] = int(listing['price']/50)
    clf.fit(X,Y)
    joblib.dump(clf,'nb_str.pkl')
    return clf.score(X,Y)

#the input test should a feature vector(s)
def predict_listing(test):
    clf = joblib.load('nb_listing.pkl')
    return clf.predict(test)

#the input should be a string feature vector
def predict_str(test):
    clf = joblib.load('nb_str.pkl')
    return clf.predict(test)

#turning an opened json file into feature vector
def read_json(f):
    X = np.zeros(numFeat)
    listing = json.load(f)
    #adding features
    for k in FEAT:
        if type(listing[k]) is unicode:
            X[hash(k)%numFeat] = 1
        elif type(listing[k]) is int or type(listing[k]) is float:
            X[hash(k)%numFeat] = float(listing[k])
        else:
            continue
    X = X.reshape(1,-1)
    return X

#turning list of string (description) into feature vector
#TODO tfidf
def parse_str(f):
    X = np.zeros((1,strFeat))
    listing = json.load(f)
    desc = nltk.word_tokenize(listing['description'])
    for item in desc:
        X[0,hash(item.lower())%strFeat] = X[0,hash(item.lower())%strFeat]+1
    return X
