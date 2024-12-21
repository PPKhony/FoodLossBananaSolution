import json
import boto3
from urllib.parse import urlparse 

sns_client = boto3.client('sns')
s3_client = boto3.client('s3')
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:637423557159:CheckingSNS'

def get_presigned_url(s3_url):
    parsed_url = urlparse(s3_url)
    bucket = parsed_url.netloc.split('.')[0]
    key = parsed_url.path.lstrip('/')

    # สร้าง Presigned URL
    response = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket, 'Key': key},
        ExpiresIn=86400  # URL จะมีอายุ 1 วัน
    )
    return response

def lambda_handler(event, context):
    for record in event['Records']:
        if record['eventName'] in ['INSERT', 'MODIFY']:
            new_image = record['dynamodb']['NewImage']
            
            banana_class = new_image.get('classification', {}).get('S')
            s3_path = new_image.get('s3_path', {}).get('S')

            if banana_class in ['Ripe Banana', 'Overripe Banana', 'Rotten Banana']:
                presigned_url = get_presigned_url(s3_path)

                message = (
                    f"Attention: {banana_class}!\n"
                    f"Please check the status immediately.\n"
                    f"Image: {presigned_url}"
                )
            
                sns_client.publish(
                    TopicArn=SNS_TOPIC_ARN,
                    Message=message,
                    Subject="Banana Alert: Please check the bananas!"
                )

    return {"statusCode": 200, "body": json.dumps("Success")}