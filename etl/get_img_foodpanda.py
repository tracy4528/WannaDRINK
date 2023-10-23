import requests
import json 
import io
import boto3
from dotenv import load_dotenv
import os
from datetime import datetime
import pymysql
import time
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
conn = conn_pool.get_connection()
cursor = conn.cursor()

bucket_name = 'wannadrink'

def get_img_url():
    sql = "SELECT id,image_url FROM product.drink_list where image_s3 is null;"
    cursor.execute(sql)
    products = cursor.fetchall()
    file_name_list = []
    image_url_list=[]
    id_list=[]
    for product in products:
        file_name = product['image_url'].split('/')[-1].split('.')[0]
        image_url=product['image_url']
        id=product['id']
        file_name_list.append(file_name)
        image_url_list.append(image_url)
        id_list.append(id)
    return image_url_list, file_name_list,id_list


def saving_s3(image_url_list, file_name_list,id_list):
    count_processed = 0 
    for i in range(len(image_url_list)):
        image_url = image_url_list[i]
        if not image_url:
            continue
        file_name = 'drink_img/'+file_name_list[i]+'.jpg'
        id=id_list[i]
        print(file_name)
        response = requests.get(image_url)

        try:
            if response.status_code == 200:
                image_data = response.content
                s3 = boto3.client('s3')
                image_io = io.BytesIO(image_data)
                s3.upload_fileobj(
                    Fileobj=image_io,
                    Bucket=bucket_name,
                    Key=file_name
                )

                s3_image_url = f"https://{bucket_name}.s3.amazonaws.com/{file_name}"

                update_sql = "UPDATE drink_list SET image_s3 = %s WHERE id = %s;"
                cursor.execute(update_sql, (s3_image_url, id))
                
                print("S3 URL:", s3_image_url)
                count_processed += 1  
            else:
                print("HTTP requests fail ")
        except Exception as e:
            print(f"========= error: {str(e)}=========")
    
        conn.commit() 
        print('========= done =========')

    cursor.close()
    conn.close()



if __name__ == "__main__":
    image_url_list, file_name_list,id_list=get_img_url()
    saving_s3(image_url_list, file_name_list,id_list)
