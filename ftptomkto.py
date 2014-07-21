import marketoCon
import mktolist
import mktoauth
from xml.sax.saxutils import escape

class FtpToMktoTransfer(object):
    def __init__(self, mkto, mapIn, reader):
        self.oldpart='' ##INCOMPLETE LINE TEMP STORAGE
        ##Instance new Marketo Connection and list
        mktocreds=mkto['credentials']
        self.mktoClient=marketoCon.Client(str(mktocreds['url']), str(mktocreds['userid']), str(mktocreds['encryptionkey']))
        self.mktoList=mktolist.MktoList(self.mktoClient, mkto['program'], mkto['list'])
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
    
    def chunkToMkto(self, chunk):
        ##Pull first line of the first chunk and make it a Marketo friendly header (fieldnames)
        if not self.gotHeader:
            chunks=chunk.split(self.newline, 1)  ##Split off first line
            mktoheader=self.csvHeaderToMarketoMap(chunks[0])
            self.mktoList.setFieldNames(mktoheader) ##Set MktoList object Headers using map
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
        while self.currentbytes<=self.reader.filesize:
            self.reader.ftpcsv2tmpcsv(rest=self.currentbytes)
            tmpfile=open(self.reader.localpath, 'r')
            self.chunkToMkto(tmpfile.read())
            tmpfile.close()
            self.currentbytes=self.reader.filesize+1 ##EVENTUALLY CONVERT THIS TO ITERATE THROUGH A BIG FILE

    def csvHeaderToMarketoMap(self, csvheader):
        mktoheader=csvheader ##Reassign input for manipulation
        for fieldmap in self.map: ##Iterate through field map list
            mktoheader=mktoheader.replace(fieldmap['ftp'], fieldmap['mkto']) ##Replace FTP fieldname with Mkto Fieldname
        return mktoheader