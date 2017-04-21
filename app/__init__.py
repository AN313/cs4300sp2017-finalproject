from flask import Flask, request, render_template, send_from_directory, jsonify
import json
from app.controllers.concerns import naive_bayes, b2_storage
import os
from dotenv import load_dotenv
import threading

dotenv_path = os.path.realpath(os.path.join(os.path.dirname(
                               os.path.abspath(__file__)), '../.env'))
load_dotenv(dotenv_path)

view_dir = os.path.join(os.path.dirname(
                        os.path.abspath(__file__)), 'views')


asset_dir = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'assets')

data_dir = os.path.realpath(os.path.join(os.path.dirname(
                            os.path.abspath(__file__)), '../static/data'))

nb = naive_bayes.NaiveBayes(data_dir, asset_dir)

app = Flask(__name__, template_folder=view_dir)

b2s = b2_storage.B2Storage(os.environ['B2_ID'], os.environ['B2_KEY'])
b2s.renewUploadToken()
renewT = threading.Timer(86400, b2s.renewUploadToken)
renewT.start()


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


@app.route("/admin/uploadJson", methods=['POST'])
def adminUploadJson():
    fileJson = request.json
    res = b2s.upload(fileJson['name'], fileJson['data'],
                     'application/json')
    return jsonify(res)


@app.route("/admin/downloadJson")
def adminDownloadJson():
    res = b2s.download(request.args['name'])
    return jsonify(json.loads(res))


@app.route("/admin/listFiles")
def adminListFiles():
    res = b2s.ls(request.args['pathname'])
    return jsonify(res)


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

    return jsonify({
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
    return jsonify({
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
