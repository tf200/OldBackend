from celery import shared_task
import boto3
from django.conf import settings  # Import Django settings

@shared_task
def clear_temporary_files():
    s3 = boto3.resource('s3',
                        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                        region_name=settings.AWS_S3_REGION_NAME)
    bucket = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)

    prefix = 'temporary_files/'
    objects_to_delete = bucket.objects.filter(Prefix=prefix)

    # Delete the objects
    for obj in objects_to_delete:
        obj.delete()
    
    return 'success'