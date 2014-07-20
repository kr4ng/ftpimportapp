"""
Input Validator/Converter
"""
import json
from jsonschema import validate

def validateAndConvert(newRequest):
	schema = {
		"type":"object",
		"properties":{
			"customer":{"type": "number"},
			"ftp":{
				"type":"object",
				"properties":{
					"url":{"type": "string"},
					"username":{"type": "string"},
					"password":{"type": "string"},
					"path":{"type": "string"}
				}
			},
			"mkto":{
				"type":"object",
				"properties":{
					"credentials":{
						"type":"object",
						"properties":{
							"url":{"type": "string"},
							"userid":{"type": "string"},
							"encryptionkey":{"type": "string"}
						}
					},
					"program":{"type": "string"},
					"list":{"type": "string"}
				}
			},
			"map":{
				"type":"array",
				"items":{
					"type":"object",
					"properties":{
						"ftp":{"type":"string"},
						"mkto":{"type": "string"}
					}
				}
			}
		}
	}
	try:
		pyNewRequest=json.loads(newRequest)
		validate(pyNewRequest, schema)
		return pyNewRequest
	except:
		#print "You Goofed"
		return False