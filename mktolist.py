"""
Import to List Wrapper
"""
import xml.etree.ElementTree as ET

class MktoList:
	def __init__(self, client, programName=None, listName=None, fieldnames=None):
		self.fieldNames=fieldnames
		self.rows=""
		self.client=client
		self.programName=programName
		self.listName=listName
		self.debug=False
	
	def submit(self):
		body = ("<ns1:paramsImportToList>" +
					"<programName>" + self.programName + "</programName>" +
					"<importListMode>UPSERTLEADS</importListMode>" +
					"<listName>"+self.listName+"</listName>"+
					"<clearList>false</clearList>"+
					"<importFileHeader>"+self.fieldNames+"</importFileHeader>"+
					"<importFileRows>"+self.rows+"</importFileRows>"+
				"</ns1:paramsImportToList>")
		if self.debug:
			flog = open('tmp/mktolog.xml', 'w+')
			flog.write(body)
		response=self.client.request(body)
		root = ET.fromstring(response.text)
		return root.find('.//importStatus').text
		
	def addRow(self, row):
		self.rows+="<stringItem>"+row+"</stringItem>"
	
	def setFieldNames(self, fieldnames):
		self.fieldNames=fieldnames
		
	def setProgram(self, programName):
		self.programName=programName
		
	def setList(self, listName):
		self.listName=listName