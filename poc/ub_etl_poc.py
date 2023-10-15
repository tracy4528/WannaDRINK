import re
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

s3_bucket_name='wannadrink'
s3_folder_path='ubereat/'
currentDateAndTime = datetime.now()

def s3_parse():
    objects = s3.list_objects_v2(Bucket=s3_bucket_name, Prefix=s3_folder_path)

    for obj in objects.get('Contents'):
        file_name = obj.get('Key')
        
        if file_name.endswith(".json"):
            s3_object = s3.get_object(Bucket=s3_bucket_name, Key=file_name)
            json_data = s3_object['Body'].read().decode('utf-8')
            data = json.loads(json_data)

            print(file_name)
            html_content = data.get("html_content", "")
            pattern = r'<div class="spacer _4"></div><div class="spacer _4"></div>(.*?)</div>'
            matches = re.finditer(pattern, html_content)

            pattern2 = r'<div class=\"g9 ga hx bb\"><span data-testid=\"rich-text\" class=\"hy ei hz ch d2 cj d3 b1\">(.*?)</span>'
            drink_matches = re.finditer(pattern2, html_content)

            matches3 = re.findall(r'class="fv er fw be ct bg ek b1">([^<]+).*?<div class="spacer _4"></div>([^<]+)', html_content)
            for match in matches3:
                print(match)

        # for match in matches:
        #     number = match.group(1)
        #     print( number)

        # for m in drink_matches:
        #     drink = m.group(1)
        #     print( drink)

text={'杏仁凍五桐茶 Wootea with Almond jelly': '99% (378)',
'最完美手沖泰奶 Authentic Thai Milk Tea': '97% (88)',
'椰椰芋圓奶霜 Coconut Ice Crush with Taro Ball': '100% (14)',
'珍珠手沖泰奶 Bubble with Authentic Thai Milk Tea': '96% (57)',
'蜜桃果粒冰沙 Peach Ice Crush with Green Tea Jelly': '100% (9)',
'綠茶凍手沖泰奶 Green tea jelly with Authentic Thai Milk Tea': '100% (24)',
'杏仁凍五桐茶 Wootea with Almond jelly': '98% (572)',
'經典五桐茶 Wootea': '98% (222)',
'老實人紅茶 Black Tea': '99% (170)'}


for drink, rating in text.items():
    update_query = f"UPDATE drink_list SET drink_rating_review = '{rating}' WHERE name = '{drink}' and  store like '%珍煮丹%'"
    cursor.execute(update_query)

conn.commit()
cursor.close()