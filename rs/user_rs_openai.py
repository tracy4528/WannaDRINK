import openai
from dotenv import load_dotenv
from datetime import datetime
import json 

import os
import pymysql
import boto3


load_dotenv()


conn = pymysql.connect(host=os.getenv('mysql_host'), 
                       user=os.getenv('mysql_user'),
                       password=os.getenv('mysql_password'), 
                       database='product',
                       cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()
s3 = boto3.client('s3',
                    region_name='ap-northeast-1',
                    aws_access_key_id=os.getenv('iam_drink_key'),
                    aws_secret_access_key=os.getenv('iam_drink_secretkey'))

comments = []
today_date = datetime.today().strftime('%Y%m%d')

def hot_article_text_ptt():
    sql=f"SELECT url FROM ptt_articles  where crawl_date='{today_date}' ORDER BY push DESC limit 1"
    cursor.execute(sql)
    urls = cursor.fetchall()
    for url in urls:
        data=url['url'].split('/')[-1].split('.')[1]
        file_key= 'ptt/'+today_date+'/'+data+'.json'
        response = s3.get_object(Bucket='wannadrink', Key=file_key)
        json_data = response['Body'].read().decode('utf-8')
        data = json.loads(json_data)

        if 'comments' in data:
                comments.extend([comment['content'] for comment in data['comments']])
        if 'content' in data:
                comments.extend([data['content']])
    return comments


def get_hot_word():
    text=hot_article_text_ptt()

    openai.api_key = os.getenv('openai_key')
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"請幫我從以下論壇文章取出兩個熱門討論的飲料店及飲料品項, 文章：'{text}'"}
        ]
    )
    keyword=completion["choices"][0]["message"]["content"]
    print(keyword)

    insert_sql = ("INSERT INTO `hot_keyword` (keyword, date, from_) VALUES (%s, %s, %s)")
    cursor = conn.cursor()
    cursor.execute(insert_sql, (keyword,today_date,'ptt'))  
    conn.commit()


