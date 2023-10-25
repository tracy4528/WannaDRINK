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

            for match in matches:
                number = match.group(1)
                print(f'{number}')

            pattern2 = r'<span data-testid=\"rich-text\" class=\"hw er hx be ct bg ek b1\">(.*?)</span>'
            drink_matches = re.finditer(pattern2, html_content)

            for m in drink_matches:
                drink = m.group(1)
                print(drink)

            # matches3 = re.findall(r'class="fv er fw be ct bg ek b1">([^<]+).*?<div class="spacer _4"></div>([^<]+)', html_content)
            # for match in matches3:
            #     print(match)


            

text={'復刻胚芽奶茶': '97% (222)',
'復刻奶茶': '97% (634)',
'舶來紅茶': '96% (30)',
'藝伎多多':'98% (263)',
'桂香烏龍多多': '98% (209)',
'綠茶多多': '98% (173)',
'舶來多多': '98% (92)',
'綺夢紅茶': '98% (43)',
'鶴記鴛鴦凍奶茶 ':'97% (699)',
'桂香烏龍凍綺夢那堤':'98% (233)'}


def insert_sql(text):
    for drink, rating in text.items():
        update_query = f"UPDATE drink_list SET drink_rating_review = '{rating}' WHERE name like '%{drink}%' and  store like '%鶴茶樓%'"
        cursor.execute(update_query)

    conn.commit()
    cursor.close()


insert_sql(text)
#s3_parse()