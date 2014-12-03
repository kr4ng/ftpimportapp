'''
S3 Manipulator Class - An object to handle creating boto connections
and manipulating CSV files.
bucket location - rightstackftp.s3-website-us-west-2.amazonaws.com
'''
import time
import boto
from datetime import datetime

from boto.s3.connection import S3Connection
from boto.s3.connection import Location
from boto.s3.key import Key

class S3manipulator(object):
    '''
    Creating an instance of the S3manipulator will connect you to
    an instance of S3 based on your applications AWS KEYS.  The 
    class contains functions for creating a bucket, storing data in a bucket,
    and fetching a file from a bucket as a boto data file.
    '''
    #main connection
    conn = None
    #accountname of the customer using the rightstackftp
    accountname = None
    #initialize an empty S3 bucketobject and bucketname
    bucketobject = None
    bucketname = None
    #initialize an empty fileobject and filename
    fileobject = None
    filename = None
    #AWS Keys which will become global environment variables
    #insert here

    def __init__(self, accountname, awskey=None, awssecretkey=None):
        '''
        :open a connection and create a new bucketname for the account
        :an accountname will propagate throughtout all the files
        :in the s3 bucket.
        :inputs - accountname
        :returns - None
        '''
        if awskey:
            self.AWS_ACCESS_KEY_ID = awskey
        if awssecretkey:
            self.AWS_ACCESS_KEY_ID = awskey
        if accountname:
            #initialize the accountname and bucketname for this connection
            self.accountname = accountname
            ts = time.time()
            currenttime = datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
            self.bucketname = self.accountname + currenttime 
        self.conn = S3Connection(self.AWS_ACCESS_KEY_ID, self.AWS_SECRET_ACCESS_KEY)

    def create_bucket(self):
        '''
        :Create a new bucket for an account with structure str(accountname+timestamp).
        :inputs - None
        :returns - a boto Bucket Object <Bucket: accountname2014-07-09>
        '''
        bucket = self.conn.create_bucket(self.bucketname)
        self.bucketobject = bucket
        #bucket example <Bucket: accountname2014-07-19>
        return bucket

    def store_data(self, newfilesname=None, pathtofile=None, filetype='CSV'):
        '''
        :stores data in an S3 bucket.  create_bucket is run if bucket != exist
        :inputs - newfilesname = name of the file to store in the bucket
                  pathtofile = path to the file we are storing in the bucket
        :returns - a boto Key object <Key: bucketname, newfilesname>
        '''
        if self.bucketobject == None:
            #create a bucket if does not already exist
            self.create_bucket()
        #create key with S3manipulator.bucketname
        k = Key(self.conn.get_bucket(self.bucketname))
        #>>>print k >>> <Key: accountname2014-07-19,None>
        if newfilesname == None:
            k.key = self.bucketname
            self.filename = self.bucketname
        else:
            k.key = newfilesname
            self.filename = newfilesname
        k.set_contents_from_filename(pathtofile) #<Key: accountname2014-07-19,accountname2014-07-19>
        return k
       
    def fetch_file_from_bucket(self, *filename):
        '''
        :inputs - filename as string is optional
        :         no filename means we get the globalfilename self.filename
        :returns - file as boto object #<boto.s3.bucketlistresultset.BucketListResultSet object at 0x10c287150>
        '''
        b = self.conn.get_bucket(self.bucketname)
        if filename:           
            self.fileobject = b.list(filename)
        elif self.filename:
            self.fileobject = b.list(self.filename)
        else:
            print 'No filename given and store data has never been called for this connection'
        return self.fileobject

    def delete_bucket(self, *bucketname):
        '''
        :deletes the bucket associated with the latest connection
        :inputs - (optional) - bucketname - to deleter a different bucket TODO
        '''
        full_bucket = self.conn.get_bucket(self.bucketname)
        for key in full_bucket.list():
            key.delete()
        self.conn.delete_bucket(self.bucketname)
        return None

if __name__ == '__main__':
    a = S3manipulator('lulzsec')
    a.create_bucket()
    '''
    #key = s3.get_bucket('media.yourdomain.com').get_key('examples/first_file.csv')
    #key.get_contents_to_filename('/myfile.csv')
    '''
