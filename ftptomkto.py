'''
This file houses the FtpToMktoTransfer class.
With this object you can start transfers into marketo from a CSV.
'''

import pymarketo
from pymarketo import mktoclasses

import csv
import sys

from xml.sax.saxutils import escape

class FtpToMktoTransfer(object):
    def __init__(self, mkto, mapIn, reader):
        '''
        :inputs - mkto, mapIn, reader with examples as follows:
        :mkto = { "credentials":{ "url":"https://939-LPS-822.mktoapi.com/soap/mktows/2_3", 
        :                        "userid":"mktodemoaccount1961_3786898253485E77E66916", 
        :                        "encryptionkey":"52545396568742865533448855EE7789EE66772CE512" }, 
        :                        "program":"testing", 
        :                        "list":"TestList" 
        :                        }
        :mapIn = [ { "ftp":"First name", "mkto":"First Name" },
        :           { "ftp": "Email", "mkto": "Email Address" },
        :           {"ftp":"Company", "mkto":"Company Name"},
        :           {"ftp":"Address", "mkto":"Address"} 
        :           ]
        :reader = Csvreader(creds) #Csvreader is a subclass of Ftpconnector 
        :                           #and is used to establish a connection to an FTP with CSVs
        :creds = {"url":"ftp.marketosolutionsconsulting.com", 
        :          "username":"marketos", 
        :          "password":"$C_rockst@r5", 
        :          "path":"rightstackcustomobject.csv",
        :          "csvtype":"customtable"
        :          }
        :Constructor for FtpToMktoTransfer. When instantiated, the csvtype will determine
        :the marketo call that will be used in the mktoclasses.py
        :Other Notes:
        :self.oldpart = incomplete line temp storage
        :self.csvtype = reader.csvtype which comes from the json which will either be customtable or standardtable
        '''
        self.oldpart='' ##INCOMPLETE LINE TEMP STORAGE
        ##Instance new Marketo Connection and list
        mktocreds=mkto['credentials']
        self.csvtype=reader.csvtype
        self.mktoClient=pymarketo.Client(str(mktocreds['url']), str(mktocreds['userid']), str(mktocreds['encryptionkey']))
        if self.csvtype == 'customtable':
            self.mktoCustomObject=mktoclasses.MktoCustomObject(self.mktoClient)
        else:
            self.mktoList=mktoclasses.MktoList(self.mktoClient, mkto['program'], mkto['list'])
        ##Set Header flag and map
        self.gotHeader=False
        self.map=mapIn
        self.newline='\r'
        self.reader=reader
        self.currentbytes=0
        ## DEBUG FLAG !!
        self.debug=True
        if self.debug:
            self.callnum=0
    
    def customObjectCsvToMkto(self, csvfile):
        '''
        :inputs - csvfile as tmpfile=open(self.reader.localpath, 'rU')
        :returns - True
        :This function takes a csvfile and loops through each row
        :and calls the MktoCustomObject class to build the XML and send it to
        :Marketo 100 rows of the custom object at a time.
        :extra dependencies - import csv
        '''
        count = 0
        reader=csv.reader(csvfile)
        for row in reader:
            if not self.gotHeader:
                self.mktoCustomObject.setNames(row)
                self.gotHeader=True
            else:
                self.mktoCustomObject.addOneCustomObjectRow(row)
            count += 1
            if count > 99:
                self.mktoCustomObject.testXML() #TOREPLACE - this emulates sending it to marketo instead of actually sending
                self.mktoCustomObject.customobjectxml = ''
                count = 0
                print 'batch complete'
        return True

    def chunkToMkto(self, chunk):
        '''
        :input - chunk is an open csvfile
        :So it isn't an object it is actually an opened chunk.
        :returns - True
        :This function takes an open csvfile and replaces newlines with the
        :xml required to then send to Marketo, then it calls MktoList class
        :submit() method to send it to Marketo 50 Mbs at a time.
        '''
        ##Pull first line of the first chunk and make it a Marketo friendly header (fieldnames)
        if not self.gotHeader:
            chunks=chunk.split(self.newline, 1)  ##Split off first line
            mktoheader=self.csvHeaderToMarketoMap(chunks[0])
            self.mktoList.setFieldNames(mktoheader) ##Set mktoList object Headers using map
            chunk=chunks[1] ##Reset input to not include headers
            self.gotHeader=True ##Set flag so that this all doesn't happen again
        if self.debug:
            flog=open('tmp/chunklog'+str(self.callnum)+'.csv', "w+")
            flog.write(chunk)
            flog.close()
            self.callnum+=1
        chunks=chunk.rsplit(self.newline,1) ## - !!! - THIS WILL DROP THE LAST ROW OF THE FILE IF IT DOESNT END WITH \n
        newMessage=escape(self.oldpart+chunks[0]) ##Prepend last incomplete line to current message
        self.oldpart=chunks[1] ##Store incomplete from end of message (or '' if file at end)
        self.mktoList.rows="<stringItem>"+newMessage.replace(self.newline, '</stringItem><stringItem>')+"</stringItem>" ##Replace newline with xml tags
        self.mktoList.submit() ##Send Full Message for chunk to Marketo
        return True

    def startTransfer(self):
        '''
        :inputs - None, but requires successful instantiation of the class
        :When called, this starts transfer of a csvfile into Marketo. This is the loop
        :which then calls chunkToMkto or customObjectCsvToMkto if the csvtype is custom.
        :This is the Main Loop.
        '''
        if self.csvtype == 'customtable':
            while self.currentbytes<=self.reader.filesize:
                print 'in loop'
                self.reader.ftpcsv2tmpcsv(rest=self.currentbytes)
                tmpfile=open(self.reader.localpath, 'rU')
                self.customObjectCsvToMkto(tmpfile)
                tmpfile.close()
                self.currentbytes=self.reader.filesize+1
        else:
            while self.currentbytes<=self.reader.filesize:
                self.reader.ftpcsv2tmpcsv(rest=self.currentbytes)
                tmpfile=open(self.reader.localpath, 'r')
                self.chunkToMkto(tmpfile.read())
                tmpfile.close()
                self.currentbytes=self.reader.filesize+1 ##EVENTUALLY CONVERT THIS TO ITERATE THROUGH A BIG FILE

    def csvHeaderToMarketoMap(self, csvheader):
        '''
        :inputs - csvheader = "name1,name2,name3.../n"
        :This function replaces the csvheaders with the headers specified in the map.
        :sample map - [ { "ftp":"First name", "mkto":"First Name" },{ "ftp": "Email", "mkto": "Email Address" },
                        {"ftp":"Company", "mkto":"Company Name"},{"ftp":"Address", "mkto":"Address"} ]
        '''
        mktoheader=csvheader
        #loop through the map defined by the json and
        #replace the CSV fieldname with the Mkto Friendly Name
        for fieldmap in self.map:
            mktoheader=mktoheader.replace(fieldmap['ftp'], fieldmap['mkto']) ##Replace FTP fieldname with Mkto Fieldname
        return mktoheader

if __name__ == '__main__':
    '''
    Test taking a local file and testing customObjectCsvToMkto
    mkto = { "credentials":{ "url":"https://939-LPS-822.mktoapi.com/soap/mktows/2_3", "userid":"mktodemoaccount1961_3786898253485E77E66916", "encryptionkey":"52545396568742865533448855EE7789EE66772CE512" }, "program":"testing", "list":"TestList" }
    mapIn = [ { "ftp":"First name", "mkto":"First Name" },{ "ftp": "Email", "mkto": "Email Address" },{"ftp":"Company", "mkto":"Company Name"},{"ftp":"Address", "mkto":"Address"} ]
    reader = Csvreader(creds)
    creds = {"url":"ftp.marketosolutionsconsulting.com", "username":"marketos", "password":"$C_rockst@r5", "path":"rightstackcustomobject.csv"}
    '''
    mkto = { "credentials":{ "url":"https://939-LPS-822.mktoapi.com/soap/mktows/2_3", "userid":"mktodemoaccount1961_3786898253485E77E66916", "encryptionkey":"52545396568742865533448855EE7789EE66772CE512" }, "program":"testing", "list":"TestList" }
    mapIn = [ { "ftp":"First name", "mkto":"First Name" },{ "ftp": "Email", "mkto": "Email Address" },{"ftp":"Company", "mkto":"Company Name"},{"ftp":"Address", "mkto":"Address"} ]
    creds = {"url":"ftp.marketosolutionsconsulting.com", "username":"marketos", "password":"$C_rockst@r5", "path":"rightstackcustomobject.csv", "csvtype":"customtable"}
    from ftpconnector import Csvreader
    reader = Csvreader(creds)
    ftptomkto = FtpToMktoTransfer(mkto, mapIn, reader)
    ftptomkto.startTransfer()
