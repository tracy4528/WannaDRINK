import boto3
import json
import pymysql
from dotenv import load_dotenv
import pandas as pd
import os
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import jieba
import jieba.analyse as analyse
from collections import Counter

load_dotenv()

s3 = boto3.client('s3',
                  region_name='ap-northeast-1',
                  aws_access_key_id=os.getenv('iam_drink_key'),
                  aws_secret_access_key=os.getenv('iam_drink_secretkey'))
comments = []
s3_bucket_name='wannadrink'
s3_folder_path = 'ptt/20230918/'
s3_object_key='ptt/20230918/1694500485.json'


conn = pymysql.connect(host=os.getenv('mysql_host'), 
                       user=os.getenv('mysql_user'),
                       password=os.getenv('mysql_password'), 
                       database='product')
cursor = conn.cursor()


# s3_object = s3.get_object(Bucket=s3_bucket_name, Key=s3_object_key)
# json_data = s3_object['Body'].read().decode('utf-8')
# data = json.loads(json_data)

comments = []


def dict():
    sql='SELECT original_name FROM foodpanda_store_code;'
    cursor.execute(sql)
    names = cursor.fetchall()
    sql_p='SELECT name FROM foodpanda;'
    cursor.execute(sql_p)
    products = cursor.fetchall()
    with open('dict.txt', 'w', encoding='utf-8') as f:
        for name in names:
            f.write(name[0] + '\n')
    with open('dict.txt', 'a', encoding='utf-8') as f:
        for product in products:
            f.write(product[0] + '\n')
    cursor.close()

def extract_comments_from_s3():
    objects = s3.list_objects_v2(Bucket=s3_bucket_name, Prefix=s3_folder_path)
    for obj in objects.get('Contents'):
        file_name = obj.get('Key')
        if file_name.endswith(".json"):
            s3_object = s3.get_object(Bucket=s3_bucket_name, Key=file_name)
            json_data = s3_object['Body'].read().decode('utf-8')
            data = json.loads(json_data)
            
            if 'comments' in data:
                comments.extend([comment['content'] for comment in data['comments']])
            if 'content' in data:
                comments.extend([data['content']])
            
extract_comments_from_s3()

jieba.load_userdict('./dict_big.txt')
jieba.analyse.set_stop_words('./stops.txt')
comment_text = ' '.join(comments).encode('utf-8').decode('utf-8')
tags=jieba.analyse.extract_tags (comment_text,topK=30, withWeight=False, allowPOS=())
print(tags)

'''
jieba.set_dictionary('dict.txt.big') 
jieba.load_userdict('./dict.txt_drink.txt')
# with open('stops.txt', 'r', encoding='utf8') as f:
#     stops = f.read().split('\n') 


comment_text = ' '.join(comments).encode('utf-8').decode('utf-8')
jieba.analyse.set_stop_words('./dict.txt_drink.txt')
# words = ' '.join(jieba.cut(comment_text))
tags=jieba.analyse.extract_tags (comment_text,topK=10, withWeight=False, allowPOS=())
print(tags)

stops.append('\n')  
stops.append('\n\n')
terms = [t for t in jieba.cut(words, cut_all=True) if t not in stops]
print(sorted(Counter(terms).items(), key=lambda x:x[1], reverse=True))

myWordClode = WordCloud(font_path='SourceHanSansTW-Regular.otf', width=800, height=400).generate(words)

plt.figure(figsize=(8, 6), dpi=100) 
plt.imshow(myWordClode)
plt.axis("off")
plt.show()
'''





