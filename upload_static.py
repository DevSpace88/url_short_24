import boto3
import os
from main import app

# moving static files to aws s3 (kinda like collectstatic in django)
s3 = boto3.client(
    's3',
    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
    region_name=os.environ['AWS_REGION']  # Optional: Setzen Sie Ihre AWS-Region
)


def upload_static_files():
    static_folder = app.static_folder
    for root, dirs, files in os.walk(static_folder):
        for filename in files:
            local_path = os.path.join(root, filename)
            s3_path = 'static/' + os.path.relpath(local_path, static_folder)
            
            s3.upload_file(
                Filename=local_path,
                Bucket=os.environ.get('S3_BUCKET_NAME'),
                Key=s3_path
            )
            print(f"Uploaded {s3_path}")

upload_static_files()

