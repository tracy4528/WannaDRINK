import boto3
import json
import pymysql
from dotenv import load_dotenv
import os
from datetime import datetime


load_dotenv()

s3 = boto3.client('s3',
                    region_name='ap-northeast-1',
                    aws_access_key_id=os.getenv('iam_drink_key'),
                    aws_secret_access_key=os.getenv('iam_drink_secretkey'))

conn = pymysql.connect(host=os.getenv('mysql_host'), 
                       user=os.getenv('mysql_user'),
                       password=os.getenv('mysql_password'), 
                       database='product')
cursor = conn.cursor()

count_processed = 0 
s3_bucket_name='wannadrink'
s3_folder_path='foodpanda/'
currentDateAndTime = datetime.now()

objects = s3.list_objects_v2(Bucket=s3_bucket_name, Prefix=s3_folder_path)

for obj in objects.get('Contents'):
    file_name = obj.get('Key')
    
    if file_name.endswith(".json"):
        s3_object = s3.get_object(Bucket=s3_bucket_name, Key=file_name)
        json_data = s3_object['Body'].read().decode('utf-8')
        data = json.loads(json_data)

        store_name=data['name']
        store_rating=data['rating']
        review_number=data['review_number']
        latitude=data['latitude']
        longitude=data['longitude']
        store_code=data['code']
        store_url=data['web_path']
        address=data['address'].split(')')[-1]
        hero_image=data['hero_image']
        print(store_name,store_url,address,store_rating)
        

        insert_product_sql = ("INSERT INTO `store_info` (store_name, store_latitude, store_longitude, store_rating,store_image,store_review_number, store_url_fp, address, store_code,created_time) "
                                        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
        cursor.execute(insert_product_sql,(store_name, latitude, longitude, store_rating,hero_image,review_number, store_url, address, store_code,currentDateAndTime))
        count_processed += 1  

    if count_processed % 50 == 0:
        conn.commit() 
conn.commit() 
cursor.close()
conn.close()
        

