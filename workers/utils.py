import yaml
import uuid

import yaml,json
import os
from pathlib import Path
import sys, traceback
import uuid
## aws
import boto3
from botocore.exceptions import ClientError

def load_configuration():
    return yaml.safe_load(open('../config.yml','r'))

def get_uuid():
    return str(uuid.uuid4())
### download file

class AWS_S3:
    def __init__(self, config):
        self.config=config
        self.tempDirectory=Path(self.config['TEMP_DIRECTORY'])
        os.environ['AWS_ACCESS_KEY_ID']=self.config['AWS_ACCESS_KEY_ID']
        os.environ['AWS_SECRET_ACCESS_KEY']=self.config['AWS_SECRET_ACCESS_KEY']
        os.environ['AWS_DEFAULT_REGION']=self.config['AWS_DEFAULT_REGION']
        self.bucket_name=self.config['S3_BUCKET_NAME']
        self.aws_s3=boto3.client('s3')
        # self.aws_resource = boto3.resource('s3')
        self.initialize()

    def initialize(self):
        ## make directory
        self.tempDirectory.mkdir(parents=True,exist_ok=True)       

    def getFileObject(self,filename, overwrite=False):
        try:
          tf = self.checkFileExist(filename)
          temp_outpath=self.tempDirectory.joinpath(filename)
          if tf:
            if temp_outpath.exists() and not overwrite: return str(temp_outpath)
            temp_outpath.parent.mkdir(parents=True, exist_ok=True)
            f=open(temp_outpath,'wb+')
            self.aws_s3.download_fileobj(self.bucket_name,filename,f)
            f.close()
            return str(temp_outpath)
          else: 
            if temp_outpath.exists() and not overwrite: return str(temp_outpath)
        except Exception as e:
          print(e)
          return False

    def getFileList(self,root_path): #get all pages
        bucket_name = self.bucket_name
        paginator=self.aws_s3.get_paginator('list_objects')
        operation_parameters = {'Bucket': bucket_name,
                                'Prefix': root_path}
        page_iterator=paginator.paginate(**operation_parameters)
        res=[]
        for p in page_iterator:
            if 'Contents' in p:
                temp=[f['Key'] for f in p['Contents']]
                res+=temp
        return res 

    def checkFileExist(self, filepath):
        try:
            self.aws_s3.head_object(Bucket=self.bucket_name, Key=filepath)
            return True
        except ClientError as e:
            return False
          
          
    def uploadFile(self,filename,output_key,meta=None):
        temp_outpath=self.tempDirectory.joinpath(filename)
        ### move the file to s3
        self.aws_s3.upload_file(str(filename),self.bucket_name,output_key)
        return output_key

