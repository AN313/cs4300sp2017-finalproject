import numpy as np
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn.externals import joblib
import os, json, nltk



import os
# __file__ refers to the file settings.py 
APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
APP_STATIC = os.path.join(APP_ROOT, 'static')

#Assuming the training files are at /data/sensei

#features we are going to use
FEAT = "property_type, additional_house_rules, bedrooms, max_nights, summary, neighborhood, space, address, square_feet, check_out_time, transit, bathrooms, amenities, instant_bookable, experiences_offered, star_rating, name, max_nights, check_in_time, cancellation_policy, person_capacity, house_rules, description, bed_type, beds, room_type".split(', ')
# feature vector size
numFeat = 100
strFeat = 2500
# CHANGE this for training file directory
trainFile = "data/sensei"
#training directory
curDir = os.getcwd()
training_dir = os.path.join(curDir, trainFile)

# trains a naive bayes classifier on listings in /data/sensei
def train_classifier_listing(dataDir = None):
    if dataDir == None:
        dataDir = training_dir
    clf = GaussianNB()
    trail = os.walk(dataDir)
    for _,_,files in trail:
        X = np.zeros((len(files),numFeat))
        Y = np.zeros(len(files))
        for i, f in enumerate(files):
            #read json into feature vector
            raw = open(os.path.join(training_dir,f),'r')
            listing = json.load(raw)
            X[i] = read_jsonObj(listing)
            Y[i] = int(listing['price']/50)
    clf.fit(X,Y)
    joblib.dump(clf,'nb_listing.pkl')
    return clf.score(X,Y)

#train a classifier on description
def train_classifier_desc(dataDir = None):
    if dataDir == None:
        dataDir = training_dir

    clf = MultinomialNB()
    trail = os.walk(dataDir)
    for _,_,files in trail:
        X = np.zeros((len(files),strFeat))
        Y = np.zeros(len(files))
        for i, f in enumerate(files):
            #read json into dict
            raw = open(os.path.join(training_dir,f),'r')
            listing = json.load(raw)
            X[i] = parse_str(listing['description']+listing['name']+listing['house_rules'])
            Y[i] = int(listing['price']/50)
    clf.fit(X,Y)
    joblib.dump(clf,'nb_str.pkl')
    return clf.score(X,Y)

# Input:
# jsonObj: json object
def predict_listing(jsonObj):
    # print os.getcwd()
    test = read_jsonObj(jsonObj)
    clf = joblib.load(os.path.join(APP_STATIC, 'nb_listing.pkl'))
    return clf.predict(test)

# Input:
# strObj: input String
def predict_str(strObj):
    test = parse_str(strObj)
    clf = joblib.load('nb_str.pkl')
    return clf.predict(test)

#turning an opened json file into feature vector
def read_jsonfile(f):
    X = np.zeros((1,numFeat))
    listing = json.load(f)
    #adding features
    for k in FEAT:
        if type(listing[k]) is unicode:
            X[0,hash(k)%numFeat] = 1
        elif type(listing[k]) is int or type(listing[k]) is float:
            X[0,hash(k)%numFeat] = float(listing[k])
        else:
            continue
    return X

# turning an opened json file into feature vector
def read_jsonObj(listing):
    X = np.zeros((1,numFeat))
    # adding features
    for k in FEAT:
        if k in listing:
            
            if type(listing[k]) is unicode:
                X[0,hash(k) % numFeat] = 1
            elif type(listing[k]) is int or type(listing[k]) is float:
                X[0,hash(k) % numFeat] = float(listing[k])
            else:
                continue
        else:
            continue
    X = X.reshape(1, -1)
    return X

#turning list of string (description) into feature vector
#TODO tfidf
def parse_str(s):
    X = np.zeros((1,strFeat))
    desc = nltk.word_tokenize(s)
    for item in desc:
        X[0,hash(item.lower())%strFeat] = X[0,hash(item.lower())%strFeat]+1
    return X
