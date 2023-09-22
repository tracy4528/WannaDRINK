import boto3
import json
import pymysql
from dotenv import load_dotenv
import os

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
        print(f'=={store_name}==')

        for result in data['menus']:
            for _ in result["menu_categories"]:
                category_name=_['name']
                for p in _['products']:
                    name=p['name']
                    description=p['description']
                    price=p['product_variations'][0]['price']
                    # size=p['product_variations'][0]['name']
                    if 'name' in p['product_variations'][0]:
                        size = p['product_variations'][0]['name']
                    else:
                        size = None
                    image_url=p['file_path']
                    product_id=p['id']
                    product_code=p['code']
    

                    insert_product_sql = ("INSERT INTO `foodpanda` (store, store_rating, name, size, price, description, image_url,  category_name, product_code, product_id) "
                                        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
                    cursor.execute(insert_product_sql,(store_name, store_rating, name, size, price, description, image_url,category_name, product_code,product_id))
                    print(name)
            
        conn.commit()
        count_processed += 1  # 增加处理的文件数量
        if count_processed >= 10:
            break
cursor.close()
conn.close()