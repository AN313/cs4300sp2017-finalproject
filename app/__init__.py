from flask import Flask, request
import json
from .controllers.concerns import naive_bayes

app = Flask(__name__)


@app.route("/")
def homeIndex():
    return "Hello World!"


@app.route("/admin")
def adminIndex():
    return "Hello Admin!"


@app.route("/host")
def hostIndex():
    return "Hello Host!"


@app.route("/host/predict", methods=['POST'])
def hostPredict():
    listing = request.json
    priceClass = naive_bayes.predict(naive_bayes.bundle(listing))
    return json.dumps({
        'priceClass': priceClass
    })


@app.route("/traveler")
def travelerIndex():
    return "Hello Traveler!"


@app.route("/traveler/predict")
def travelerPredict():
    url = request.args['url']
    return json.dumps({
        'for': url,
        'priceRange': [100, 200]
    })
