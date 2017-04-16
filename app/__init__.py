from flask import Flask, request
import json

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
    price = request.json['price']
    rooms = request.json['rooms']
    return json.dumps({
        'priceRange': [price - 10, price + 10]
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
