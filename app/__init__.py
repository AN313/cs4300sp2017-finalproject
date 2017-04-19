from flask import Flask, request, render_template, send_from_directory
import json
from app.controllers.concerns import naive_bayes
import os

view_dir = os.path.join(os.path.dirname(
                        os.path.abspath(__file__)), 'views')


asset_dir = os.path.join(os.path.dirname(
                        os.path.abspath(__file__)), 'assets')

app = Flask(__name__, template_folder=view_dir)


@app.route("/")
def homeIndex():
    return "Hello World!"


@app.route("/admin")
def adminIndex():
    return "Hello Admin!"


@app.route("/host")
def hostIndex():
    return render_template('host.html')


@app.route("/host/predict", methods=['POST'])
def hostPredict():
    listing = request.json

    # print "json:   " + str(listing)
    priceClass = naive_bayes.predict_listing(listing)[0]
    low = priceClass*50
    high = (priceClass+1)*50-1
    

    return json.dumps({
        'priceClass': str(low)+" ~ " + str(high)
        # 'priceClass': 50
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
    return send_from_directory(os.path.join(asset_dir,'javascripts'), path)


@app.route('/static/stylesheets/<path:path>')
def send_css(path):
    print(path)
    return send_from_directory(os.path.join(asset_dir,'stylesheets'), path)
