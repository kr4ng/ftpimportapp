"""
This is the Marketo Connector ripped mostly from the segment.io marketo library
"""

import requests
import mktoauth
#import get_lead
import logging
import httplib

httplib.HTTPConnection.debuglevel = 1

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True


class Client:

	def __init__(self, soap_endpoint=None, user_id=None, encryption_key=None):

		if not soap_endpoint or not isinstance(soap_endpoint, str):
			raise ValueError('Must supply a soap_endpoint as a non empty string.')

		if not user_id or not isinstance(user_id, (str, unicode)):
			raise ValueError('Must supply a user_id as a non empty string.')

		if not encryption_key or not isinstance(encryption_key, str):
			raise ValueError('Must supply a encryption_key as a non empty string.')

		self.soap_endpoint = soap_endpoint
		self.user_id = user_id
		self.encryption_key = encryption_key

	def wrap(self, body):
		return (
			'<?xml version="1.0" encoding="UTF-8"?>' +
			'<env:Envelope xmlns:xsd="http://www.w3.org/2001/XMLSchema" ' +
						  'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' +
						  'xmlns:wsdl="http://www.marketo.com/mktows/" ' +
						  'xmlns:env="http://schemas.xmlsoap.org/soap/envelope/" ' +
						  'xmlns:ins0="http://www.marketo.com/mktows/" ' +
						  'xmlns:ns1="http://www.marketo.com/mktows/" ' +
						  'xmlns:mkt="http://www.marketo.com/mktows/">' +
				mktoauth.header(self.user_id, self.encryption_key) +
				'<env:Body>' +
					body +
				'</env:Body>' +
			'</env:Envelope>')

	def request(self,body):
		envelope=self.wrap(body)
		flog=open('tmp/mktolog.xml', 'w+')
		flog.write(envelope)
		flog.close()
		response = requests.post(self.soap_endpoint, data=envelope,
			headers={
				'Connection': 'Keep-Alive',
				'Soapaction': '',
				'Content-Type': 'text/xml;charset=UTF-8',
				'Accept': '*/*'})
		if response.status_code == 200:
			return response
		else:
			raise Exception(response.text)