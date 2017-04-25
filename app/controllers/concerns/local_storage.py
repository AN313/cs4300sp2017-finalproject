import base64
import json
import requests
import os
import hashlib
import tempfile


class LocalStorage(object):
    tokens = {'account': '', 'upload': ''}
    urls = {'api': '', 'upload': ''}
    bucket = {'name': 'airbnbpricesuggestion',
              'id': 'b579079bc4df89c653b00a13'}
    localDir = ''

    def __init__(self, dirs):
        self.localDir = tempfile.mkdtemp()
        for d in dirs:
            dName = os.path.join(self.localDir, d)
            if not os.path.exists(dName):
                os.makedirs(dName)

    def upload(self, filename, data, contentType):
        filenameF = os.path.join(self.localDir, filename)
        if not os.path.isdir(os.path.dirname(filenameF)):
            os.makedirs(os.path.dirname(filenameF))
        with open(filenameF, 'wb') as f:
            f.write(data)
        return True

    def download(self, filename):
        return downloadRaw(filename).encode('utf-8')

    def downloadRaw(self, filename):
        fileContent = None
        with open(os.path.join(self.localDir, filename), 'w') as f:
            fileContent = f.read(data)
        return fileContent

    def ls(self, pathname):
        ret = []
        for parent, dirs, files in os.walk(os.path.join(self.localDir, pathname)):
            for f in files:
                fAbsPath = os.path.join(parent, f)
                ret.append({
                    'fileName': os.path.relpath(
                        fAbsPath,
                        os.path.join(self.localDir, pathname)
                    ),
                    "action": "",
                    "contentLength": os.path.getsize(fAbsPath),
                    "contentSha1": "",
                    "contentType": "",
                    "fileId": "",
                    "fileInfo": {},
                    "contentLength": os.path.getsize(fAbsPath),
                    "uploadTimestamp": 0
                })
        return ret
