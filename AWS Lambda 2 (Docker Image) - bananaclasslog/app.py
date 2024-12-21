import boto3
import datetime
from decimal import Decimal
from PIL import Image
import requests
import uuid
from zoneinfo import ZoneInfo


s3_resource = boto3.resource('s3', region_name='us-east-1')
s3_client = boto3.client('s3')

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('BananaInfo')

def lambda_handler(event, context):
    print('start functioning')
    # Retrieve the bucket name and object key from the event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    # bucket = s3_resource.Bucket(bucket_name)
    file_name = event['Records'][0]['s3']['object']['key']
    file_name = file_name.replace('+', ' ')
    print(bucket_name + " : " + file_name)
    IMAGE_WIDTH = 224
    IMAGE_HEIGHT = 224
    IMAGE_SHAPE = (IMAGE_WIDTH, IMAGE_HEIGHT)
    img = readImageFromBucket(file_name, bucket_name).resize(IMAGE_SHAPE)

    if image_check(img):
        item = {}
        item['filename'] = file_name
        item['photo_id'] = str(uuid.uuid4())
        s1 = file_name.split()
        s2 = s1[1].split(".")
        
        api_url = "http://54.224.79.21:5000/classify"
        img.save(f"/tmp/{file_name}")
        with open(f'/tmp/{file_name}', 'rb') as image_file:
            request_body = {'file': image_file}
            response = requests.post(api_url, files=request_body)
            print(response.json())
            response = response.json()
            basketNum = int(s2[0])
            stackNum = 5
            item['row'] = int(basketNum-1 % stackNum)
            item['column'] = int(basketNum-1 / stackNum)
            item['classification'] = response['predicted_class_name']
            item['accuracy'] = Decimal(response['accuracy'])
            item['s3_path'] = f'https://{bucket_name}.s3.amazonaws.com/{file_name}'
            item['timestamp'] = str(datetime.datetime.now(ZoneInfo('Asia/Bangkok')))
            
            table.put_item(Item=item)
    else:
        print("The provided file is not a valid image.")

def image_check(input_image):
    try:
        input_image.verify()
        print('Image Verified')
        return True
    except Exception:
        return False

def readImageFromBucket(key, bucket_name):
    bucket = s3_resource.Bucket(bucket_name)
    object = bucket.Object(key)
    response = object.get()
    return Image.open(response['Body'])
    