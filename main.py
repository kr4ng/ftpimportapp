'''
Internal REST API main file. Procfile references this file.
When a post request is made to /startjob, this code runs to 
start a worker thread to grab a csv file and push it to Marketo.
'''

import os

#Flask imports for restful, json and requesting data from the post
from flask import Flask, request, json

from flask.ext import restful
from flask.ext.jsonpify import jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from threading import Thread

#These are the transfer functions
from ftpconnector import Csvreader
from s3connector import S3manipulator
from ftptomkto import FtpToMktoTransfer

#This is the Job model and the schema validator functions
from models import Job
import inputValidatorConverter
from inputValidatorConverter import validateAndConvert

app = Flask(__name__)
#start the database
#postgres://bfrvhaxkuagzhn:FPIYxY8n7By_1A-Oqovlhah_8g@ec2-54-197-250-40.compute-1.amazonaws.com:5432/d2qsuiqdvbg6an
#postgres://localhost:5432/rightstackftp
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "postgres://bfrvhaxkuagzhn:FPIYxY8n7By_1A-Oqovlhah_8g@ec2-54-197-250-40.compute-1.amazonaws.com:5432/d2qsuiqdvbg6an")
db = SQLAlchemy(app)

api = restful.Api(app)

class startjob(restful.Resource):
    def post(self):
        '''
        Main API for starting a CSV to Marketo Transfer Job
        '''
        #store payload as dictionary
        json_input = request.get_json(force=True)
        #validate against schema, pyinput is a dictionary
        pyinput = validateAndConvert(json_input)
        #write to database
        newjob = Job(pyinput['customerId'], "Job Started", bigIn=pyinput)
        db.session.add(newjob)
        db.session.commit()
        #start worker
        #getjob=Job.query.filter_by(customerId=pyinput['customer'])
        worker=Thread(target=transfer, args=(newjob,pyinput))
        worker.daemon=False
        worker.start()
        return jsonify(jobId=newjob.id, status=newjob.status)

api.add_resource(startjob, '/startjob')

def transfer(job, pyinput):
    '''
    :inputs - job is of model Job
    :       - pyinput is a dictionary of which creds are a part of it.
    :       - Creds - {"url":"ftp.marketosolutionsconsulting.com", "username":"marketos", 
    :                  "password":"$C_rockst@r5", "path":"rightstack.csv", "csvtype": "standardtable"}
    :This function takes a job and a dictionary and 
    :executes the transfer of data to Marketo.
    :Todo - Work on set different job status's based on outcomes for debugging in the UI to
    :improve overall customer UX.
    '''
    creds = pyinput['ftp']
    reader = Csvreader(creds)
    ftptomkto=FtpToMktoTransfer(pyinput['mkto'],pyinput['map'], reader)
    ftptomkto.startTransfer()
    reader.endconnection()
    reader.delete_file()
    job.setStatus('Job Complete')
    db.session.add(job)
    db.session.commit()
    return None

if __name__ == '__main__':
    app.run(debug=True)
    #for debugging
    #print 'rightStack LLC'