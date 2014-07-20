import os
import urllib3
from flask import Flask, request, json

from flask.ext import restful
from flask.ext.jsonpify import jsonify

from inputValidatorConverter import validateAndConvert

app = Flask(__name__)
api = restful.Api(app)

class startjob(restful.Resource):
    def post(self):
        json_input = request.get_json(force=True)
        print json_input
        pyinput = validateAndConvert(json_input)
        print pyinput
        return pyinput

api.add_resource(startjob, '/startjob')

if __name__ == '__main__':
    #app.run(debug=True)
    #for debugging
    print 'lol'