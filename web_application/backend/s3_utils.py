import boto3
import os
from dotenv import load_dotenv

load_dotenv()

s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION', 'ap-south-1')
)

BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')

def upload_file_to_s3(file_content, filename):
    try:
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=filename,
            Body=file_content
        )
        
        # Generate URL
        url = f"https://{BUCKET_NAME}.s3.{os.getenv('AWS_REGION', 'us-east-1')}.amazonaws.com/{filename}"
        return url
    except Exception as e:
        print(f"Error uploading to S3: {str(e)}")
        raise e

def delete_file_from_s3(filename):
    try:
        s3_client.delete_object(
            Bucket=BUCKET_NAME,
            Key=filename
        )
    except Exception as e:
        print(f"Error deleting from S3: {str(e)}")
        raise e 