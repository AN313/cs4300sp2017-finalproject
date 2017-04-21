import csv
import json
import requests


class AirbnbCrawler(object):
    # listing ids
    idList = []
    # broken listing ids
    broken = set()

    token = ''
    b2s = None

    def __init__(self, csvFilename, username, password, b2s):
        # from csv file read all listing ids
        csvFile = open(csvFilename, 'r')
        ny = csv.reader(csvFile, dialect='excel')
        self.idList = [row[0] for row in ny]
        self.idList = self.idList[1:]  # remove header
        csvFile.close()

        # get oauth token from airbnb
        response_data = requests.post(
            'https://api.airbnb.com/v1/authorize',
            data={
                'username': username,
                'password': password,
                'client_id': '3092nxybyb0otqw18e8nh5nty'
            }
        ).json()
        self.token = response_data['access_token']
        self.b2s = b2s

    def crawl(self, index, posBegin, posEnd, noSave=True, purpose='training'):
        urlH = 'https://api.airbnb.com/v2/listings'
        urlT = '?client_id=3092nxybyb0otqw18e8nh5nty&_format=v1_legacy_for_p3'

        print('get {}'.format(index))
        listId = self.idList[index]
        if listId in self.broken:
            return False

        try:
            request = requests.get(
                '{}/{}{}'.format(urlH, listId, urlT),
                headers={'X-Airbnb-OAuth-Token': self.token}
            )
            result = request.json()['listing']
            resultJson = json.dumps(
                result,
                sort_keys=True,
                separators=(',', ':')
            ).encode('utf-8')

            if noSave:
                return result

            self.b2s.upload(
                'data/{}/{}-{}/{}.json'.format(
                    purpose,
                    posBegin,
                    posEnd,
                    listId
                ),
                resultJson,
                'application/json'
            )
            return result
        except(KeyError):
            self.broken.add(listId)
            return False
