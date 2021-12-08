from storages.backends.s3boto3 import S3Boto3Storage
from decouple import config

class MediaStorage(S3Boto3Storage):    
    location = 'media'    
    file_overwrite = True
    bucket_name = config('AWS_STORAGE_BUCKET_NAME')