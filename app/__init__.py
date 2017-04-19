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
    listing = request.json
    print(listing['classifier_type'])
    if listing['classifier_type'] == "1":
        priceClass = nb.predict_listing(listing)[0]
    elif listing['classifier_type'] == "2":
        priceClass = nb.predict_str(
            listing['description'] + listing['house_rules'])
        similar = nb.find_similar(
            listing['description'] + listing['house_rules'])
    else:
        priceClass = -1
    low = priceClass * 50
    high = (priceClass + 1) * 50 - 1

    return json.dumps({
        'priceClass': str(low) + " ~ " + str(high),
        'similar': ' '.join(similar)
    })

    # price = 50
    # return render_template('host.html', price = price)


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


@app.route('/static/stylesheets/<path:path>')
def send_css(path):
    print(path)
    return send_from_directory(os.path.join(asset_dir, 'stylesheets'), path)
