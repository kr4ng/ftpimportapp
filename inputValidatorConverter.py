"""
Input Validator/Converter
"""
import json
from jsonschema import validate

def validateAndConvert(newRequest):
	schema = {
		"type":"object",
		"properties":{
			"customerId":{"type": "number"},
			"customerName":{"type": "string"},
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
					"list":{"type": "string"},
					"targetobject":{"type": "string"}
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
		validate(newRequest, schema)
		return newRequest
	except:
		return False