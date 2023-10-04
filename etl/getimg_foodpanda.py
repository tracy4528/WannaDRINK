import requests
import json 
import io
import boto3
from dotenv import load_dotenv
import os
from datetime import datetime
import pymysql

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

# S3 存储桶名称和文件名
bucket_name = 'wannadrink'
file_name = 'drink_img/a2ff.jpg'  # 本地文件名

# 設定圖片的URL
image_url = "https://images.deliveryhero.io/image/fd-tw/LH/a2ff-hero.jpg"

# 發送HTTP GET請求以下載圖片
response = requests.get(image_url)

# 檢查是否成功下載圖片
if response.status_code == 200:
    # 獲取圖片的內容
    image_data = response.content

    # 初始化 S3 客户端
    s3 = boto3.client('s3')

    # 将图像数据包装在 io.BytesIO 中
    image_io = io.BytesIO(image_data)

    # 上传图像到 S3 存储桶
    s3.upload_fileobj(
        Fileobj=image_io,
        Bucket=bucket_name,
        Key=file_name
    )

    # 生成 S3 存储的图像 URL
    s3_image_url = f"https://{bucket_name}.s3.amazonaws.com/{file_name}"
    
    print("圖片下載成功並已上傳到 Amazon S3")
    print("S3 圖片 URL:", s3_image_url)
else:
    print("無法下載圖片，HTTP請求失敗")


