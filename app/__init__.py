from flask import Flask, request, render_template, send_from_directory
import json
from app.controllers.concerns import naive_bayes
import os

view_dir = os.path.join(os.path.dirname(
                        os.path.abspath(__file__)), 'views')


asset_dir = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'assets')

data_dir = os.path.realpath(os.path.join(os.path.dirname(
                            os.path.abspath(__file__)), '../static/data'))

nb = naive_bayes.NaiveBayes(data_dir, asset_dir)

app = Flask(__name__, template_folder=view_dir)


@app.route("/")
def homeIndex():
    return "Hello World!"


@app.route("/admin")
def adminIndex():
    return "Hello Admin!"


@app.route("/admin/trainDesc")
def adminTrainDesc():
    nb.train_classifier_desc()
    return 'OK'


@app.route("/admin/trainListing")
def adminTrainListing():
    nb.train_classifier_listing()
    return 'OK'


@app.route("/host")
def hostIndex():
    return render_template('host.html')


@app.route("/host/predict", methods=['POST'])
def hostPredict():
    similar = []
    topWords = ""
    listing = request.json
    print(listing['classifier_type'])
    if listing['classifier_type'] == "1":
        priceClass = nb.predict_listing(listing)
    elif listing['classifier_type'] == "2":
        priceClass = nb.predict_str(
            listing['description'] + listing['house_rules'])
        similar = nb.find_similar(
            listing['description'] + listing['house_rules'])
        topWords = nb.getTopWords(
            listing['description'] + listing['house_rules'])
        reviewWords = nb.getReviewWords(
            listing['description'] + listing['house_rules'],
            similar)
    else:
        priceClass = -1

    low = priceClass * 25
    high = (priceClass + 1) * 25 - 1
    # print(similar[2]['id'])
    print(priceClass);

    return json.dumps({
        'priceClass': str(low) + " ~ " + str(high),
        'similar': similar,
        'classifier_type': listing['classifier_type'],
        'topWords': topWords,
        'reviewWords':reviewWords
        })

@app.route("/traveler")
def travelerIndex():
    return render_template('traveler.html')


@app.route("/traveler/predict")
def travelerPredict():
    url = request.args['url']
    return json.dumps({
        'for': url,
        'priceRange': [100, 200]
    })


@app.route('/static/javascripts/<path:path>')
def send_js(path):
    print(path)
    return send_from_directory(os.path.join(asset_dir, 'javascripts'), path)

@app.route('/static/images/<path:path>')
def send_img(path):
    print(path)
    return send_from_directory(os.path.join(asset_dir, 'images'), path)


@app.route('/static/stylesheets/<path:path>')
def send_css(path):
    print(path)
    return send_from_directory(os.path.join(asset_dir, 'stylesheets'), path)
