from sklearn.naive_bayes import GaussianNB
from sklearn.externals import joblib
import os
import json
import numpy as np

# Assuming the training files are at /data/sensei

# features we are going to use
FEAT = "property_type, additional_house_rules, bedrooms, max_nights, summary, neighborhood, space, address, square_feet, check_out_time, transit, bathrooms, amenities, instant_bookable, experiences_offered, star_rating, price_native, max_nights, check_in_time, cancellation_policy, person_capacity, house_rules, description, bed_type, beds, room_type".split(
    ', ')
# feature vector size
numFeat = 100

# CHANGE this for training file directory
trainFile = "data/sensei"
# training directory
curDir = os.getcwd()
training_dir = os.path.join(curDir, trainFile)


# trains a naive bayes classifier on listings in /data/sensei
def train_classifier():
    clf = GaussianNB()
    trail = os.walk(training_dir)
    for _, _, files in trail:
        X = np.zeros((len(files), numFeat))
        Y = np.zeros(len(files))
        for i, f in enumerate(files):
            # read json into dict
            raw = open(os.path.join(training_dir, f), 'r')
            listing = json.load(raw)
            # adding features
            X[i] = bundle(listing)
            Y[i] = int(listing['price'] / 50)
    clf.fit(X, Y)
    joblib.dump(clf, 'nb.pkl')
    return clf.score(X, Y)


# turns a listing dictionary into a feature vector
def bundle(listing):
    ret = np.zeros((1, numFeat))
    for k in FEAT:
        if k not in listing:
            continue
        if type(listing[k]) is unicode:
            ret[hash(k) % numFeat] = 1
        elif type(listing[k]) is int or type(listing[k]) is float:
            ret[hash(k) % numFeat] = float(listing[k])
        else:
            continue


# the input test should a feature vector(s)
def predict(test):
    clf = joblib.load('nb.pkl')
    return clf.predict(test)


# turning an opened json file into feature vector
def read_json(f):
    X = np.zeros(numFeat)
    listing = json.load(f)
    # adding features
    for k in FEAT:
        if type(listing[k]) is unicode:
            X[hash(k) % numFeat] = 1
        elif type(listing[k]) is int or type(listing[k]) is float:
            X[hash(k) % numFeat] = float(listing[k])
        else:
            continue
    X = X.reshape(1, -1)
    return X
