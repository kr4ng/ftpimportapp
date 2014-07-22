"""
DB Connector
"""
import json
from datetime import datetime
from flask.ext.sqlalchemy import SQLAlchemy


from flask import Flask
import os
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "postgres://bfrvhaxkuagzhn:FPIYxY8n7By_1A-Oqovlhah_8g@ec2-54-197-250-40.compute-1.amazonaws.com:5432/d2qsuiqdvbg6an")


db=SQLAlchemy(app)

class Job(db.Model):
	__tablename__ = "job"
	id = db.Column(db.Integer, primary_key=True)
	customerId = db.Column(db.Integer)
	customername = db.Column(db.String(30))
	status = db.Column(db.String(20))
	#ftpId = db.Column(db.Integer)
	ftpUsername = db.Column(db.String(20))
	ftpPassword = db.Column(db.String(20))
	ftpURL = db.Column(db.String(60))
	ftpPath = db.Column(db.String(80))
	#mktoId = db.Column(db.Integer)
	mktoUserId = db.Column(db.String(60))
	mktoKey = db.Column(db.String(60))
	mktoEndpoint = db.Column(db.String(60))
	mktoProgram = db.Column(db.String(30))
	mktoList = db.Column(db.String(30))
	map = db.Column(db.String(1000))
	start = db.Column(db.DateTime)
	done = db.Column(db.DateTime)
	tag = db.Column(db.String(20))
	
	def __init__(self, customerId, status, bigIn=None, tag=None):
		self.customerId=customerId
		self.status=status
		self.tag=tag
		self.setBigIn(bigIn)
		self.start=datetime.now()
	
	def __repr__(self):
		return '<Job %r>' % self.id
	
	def setStatus(self, status):
		self.status=status
		
	def setBigIn(self, bigIn):
		if bigIn is None:
			pass
		else:
			self.customername=bigIn['customerName']
			self.ftpUsername=bigIn['ftp']['username']
			self.ftpPassword=bigIn['ftp']['password']
			self.ftpURL=bigIn['ftp']['url']
			self.ftpPath=bigIn['ftp']['path']
			self.mktoUserId=bigIn['mkto']['credentials']['userid']
			self.mktoKey=bigIn['mkto']['credentials']['encryptionkey']
			self.mktoEndpoint=bigIn['mkto']['credentials']['url']
			self.mktoProgram=bigIn['mkto']['program']
			self.mktoList=bigIn['mkto']['list']
			self.map = json.dumps(bigIn['map'])

if __name__=="__main__":
	from flask import Flask
	import os
	app = Flask(__name__)
	app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "postgres://bfrvhaxkuagzhn:FPIYxY8n7By_1A-Oqovlhah_8g@ec2-54-197-250-40.compute-1.amazonaws.com:5432/d2qsuiqdvbg6an")

	db=SQLAlchemy(app)
	db.create_all()
		