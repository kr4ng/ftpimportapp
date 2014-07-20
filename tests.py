'''
This is a test of the following:
1. open an FTP connection
2. grab file and store it locally (ephermeral heroku memory)
3. open s3 connection
4. take local file and add it to s3bucket
5. delete local file
'''
if __name__ == '__main__':
    from ftpconnector import Csvreader
    from s3connector import S3manipulator

    creds = {"url":"ftp.marketosolutionsconsulting.com", "username":"marketos", "password":"$C_rockst@r5", "path":"rightstack.csv", "account":'generalmotors'}
    #Create a new Csvreader
    reader = Csvreader(creds)
    #use the readers ftp to tmp folder file transfer method
    localfilepath = reader.ftpcsv2tmpcsv()
    #kill the readers connection to ftp
    reader.endconnection()
    #Create a new S3manipulator
    a = S3manipulator(creds['account'])
    #Create bucket
    a.create_bucket()
    #Store data in bucket
    a.store_data(pathtofile=localfilepath)
    #Delete temp file
    reader.delete_file()
    #Delete bucket
    #a.delete_bucket()