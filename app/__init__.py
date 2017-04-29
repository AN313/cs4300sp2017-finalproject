from flask import Flask, request, render_template, send_from_directory, \
    jsonify, stream_with_context, Response
import json
from app.controllers.concerns import naive_bayes, tf_idf, \
    b2_storage, local_storage, \
    airbnb_crawler
import os
from dotenv import load_dotenv
import threading
import time
from celery import Celery


dotenv_path = os.path.realpath(os.path.join(os.path.dirname(
                               os.path.abspath(__file__)), '../.env'))
load_dotenv(dotenv_path)

view_dir = os.path.join(os.path.dirname(
                        os.path.abspath(__file__)), 'views')


asset_dir = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'assets')

data_dir = os.path.realpath(os.path.join(os.path.dirname(
                            os.path.abspath(__file__)), '../static/data'))


app = Flask(__name__, template_folder=view_dir)


# http://flask.pocoo.org/docs/0.12/patterns/celery/
def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery


app.config.update(
    CELERY_BROKER_URL=os.environ['REDIS_URL'] if
    'REDIS_URL' in os.environ else 'redis://localhost:6379',
    CELERY_RESULT_BACKEND=os.environ['REDIS_URL'] if
    'REDIS_URL' in os.environ else 'redis://localhost:6379'
)
celery = make_celery(app)


if 'production' in os.environ and os.environ['production']:
    b2s = b2_storage.B2Storage(os.environ['B2_ID'], os.environ['B2_KEY'])
    b2s.renewUploadToken()
    renewT = threading.Timer(86400, b2s.renewUploadToken)
    renewT.start()
else:
    b2s = local_storage.LocalStorage(['data/training', 'classifiers'])

nb = naive_bayes.NaiveBayes(b2s)
tfIdf = tf_idf.TfIdf(b2s)

crawler = airbnb_crawler.AirbnbCrawler(
    os.path.join(data_dir, 'newyork.csv'),
    os.environ['ABB_USER'], os.environ['ABB_PASSWORD'], b2s
)


@app.route("/")
def homeIndex():
    return "Hello World!"


@app.route("/admin")
def adminIndex():
    return render_template('admin.html')


@app.route("/admin/crawl")
def adminCrawl():
    posBegin = int(request.args['begin'], base=10)
    posEnd = int(request.args['end'], base=10)
    i = int(request.args['i'], base=10)
    res = crawler.crawl(i, posBegin, posEnd, noSave=False)
    return jsonify(res)


@celery.task()
def adminBuildTfIdfTask():
    tfIdf.build_tfidf()


@app.route("/admin/buildTfIdf")
def adminBuildTfIdf():
    adminBuildTfIdfTask.delay()
    return 'OK'


@celery.task()
def adminTrainRegressionTask():
    tfIdf.train_regression()


@app.route("/admin/trainRegression")
def adminTrainRegression():
    adminTrainRegressionTask.delay()
    return 'OK'


@celery.task()
def adminTrainDescTask():
    nb.train_classifier_desc()


@app.route("/admin/trainDesc")
def adminTrainDesc():
    adminTrainDescTask.delay()
    return 'OK'


@celery.task()
def adminTrainListingTask():
    nb.train_classifier_listing()


@app.route("/admin/trainListing")
def adminTrainListing():
    adminTrainListingTask.delay()
    return 'OK'


@app.route("/admin/uploadJson", methods=['POST'])
def adminUploadJson():
    fileJson = request.json
    res = b2s.upload(fileJson['name'], fileJson['data'].encode('utf-8'),
                     'application/json')
    return jsonify(res)


@app.route("/admin/downloadJson")
def adminDownloadJson():
    res = b2s.download(request.args['name'])
    return jsonify(json.loads(res))


@app.route("/admin/download")
def adminDownload():
    res = b2s.download(request.args['name'])
    return res


@app.route("/admin/listFiles")
def adminListFiles():
    res = b2s.ls(request.args['pathname'])
    return jsonify(res)


@app.route("/api/listing")
def apiListingIndex():
    res = crawler.crawl(i, noSave=True)
    return jsonify(res)


@app.route("/host")
def hostIndex():
    return render_template('host.html')


@app.route("/host/predict", methods=['POST'])
def hostPredict():
    similar = []
    topWords = ""
    listing = request.json
    if listing['classifier_type'] == "1":
        priceClass = nb.predict_listing(listing)
    elif listing['classifier_type'] == "2":
        priceClass = nb.predict_str(
            listing['description'] + listing['house_rules'])
        similar = nb.find_similar(
            listing['description'] + listing['house_rules'])
        topWords = nb.getTopWords(
            listing['description'] + listing['house_rules'])
        print(topWords)
    else:
        priceClass = -1

    low = priceClass * 50
    high = (priceClass + 1) * 50 - 1
    # print(similar[2]['id'])
    print(priceClass)

    return jsonify({
        'priceClass': str(low) + " ~ " + str(high),
        'similar': similar,
        'classifier_type': listing['classifier_type'],
        'topWords': topWords
    })


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
    return send_from_directory(os.path.join(asset_dir, 'javascripts'), path)


@app.route('/static/images/<path:path>')
def send_img(path):
    print(path)
    return send_from_directory(os.path.join(asset_dir, 'images'), path)


@app.route('/static/stylesheets/<path:path>')
def send_css(path):
    return send_from_directory(os.path.join(asset_dir, 'stylesheets'), path)


@app.route('/static/fonts/<path:path>')
def send_fonts(path):
    return send_from_directory(os.path.join(asset_dir, 'fonts'), path)
