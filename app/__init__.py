from flask import Flask, request, render_template, send_from_directory
import json
from .controllers.concerns import naive_bayes
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
    priceClass = naive_bayes.predict(naive_bayes.bundle(listing))
    return json.dumps({
        'priceClass': priceClass
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
    return send_from_directory(os.path.join(asset_dir,'javascripts'), path)


@app.route('/static/stylesheets/<path:path>')
def send_css(path):
    print(path)
    return send_from_directory(os.path.join(asset_dir,'stylesheets'), path)
