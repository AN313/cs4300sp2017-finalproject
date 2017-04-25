import base64
import json
import requests
import os
import hashlib


class B2Storage(object):
    tokens = {'account': '', 'upload': ''}
    urls = {'api': '', 'upload': ''}
    bucket = {'name': 'airbnbpricesuggestion',
              'id': 'b579079bc4df89c653b00a13'}

    def __init__(self, b2Id, b2Key):
        id_and_key = '{}:{}'.format(b2Id, b2Key)
        auth_string = 'Basic ' + base64.b64encode(id_and_key.encode(
                                                  'ascii')).decode('ascii')

        response_data = requests.get(
            'https://api.backblazeb2.com/b2api/v1/b2_authorize_account',
            headers={'Authorization': auth_string}
        ).json()
        self.tokens['account'] = response_data['authorizationToken']
        self.urls['api'] = response_data['apiUrl']
        self.urls['download'] = response_data['downloadUrl']

    def renewUploadToken(self):
        response_data = requests.post(
            '%s/b2api/v1/b2_get_upload_url' % self.urls['api'],
            data=json.dumps({'bucketId': self.bucket['id']}),
            headers={'Authorization': self.tokens['account']}
        ).json()

        self.tokens['upload'] = response_data['authorizationToken']
        self.urls['upload'] = response_data['uploadUrl']

    # def renewDownloadToken():
    #     response_data = requests.post(
    #         '%s/b2api/v1/b2_get_download_authorization' % self.urls['api'],
    #         data=json.dumps({
    #             'bucketId': self.bucket['id'],
    #             'fileNamePrefix': '',
    #             'validDurationInSeconds': 604800
    #         }),
    #         headers={'Authorization': self.tokens['account']}
    #     ).json()
    #
    #     self.tokens['download'] = response_data['authorizationToken']

    def upload(self, filename, data, contentType):
        sha1 = hashlib.sha1(data).hexdigest()

        headers = {
            'Authorization': self.tokens['upload'],
            'X-Bz-File-Name':  filename,
            'Content-Type': contentType,
            'X-Bz-Content-Sha1': sha1
        }
        response_data = requests.post(
            self.urls['upload'],
            data=data,
            headers=headers
        ).json()
        return response_data

    def download(self, filename):
        url = '{}/file/{}/{}'.format(self.urls['download'],
                                     self.bucket['name'],
                                     filename)
        headers = {'Authorization': self.tokens['account']}
        response_data = requests.get(url, headers=headers).text
        return response_data

    def downloadRaw(self, filename):
        url = '{}/file/{}/{}'.format(self.urls['download'],
                                     self.bucket['name'],
                                     filename)
        headers = {'Authorization': self.tokens['account']}
        response_data = requests.get(url, headers=headers).content
        return response_data

    def ls(self, pathname):
        response_data = requests.post(
            '%s/b2api/v1/b2_list_file_names' % self.urls['api'],
            data=json.dumps({'bucketId': self.bucket['id']}),
            headers={'Authorization': self.tokens['account']}
        ).json()['files']
        return [fn for fn in response_data if
                fn['fileName'].startswith(pathname)]