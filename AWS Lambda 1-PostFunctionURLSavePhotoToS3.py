import boto3
import base64
import json
from uuid import uuid4
from datetime import datetime
import os

# Initialize AWS services
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    try:
        # Extract the image from the body (assuming binary data is Base64 encoded)
        if event.get('isBase64Encoded', False):
            image_data = base64.b64decode(event['body'])
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Invalid image encoding'})
            }

        # Extract header for image name
        headers = event.get('headers', {})
        original_filename = headers.get('x-filename')
        original_fileextension = headers.get('x-fileextension')
        user_agent = headers.get('user-agent', 'Unknown')

        # Ensure file has a valid extension
        # if not original_filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
        #     return {
        #         'statusCode': 400,
        #         'body': json.dumps({'message': 'Invalid file type'})
        #     }

        # Define S3 bucket and path
        bucket_name = "bananainfo"
        s3_path = f"{original_filename}.{original_fileextension}"

        # Upload the image to S3
        s3.put_object(
            Bucket=bucket_name,
            Key=s3_path,
            Body=image_data,
            ContentType='image/jpeg'
        )

        # Generate S3 URL
        s3_url = f"https://{bucket_name}.s3.amazonaws.com/{s3_path}"

        # Generate metadata
        photo_id = str(uuid4())

        print(json.dumps(event))

        # Return success response
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Image uploaded successfully',
                'photo_id': photo_id,
                's3_url': s3_url,
                'user_agent': user_agent
            })
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Internal server error'})
        }
