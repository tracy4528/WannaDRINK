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

def hot_article_text(date=today_date, source='ptt'): 

    sql_ptt = f"SELECT url FROM ptt_articles where crawl_date='{date}' ORDER BY push DESC limit 1 OFFSET 7 "
    sql_dcard = f"SELECT url FROM dcard_articles where crawl_date='{date}' ORDER BY push DESC limit 1 OFFSET 1"

    if source == 'ptt':  
        sql_query = sql_ptt
    elif source == 'dcard':  
        sql_query = sql_dcard

    cursor.execute(sql_query)  
    urls = cursor.fetchall()
    for url in urls:
        if source == 'ptt':  
            data = url['url'].split('/')[-1].split('.')[1]
        elif source == 'dcard':  
            data = url['url'].split('/')[-1]

        file_key = source + '/' + date + '/' + data + '.json'
        response = s3.get_object(Bucket='wannadrink', Key=file_key)
        json_data = response['Body'].read().decode('utf-8')
        data = json.loads(json_data)

        print('==============')

        if 'comments' in data:
            comments.extend([comment['content'] for comment in data['comments']])
        if 'content' in data:
            comments.extend([data['content']])
        print(data['meta_data']['title'])
        print('==============')

    return comments






def get_hot_word(date=today_date,source='ptt'):
    text=hot_article_text(date=date,source='ptt')

    openai.api_key = os.getenv('openai_key')
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"請幫我從以下論壇文章取出三個熱門討論的關鍵字,並提供list格式,例如：[鶴茶樓-桂花烏龍,清心-蜜桃凍紅茶]文章：'{text}'"}
        ]
    )
    keyword=completion["choices"][0]["message"]["content"]
    print(keyword)

    insert_sql = ("INSERT INTO `hot_keyword` (keyword, date, from_) VALUES (%s, %s, %s)")
    cursor = conn.cursor()
    cursor.execute(insert_sql, (keyword,date,source))  
    conn.commit()


get_hot_word(date='20231003',source='ptt')