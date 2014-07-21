'''
ftpconnector class
'''
import ftplib

class Ftpconnector(object):
    #open up the most basic connection with no credentials
    ftp = ftplib.FTP()

    def __init__(self, *args):
        '''
        :Initializes an ftp connection based on a username, password, and
        :ftpsite location
        :inputs - args from a child object like Csvreader
        :returns - none
        '''
        self.ftpsite = args[0]['url']
        self.username = args[0]['username']
        self.password = args[0]['password']
        self.debug=True
        if self.ftpsite and self.username and self.password:
            self.ftp.connect(self.ftpsite)
            self.ftp.login(self.username, self.password)
        else:
            print 'Cannot Connect to FTP: Missing Credentials'

    def endconnection(self):
        '''
        :Kills the current Ftp connection
        :inputs: None
        :return: None
        '''
        self.ftp.quit()

class Csvreader(Ftpconnector):
    '''
    :When a new Csvreader is instantiated, an Ftpconnection is created, and
    :the path to where the file on the ftp is set as <path>, and the
    :tempfilename that will be stored in the heroku app before being
    :stored on s3 is called <tempfilename>

    :Csv reader has a method to end connections and a method to take an
    :ftp csv and store it in a temp csv with a standard or customizable path
    '''
    #tempfilename - filename of local csv
    #path - path to csv file on the ftpsite
    tempfilename = None
    path = None

    def __init__(self, *args):
        '''
        :Initializes a new Csvreader object. args needs to have at least the following:
        :inputs - {"url":"ftp.marketosolutionsconsulting.com", "username":"marketos", 
                   "password":"$C_rockst@r5", "path":"rightstack.csv"}
        :return - None
        '''
        super(self.__class__, self).__init__(*args)
        if args[0]['path']:
            self.path = args[0]['path']
            self.tempfilename = self.username
            self.localpath='tmp/' + self.tempfilename + '.csv'
            self.filesize=self.ftp.size(self.path)
            if self.debug:
                print self.filesize
        else:
            print 'No path specified. Cannot Initialize'

    def delete_file(self):
        '''
        :deletes the current temp file
        :inputs - None
        :return - None
        '''
        import os
        os.remove("tmp/" + self.tempfilename + '.csv')     

    def ftpcsv2tmpcsv(self, rest=0):
        '''
        :input - *folder - if specified then the path of the csv that will
                           be stored local before going to s3 will not be
                           tmp/self.tempfilename it will be folder/self.tempfilename
        :return - the relative path for use by the s3connector
        '''
        self.ftp.retrbinary("RETR " + self.path,open(self.localpath, 'wb').write) #maybe add REST command
        return self.localpath
        #else:
        #    self.ftp.retrbinary("RETR " + self.path ,open(folder + self.tempfilename + '.csv', 'wb').write, rest=rest)
        #    return folder + self.tempfilename + '.csv'

    def tmpcsvhelper(self, chunk):
        open(self.localpath, 'wb').write(chunk)

    def executeByChunk(self, callbackFunc, chunksize):
        '''
        This is a wrapper for the retrBinary method using chunks
        '''
        self.ftp.retrbinary("RETR " + self.path, callbackFunc) ##REMOVED CHUNKSIZE PARAM FOR DEBUG

if __name__ == '__main__':
    creds = {"url":"ftp.marketosolutionsconsulting.com", "username":"marketos", "password":"$C_rockst@r5", "path":"rightstack.csv"}
    reader = Csvreader(creds)
    localfilepath = reader.ftpcsv2tmpcsv()
    reader.endconnection()
    reader.deletefile()

    '''
    filename = 'rightstack.csv'
    ftp = ftplib.FTP("ftp.marketosolutionsconsulting.com") 
    ftp.login("marketos", "$C_rockst@r5") 
    ftp.retrbinary("RETR " + filename ,open('tmp/' + filename, 'wb').write)
    ftp.quit()
    '''

