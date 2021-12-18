from storages.backends.s3boto3 import S3Boto3Storage
from decouple import config

class MediaStorage(S3Boto3Storage):    
    location = 'media'    
    file_overwrite = False
    bucket_name = config('AWS_STORAGE_BUCKET_NAME')

class StaticStorage(S3Boto3Storage):
    location = 'static'
    ucket_name = config('AWS_STORAGE_BUCKET_NAME')