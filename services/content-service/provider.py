"""Supabase private Storage via S3 protocol. Never persist signed URLs."""
import hashlib
import os
import time
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

class Storage:
    def __init__(self):
        self.bucket=os.environ['CONTENT_BUCKET']
        self.client=boto3.client('s3',endpoint_url=os.environ['CONTENT_S3_ENDPOINT'],region_name=os.environ.get('CONTENT_S3_REGION','local'),
            aws_access_key_id=os.environ['CONTENT_S3_ACCESS_KEY'],aws_secret_access_key=os.environ['CONTENT_S3_SECRET_KEY'],
            config=Config(signature_version='s3v4',connect_timeout=5,read_timeout=30,retries={'max_attempts':1},s3={'addressing_style':'path'}))
    def upload(self,key,media_type):
        return self.client.generate_presigned_url('put_object',Params={'Bucket':self.bucket,'Key':key,'ContentType':media_type},ExpiresIn=900)
    def read(self,key):
        return self.client.generate_presigned_url('get_object',Params={'Bucket':self.bucket,'Key':key,'ResponseContentDisposition':'attachment'},ExpiresIn=300)
    def seal(self,staging,sealed,sha256,size):
        # Sealed namespace is never signed for upload. Copy once, then verify the copy.
        try: self.client.head_object(Bucket=self.bucket,Key=sealed)
        except ClientError as error:
            if str(error.response.get('Error',{}).get('Code')) not in ('404','NoSuchKey','NotFound'): raise
            self.client.copy_object(Bucket=self.bucket,Key=sealed,CopySource={'Bucket':self.bucket,'Key':staging})
        obj=self.client.get_object(Bucket=self.bucket,Key=sealed)
        if obj['ContentLength']!=size: obj['Body'].close();raise ValueError('content_size_mismatch')
        digest=hashlib.sha256();read=0;deadline=time.monotonic()+180
        try:
            while chunk:=obj['Body'].read(1024*1024):
                read+=len(chunk)
                if time.monotonic()>deadline:raise TimeoutError('verification_timeout')
                if read>size: raise ValueError('content_size_mismatch')
                digest.update(chunk)
        finally: obj['Body'].close()
        if read!=size or digest.hexdigest()!=sha256: raise ValueError('content_hash_mismatch')
