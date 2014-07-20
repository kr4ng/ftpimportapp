import os

from flask import Flask, request, json

from flask.ext import restful
from flask.ext.jsonpify import jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from threading import Thread

from ftpconnector import Csvreader
from s3connector import S3manipulator

#from models import

from models import Job
import inputValidatorConverter
from inputValidatorConverter import validateAndConvert

app = Flask(__name__)
#start the database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "postgres://localhost:5432/rightstackftp")
db = SQLAlchemy(app)

api = restful.Api(app)

class startjob(restful.Resource):
    def post(self):
        #store payload as dictionary
        json_input = request.get_json(force=True)
        #validate against schema, pyinput is a dictionary
        pyinput = validateAndConvert(json_input)
        newjob = Job(pyinput['customerId'], "Job Started", bigIn=pyinput)
        db.session.add(newjob)
        db.session.commit()
        #getjob=Job.query.filter_by(customerId=pyinput['customer'])
        worker=Thread(target=transfer, args=(newjob,pyinput))
        worker.daemon=False
        worker.start()
        return jsonify(jobId=newjob.id, status=newjob.status)

api.add_resource(startjob, '/startjob')

def transfer(job, pyinput):
    '''
    This is a test of the following:
    1. open an FTP connection
    2. grab file and store it locally (ephermeral heroku memory)
    3. open s3 connection
    4. take local file and add it to s3bucket
    5. delete local file
    '''
    creds = pyinput['ftp']
    #creds = {"url":"ftp.marketosolutionsconsulting.com", "username":"marketos", "password":"$C_rockst@r5", "path":"rightstack.csv"}
    #Create a new Csvreader
    reader = Csvreader(creds)
    #use the readers ftp to tmp folder file transfer method
    localfilepath = reader.ftpcsv2tmpcsv()
    #kill the readers connection to ftp
    reader.endconnection()
    #Create a new S3manipulator
    a = S3manipulator(pyinput['customerName'].lower().replace(' ',''))
    #Create bucket
    a.create_bucket()
    #Store data in bucket
    a.store_data(pathtofile=localfilepath)
    #Delete temp file
    #reader.delete_file()
    job.setStatus('S3 Transfer Complete')
    db.session.add(job)
    db.session.commit()
    #open file on S3
    #bucketobject = a.fetch_file_from_bucket()
    #contents = key.get_contents_as_string()
    print contents
    '''
    for e in bucketobject.list(prefix=bucketobject.filename):
         unfinished_line = 
         for byte in e:
            print byte
            
            byte = unfinished_line + byte
            #split on whatever, or use a regex with re.split()
            lines = byte.split()
            unfinished_line = lines.pop()
            for line in lines:
                yield line
            
    '''
    #Delete bucket
    a.delete_bucket()
    return None

if __name__ == '__main__':
    app.run(debug=True)
    #for debugging
    #print 'lol'