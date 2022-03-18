import os

from flask import Flask, jsonify
import requests

app = Flask(__name__)


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


def construct_url(cid):
    return "https://" + cid + ".ipfs.dweb.link"


estuary = EstuaryData()


@app.route("/data/list")
def list_data():
    data = estuary.list_data()
    response = jsonify([construct_url(datum["cid"]["/"]) for datum in data])
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
