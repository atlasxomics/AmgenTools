##################################################################################
### Module : storage.py
### Description : Storage API , AWS S3
###
###
###
### Written by : scalphunter@gmail.com ,  2021/08/04
### Copyrighted reserved by AtlasXomics
##################################################################################

### API
from flask import request, Response , send_from_directory
# import miscellaneous modules
import os
import io
import traceback
import json
from pathlib import Path
import csv 
import cv2
import gzip
import glob
import subprocess
from flask_cors import CORS
import datetime
import boto3
import subprocess
import time
## aws

from . import utils 

class StorageAPI:
    def __init__(self,app,**kwargs):
        self.app=app
        CORS(self.app)
        self.tempDirectory=Path(self.app.config['TEMP_DIRECTORY'])
        self.bucket_name=self.app.config['S3_BUCKET_NAME']
        self.initialize()
        self.initEndpoints()
    def initialize(self):
        ## make directory
        self.tempDirectory.mkdir(parents=True,exist_ok=True)

##### Endpoints

    def initEndpoints(self):
        @self.app.route('/api/v1/storage',methods=['GET'])
        def _getFileObject():
            sc=200
            res=None
            resp=None
            param_filename=request.args.get('filename',type=str)
            param_bucket=request.args.get('bucket_name',default=self.bucket_name,type=str)
            try:
                data_bytesio,size,_= self.getFileObject(param_bucket,param_filename)
                resp=Response(data_bytesio,status=200)
                resp.headers['Content-Length']=size
                resp.headers['Content-Type']='application/octet-stream'
            except Exception as e:
                exc=traceback.format_exc()
                res=utils.error_message("Exception : {} {}".format(str(e),exc),500)
                resp=Response(json.dumps(res),status=res['status_code'])
                resp.headers['Content-Type']='application/json'
            finally:
                return resp    
              
        @self.app.route('/api/v1/storage/image_as_jpg',methods=['GET'])
        def _getFileObjectAsJPG():
            sc=200
            res=None
            resp=None
            param_filename=request.args.get('filename',type=str)
            param_bucket=request.args.get('bucket_name',default=self.bucket_name,type=str)
            try_cache = request.args.get('use_cache', type=str, default='false')
            rotation = request.args.get('rotation', type=int, default=0)
            if try_cache == 'true':
                use_cache = True
            else:
                use_cache = False
            try:
                data_bytesio,_,size,_= self.getFileObjectAsJPG(bucket_name=param_bucket, filename= param_filename, try_cache= use_cache, rotation=rotation)
                resp=Response(data_bytesio,status=200)
                resp.headers['Content-Length']=size
                resp.headers['Content-Type']='application/octet-stream'
            except Exception as e:
                exc=traceback.format_exc()
                res=utils.error_message("Exception : {} {}".format(str(e),exc),500)
                resp=Response(json.dumps(res),status=res['status_code'])
                resp.headers['Content-Type']='application/json'
                print(res)
            finally:
                return resp

        @self.app.route('/api/v1/storage/png',methods=['GET'])
        def _getFileObjectAsPNG():
            sc=200
            res=None
            resp=None
            param_filename=request.args.get('filename',type=str)
            param_bucket=request.args.get('bucket_name',default=self.bucket_name,type=str)
            try:
                data_bytesio,_,size,_= self.getImage(param_bucket, param_filename)
                resp=Response(data_bytesio,status=200)
                resp.headers['Content-Type']='application/octet-stream'
            except Exception as e:
                exc=traceback.format_exc()
                res=utils.error_message("Exception : {} {}".format(str(e),exc),500)
                resp=Response(json.dumps(res),status=res['status_code'])
                resp.headers['Content-Type']='application/json'
            finally:
                return resp

        @self.app.route('/api/v1/storage/grayscale_image_jpg_cropping', methods=['GET'])
        def _getGrayImage():
            sc = 200
            res = None
            resp = None
            param_filename=request.args.get('filename',type=str)
            param_rotation=request.args.get('rotation', default=0, type=int)
            x1 = request.args.get('x1', type=int)
            x2 = request.args.get('x2', type=int)
            y1 = request.args.get('y1', type=int)
            y2 = request.args.get('y2', type=int)
            try:
                ata_bytesio,size = self.get_gray_image_rotation_cropping_jpg(param_filename, param_rotation, x1 = x1, x2 = x2, y1 = y1, y2 = y2)
                resp=Response(data_bytesio,status=200)
                resp.headers['Content-Length']=size
                resp.headers['Content-Type']='application/octet-stream'
            except Exception as e:
                exc=traceback.format_exc()
                res=utils.error_message("Exception : {} {}".format(str(e),exc),500)
                resp=Response(json.dumps(res),status=res['status_code'])
                resp.headers['Content-Type']='application/json'
            finally:
                return resp    
        
        @self.app.route('/api/v1/storage/json',methods=['GET']) ### return json object from csv file
        def _getJsonFromFile():
            sc=200
            res=None
            resp=None
            param_filename=request.args.get('filename',type=str)
            param_bucket=request.args.get('bucket_name',default=self.bucket_name,type=str)
            no_aws_yes_server = request.args.get('no_aws_yes_server', default = 'true')
            if no_aws_yes_server == 'false':
                no_aws_yes_server = False
            else:
                no_aws_yes_server = True
            try:
                res = self.getJsonFromFile(param_bucket,param_filename, no_aws_yes_server)
                resp=Response(json.dumps(res),status=200)
                resp.headers['Content-Type']='application/json'
            except Exception as e:
                exc=traceback.format_exc()
                res=utils.error_message("Exception : {} {}".format(str(e),exc),500)
                resp=Response(json.dumps(res),status=res['status_code'])
                resp.headers['Content-Type']='application/json'
            finally:
                return resp  

        @self.app.route('/api/v1/storage/csv',methods=['GET']) ### return json object from csv file
        def _getCsvFileAsJson():
            sc=200
            res=None
            resp=None
            param_filename=request.args.get('filename',type=str)
            param_bucket=request.args.get('bucket_name',default=self.bucket_name,type=str)
            no_aws_yes_server = request.args.get('no_aws_yes_server', default='true', type=str)
            if no_aws_yes_server == 'false':
                no_aws_yes_server = False
            else:
                no_aws_yes_server = True
            try:
                res = self.getCsvFileAsJson(param_bucket,param_filename, no_aws_yes_server)
                resp=Response(json.dumps(res),status=200)
                resp.headers['Content-Type']='application/json'
            except Exception as e:
                exc=traceback.format_exc()
                res=utils.error_message("Exception : {} {}".format(str(e),exc),500)
                resp=Response(json.dumps(res),status=res['status_code'])
                resp.headers['Content-Type']='application/json'
            finally:
                return resp    
  

        @self.app.route('/api/v1/storage/list',methods=['POST'])
        def _getFileList():
            sc=200
            res=None
            resp=None
            req = request.get_json()
            param_filename= req.get('path', "")
            param_bucket=req.get('bucket', self.bucket_name)
            print(param_bucket)
            param_filter=req.get('filter', None)
            param_delimiter = req.get('delimiter', None)
            only_files = req.get('only_files', False)
            try:
                data= self.getFileList(param_bucket,param_filename, param_filter, param_delimiter, only_files)
                resp=Response(json.dumps(data,default=utils.datetime_handler),status=200)
                resp.headers['Content-Type']='application/json'
            except Exception as e:
                exc=traceback.format_exc()
                res=utils.error_message("Exception : {} {}".format(str(e),exc),500)
                print(res)
                resp=Response(json.dumps(res),status=res['status_code'])
                resp.headers['Content-Type']='application/json'
            finally:
                return resp   

        @self.app.route('/api/v1/storage/sub_folders',methods=['POST'])
        def _getSubFolders():
            sc=200
            res=None
            resp=None
            req = request.get_json()
            param_bucket=req.get('bucket_name', self.bucket_name)
            param_prefix=req.get('prefix', "")
            try:
                data= self.get_subfolders(param_bucket, param_prefix)
                resp=Response(json.dumps(data,default=utils.datetime_handler),status=200)
                resp.headers['Content-Type']='application/json'
            except Exception as e:
                exc=traceback.format_exc()
                res=utils.error_message("Exception : {} {}".format(str(e),exc),500)
                print(res)
                resp=Response(json.dumps(res),status=res['status_code'])
                resp.headers['Content-Type']='application/json'
            finally:
                return resp   

        @self.app.route('/api/v1/storage/download_link',methods=['GET'])
        def _downloadFileByLink():
            sc=200
            res=None
            param_filename=request.args.get('filename',type=str)
            param_bucket=request.args.get('bucket_name',default=self.bucket_name,type=str)
            param_expiry=request.args.get('expiry', default=3600, type=int)
            try:
                res= self.downloadFile_link(param_bucket,param_filename, param_expiry)
                res= utils.result_message(res)
            except Exception as e:
                res=utils.error_message(str(e))
            finally:
                resp=Response(json.dumps(res),status=res['status_code'])
                resp.headers['Content-Type']='application/json'
                return resp
              
        @self.app.route('/api/v1/storage/download_link_public',methods=['GET'])
        def _downloadFileByLinkPublic():
            sc=200
            res=None
            param_filename=request.args.get('filename',type=str)
            param_bucket=request.args.get('bucket_name',default=self.bucket_name,type=str)
            try:
                res= self.downloadFile_link_public(param_bucket,param_filename)
                res= utils.result_message(res)
            except Exception as e:
                res=utils.error_message(str(e))
            finally:
                resp=Response(json.dumps(res),status=res['status_code'])
                resp.headers['Content-Type']='application/json'
                return resp
                     
###### actual methods

    def getFileObject(self,bucket_name,filename, no_aws_yes_server = True):
      _,tf,date,size=self.checkFileExists(bucket_name,filename)
      temp_outpath=self.tempDirectory.joinpath(filename)
      ext=Path(filename).suffix
      if not tf :
        if temp_outpath.exists() and no_aws_yes_server:
          f=open(temp_outpath, 'rb')
          bytesIO=io.BytesIO(f.read())
          size=os.fstat(f.fileno()).st_size
          f.close() 
          return bytesIO, ext, size , temp_outpath
        else: return utils.error_message("The file doesn't exists",status_code=404)
      else:
          if not temp_outpath.exists():
            temp_outpath.parent.mkdir(parents=True, exist_ok=True)
            f=open(temp_outpath,'wb+')
            subprocess.run(f"aws s3api get-object --bucket {bucket_name} --key {filename} {temp_outpath}", shell=True)
            bytesIO=io.BytesIO(f.read())
            size=os.fstat(f.fileno()).st_size
            f.close()
          else:
            modified_time = os.path.getmtime(temp_outpath)
            formatted = datetime.datetime.fromtimestamp(modified_time)
            if date.replace(tzinfo=None) > formatted and size > 0:
              f=open(temp_outpath,'wb+')
              subprocess.run(f"aws s3api get-object --bucket {bucket_name} --key {filename} {temp_outpath}", shell=True)
            else :
              f=open(temp_outpath, 'rb')
            bytesIO=io.BytesIO(f.read())
            size=os.fstat(f.fileno()).st_size
            f.close()
          return bytesIO, ext, size , temp_outpath

    def rotate_file_object(self, relative_path, degree):
        rel_path = Path(relative_path)
        path = self.tempDirectory.joinpath(rel_path)
        img = cv2.imread(path.__str__(), cv2.IMREAD_COLOR)
        img = self.rotate_image_no_cropping(img, degree)
        bytesIO = self.get_img_bytes(img)
        size_bytes = bytesIO.getbuffer().nbytes
        return bytesIO, size_bytes
    
    def get_img_bytes(self, img):
        success, encoded = cv2.imencode('.jpg', img)
        bytes = encoded.tobytes()
        bytesIO = io.BytesIO(bytes)
        return bytesIO

    def getFileObjectAsJPG(self,bucket_name,filename, try_cache, rotation):
        _,tf,date,size=self.checkFileExists(bucket_name,filename)
        temp_filename="{}".format(Path(filename))
        temp_outpath=self.tempDirectory.joinpath(temp_filename)
        ext=Path(filename).suffix
        if not tf :
            return utils.error_message("The file doesn't exists",status_code=404)
        if try_cache and temp_outpath.exists():
            img = cv2.imread(temp_outpath.__str__(), cv2.IMREAD_COLOR)
        else:
            if temp_outpath.exists() == False: temp_outpath.parent.mkdir(parents=True, exist_ok=True)
            f=open(temp_outpath,'wb+')
            subprocess.run(f"aws s3api get-object --bucket {bucket_name} --key {filename} {temp_outpath}", shell=True)
            f.close()
            img=cv2.imread(temp_outpath.__str__(),cv2.IMREAD_COLOR)
        if rotation != 0:
            img = self.rotate_image_no_cropping(img=img, degree=rotation)
        bytesIO = self.get_img_bytes(img)
        size = bytesIO.getbuffer().nbytes
        return bytesIO, ext, size , temp_outpath.__str__()
    
    def crop_image(self,img, x1, x2, y1, y2):
        return img[y1: y2, x1: x2]

    def get_gray_image_rotation_cropping_jpg(self, filename, rotation, x1, x2, y1, y2):
        rel_path = Path(filename)
        path = self.tempDirectory.joinpath(rel_path)
        img=cv2.imread(path.__str__(),cv2.IMREAD_COLOR)
        gray_img = img[:, :, 0]
        if rotation != 0:
            gray_img = self.rotate_image_no_cropping(gray_img, rotation)
        cropped = self.crop_image(gray_img, x1, x2, y1, y2)
        bytesIO = self.get_img_bytes(cropped)
        size = bytesIO.getbuffer().nbytes
        return bytesIO, size

    def get_gray_image_rotation_jpg(self, filename, rotation):
        rel_path = Path(filename)
        path = self.tempDirectory.joinpath(rel_path)
        img=cv2.imread(path.__str__(),cv2.IMREAD_COLOR)
        gray_img = img[:, :, 0]
        if rotation != 0:
            gray_img = self.rotate_image_no_cropping(gray_img, rotation)
        bytesIO = self.get_img_bytes(gray_img)
        size = bytesIO.getbuffer().nbytes
        return bytesIO, size

    def rotate_image_no_cropping(self, img, degree):
        (h, w) = img.shape[:2]
        (cX, cY) = (w // 2, h // 2)
        # rotate our image by 45 degrees around the center of the image
        M = cv2.getRotationMatrix2D((cX, cY), degree, 1.0)
        abs_cos = abs(M[0,0]) 
        abs_sin = abs(M[0,1])
        bound_w = int(h * abs_sin + w * abs_cos)
        bound_h = int(h * abs_cos + w * abs_sin)
        M[0, 2] += bound_w/2 - cX
        M[1, 2] += bound_h/2 - cY
        rotated = cv2.warpAffine(img, M, (bound_w, bound_h))
        return rotated

    def getImage(self,bucket_name,filename):
        _,tf,date,size=self.checkFileExists(bucket_name,filename)
        temp_filename="{}".format(Path(filename))
        temp_outpath=self.tempDirectory.joinpath(temp_filename)
        ext=Path(filename).suffix
        tf=True
        if not tf :
            return utils.error_message("The file doesn't exists",status_code=404)
        else:
            if temp_outpath.exists() == False: 
              temp_outpath.parent.mkdir(parents=True, exist_ok=True)
              f=open(temp_outpath,'wb+')
              subprocess.run(f"aws s3api get-object --bucket {bucket_name} --key {filename} {temp_outpath}", shell=True)
            else:
              f=open(temp_outpath,'rb+')
            bytesIO=io.BytesIO(f.read())
            size=os.fstat(f.fileno()).st_size
            f.close()
        return bytesIO, ext, size , temp_outpath.__str__()

    def downloadFile_link(self,bucket_name,filename, expiry):
        _,tf,date,size=self.checkFileExists(bucket_name,filename)
        if not tf :
            return utils.error_message("The file doesn't exists",status_code=404)
        else:
            try:
                url = subprocess.run(f"aws s3 presign s3://{bucket_name}/{filename}", shell=True, capture_output=True)
                print(url.stdout.decode())
                resp = url.stdout.decode()
                
            except Exception as e:
                exc=traceback.format_exc()
                return utils.error_message("Couldn't have finished to get the link of the file: {}, {}".format(str(e),exc),status_code=500)
        return resp
      
    def downloadFile_link_public(self,bucket_name,filename):
        _,tf,date,size=self.checkFileExists(bucket_name,filename)
        if not tf :
            return utils.error_message("The file doesn't exists",status_code=404)
        else:
            try:
                url = subprocess.run(f"aws s3 presign s3://{bucket_name}/{filename}", shell=True, capture_output=True)
                print(url.stdout.decode())
                resp = url.stdout.decode()
            except Exception as e:
                exc=traceback.format_exc()
                return utils.error_message("Couldn't have finished to get the link of the file: {}, {}".format(str(e),exc),status_code=500)
        return resp
      
    def getJsonFromFile(self, bucket_name, filename, no_aws_yes_server):
      _,_,_,name=self.getFileObject(bucket_name,filename, no_aws_yes_server)
      out = json.load(open(name,'rb'))
      return out

    def getCsvFileAsJson(self,bucket_name,filename, no_aws_yes_server):
        _,_,_,name=self.getFileObject(bucket_name,filename, no_aws_yes_server)
        if '.gz' not in filename:
          out = []
          with open(name,'r') as cf:
            csvreader = csv.reader(cf, delimiter=',')
            for r in csvreader:
                out.append(r)
        else:
          out = []
          with gzip.open(name,'rt', encoding='utf-8') as cf:
            csvreader = csv.reader(cf, delimiter=',')
            for r in csvreader:
              out.append(r)
        return out

    def get_subfolders(self, bucket_name, prefix):
        page_iterator = subprocess.run(f"aws s3api list-objects --bucket {bucket_name} --prefix {prefix} --delimiter /", shell=True, capture_output=True)
        res = []
        file_paths = json.loads(page_iterator.stdout.decode())
        print(file_paths)
        for path in file_paths['CommonPrefixes']:
            full = path["Prefix"]
            split = full.split(prefix)
            folder_name = split[1][:-1]
            res.append(folder_name)
        return res

    def getFileList(self,bucket_name,root_path, fltr=None, delimiter = None, only_files = False): #get all pages
      #alter this to be a lambda function that filters based on the filters and also whether the object is a file or a folder
      def checkList(value, list):
        #can exclude an option if it is only looking for files and finds a folder
        if only_files and value.endswith('/'):
          return False
        if fltr is not None:
          for i in list:
            #know an option is valid if after passing the first condtion, it matches a filter
            if (i.lower() in value.lower()): 
              return True
          #if filter is true but it doesnt match any filter, then it is not valid
          return False
        # if it doesn't have a filter and passed the only files condition, then it is valid
        return True
      
      if not bucket_name: bucket_name = self.bucket_name
    
      if delimiter:
        page_iterator = subprocess.run(f"aws s3api list-objects --bucket {bucket_name} --prefix {root_path} --delimiter {delimiter}", shell=True, capture_output=True)
      else:
        page_iterator = subprocess.run(f"aws s3api list-objects --bucket {bucket_name} --prefix {root_path}", shell=True, capture_output=True)
          
      res=[]
      text = open('/root/output.txt')
      value = text.read()
      while len(value) == 0:
          time.sleep(2)
          value = text.read()
      file_paths = json.loads(value)
      print(file_paths)
      temp = [f['Key'] for f in file_paths['Contents']]
      if fltr is not None or only_files:
        temp=list(filter(lambda x: checkList(x, fltr), temp))
      res+=temp
      return res 

    def checkFileExists(self,bucket_name,filename):
      try:
          head = subprocess.run(f"aws s3api head-object --bucket {bucket_name} --key {filename}", shell=True, capture_output=True)
          object = json.loads(head.stdout.decode())
          print(object)
          date = object['LastModified']
          size = object['ContentLength']
          return 200, True, date, size
      except:
          return 404, False, '', ''


