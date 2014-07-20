import os
import urllib3
from flask import Flask, request, json

from flask.ext import restful
from flask.ext.jsonpify import jsonify

app = Flask(__name__)
api = restful.Api(app)

class startjob(restful.Resource):
    def post(self, ID):
        json_data = request.get_json(force=True)
        return None

api.add_resource(merge, '/startjob')

if __name__ == '__main__':
    #app.run(debug=True)
    #for debugging
    print 'lol'