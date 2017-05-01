import numpy as np
from sklearn.naive_bayes import GaussianNB
import os
import json, pprint

#features we are going to use
FEAT = "property_type, additional_house_rules, bedrooms, max_nights, summary, neighborhood, space, address, square_feet, check_out_time, transit, bathrooms, amenities, instant_bookable, experiences_offered, star_rating, price_native, max_nights, check_in_time, cancellation_policy, person_capacity, house_rules, description, bed_type, beds, room_type".split(', ')

# number of features allowed
numFeat = 100

#walk through training folder
curDir = os.getcwd()
training_dir = os.path.join(curDir, "data\sensei")
trail = os.walk(training_dir)
for _,_,files in trail:
    #initiated training and target
    X = np.zeros((len(files),numFeat))
    Y = np.zeros(len(files))
    for i,f in enumerate(files):
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

clf = GaussianNB()
clf.fit(X,Y)
print clf.score(X,Y)
