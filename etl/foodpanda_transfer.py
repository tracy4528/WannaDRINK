import boto3
import json
import pymysql
from dotenv import load_dotenv
import os
from datetime import datetime
from mysql.connector import pooling

load_dotenv()

s3 = boto3.client('s3',
                    region_name='ap-northeast-1',
                    aws_access_key_id=os.getenv('iam_drink_key'),
                    aws_secret_access_key=os.getenv('iam_drink_secretkey'))



conn_pool = pooling.MySQLConnectionPool(pool_name="wannadrink",
                                        pool_size=5,
                                        user=os.environ.get('mysql_user'),
                                        host= os.environ.get('mysql_host'),
                                        password= os.environ.get('mysql_password'),
                                        database= os.environ.get('mysql_database'))



s3_bucket_name='wannadrink'
s3_folder_path='foodpanda/'

def menu_to_sql( data):
    conn = conn_pool.get_connection()
    cursor = conn.cursor()
    store_name = data['name'].split('(')[0]
    store_rating = data['rating']
    review_number = data['review_number']

    insert_data = []

    for result in data['menus']:
        for category in result["menu_categories"]:
            category_name = category['name']
            for product in category['products']:
                name = product['name']
                description = product['description']
                price = product['product_variations'][0]['price']
                size = product['product_variations'][0].get('name', None)
                image_url = product['file_path']

                insert_data.append((store_name, store_rating, review_number, name, size, price, description, image_url, category_name))
    insert_product_sql = ("INSERT INTO `drink_list` (store, store_rating, store_review_number, name, size, price, description, image_url, category_name) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)")
    cursor.executemany(insert_product_sql, insert_data)
    conn.commit()

    cursor.close()
    conn.close()

def store_to_sql(data):
    conn = conn_pool.get_connection()
    cursor = conn.cursor()

    insert_data = []
    store_name=data['name']
    store_rating=data['rating']
    review_number=data['review_number']
    latitude=data['latitude']
    longitude=data['longitude']
    store_code=data['code']
    store_url=data['web_path']
    address=data['address'].split(')')[-1]
    hero_image=data['hero_image']
    insert_data.append((store_name, latitude, longitude, store_rating,hero_image,review_number, store_url, address, store_code,currentDateAndTime))
 

    insert_product_sql = ("INSERT INTO `store_info` (store_name, store_latitude, store_longitude, store_rating,store_image,store_review_number, store_url_fp, address, store_code,created_time) "
                            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
    cursor.executemany(insert_product_sql, insert_data)
    conn.commit()

    cursor.close()
    conn.close()

def s3_get_json():
    
    objects = s3.list_objects_v2(Bucket=s3_bucket_name, Prefix=s3_folder_path)

    for obj in objects.get('Contents'):
        file_name = obj.get('Key')

        if file_name.endswith(".json"):
            s3_object = s3.get_object(Bucket=s3_bucket_name, Key=file_name)
            json_data = s3_object['Body'].read().decode('utf-8')
            data = json.loads(json_data)
            menu_to_sql(data)
            store_to_sql(data)

    

