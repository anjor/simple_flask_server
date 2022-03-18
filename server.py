import logging
import os

from flask import Flask, jsonify, request
from flask_cors import cross_origin, CORS
import requests

app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

gunicorn_logger = logging.getLogger('gunicorn.warn')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)


class EstuaryData:
    base_url = "https://api.estuary.tech"

    def __init__(self):
        self.api_key = os.environ.get("API_KEY")
        self.auth_header = self._get_auth_header()
        self.data = None

    def _get_auth_header(self):
        return {"Authorization": "Bearer " + self.api_key}

    def list_data(self):
        if not self.data:
            resp = requests.get(url=EstuaryData.base_url + "/content/stats", headers=self.auth_header)
            if resp.status_code == 200:
                self.data = resp.json()

        return self.data

    def add_cid_to_collection(self, cid, collection_id):
        payload = {
            "contents": [],
            "cids": [cid],
            "collection": collection_id
        }
        resp = requests.post(url=EstuaryData.base_url + "/collections/add-content", headers=self.auth_header,
                             data=payload)
        app.logger.warn(resp.request.body)
        return resp.json()


def construct_url(cid):
    return "https://" + cid + ".ipfs.dweb.link"


estuary = EstuaryData()
male_collection_id = "7ca25d9a-26b4-418e-8e03-e6667e4d33b3"
female_collection_id = "34a583c1-ac36-4507-9de5-a209f48fd34e"
child_collection_id = "825c5e9a-f967-49ea-86e7-341f860d027a"


@app.route("/data/list", methods=["GET"])
@cross_origin()
def list_data():
    data = estuary.list_data()
    response = jsonify([construct_url(datum["cid"]["/"]) for datum in data])
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route("/collections/<collection>", methods=["POST"])
@cross_origin()
def add_cid_to_collection(collection):
    content = request.get_json()
    app.logger.warn("request %s", request)
    app.logger.warn("content %s", content)
    cid = content['cid']
    app.logger.warn("cid %s", cid)
    resp = {}
    if collection == 'male':
        resp = estuary.add_cid_to_collection(cid, male_collection_id)
    elif collection == 'female':
        resp = estuary.add_cid_to_collection(cid, female_collection_id)
    elif collection == 'child':
        resp = estuary.add_cid_to_collection(cid, child_collection_id)
    else:
        app.logger.warn("Unknown collection %s", collection)

    return jsonify(resp)
