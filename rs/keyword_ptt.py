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
s3_folder_path = 'ptt/20231003/'


conn = pymysql.connect(host=os.getenv('mysql_host'), 
                       user=os.getenv('mysql_user'),
                       password=os.getenv('mysql_password'), 
                       database='product')
cursor = conn.cursor()






def extract_comments_from_s3(s3_folder_path):
    comments = []
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
    return comments

def process_comments(comments):
    jieba.load_userdict('./dict_big.txt')
    jieba.analyse.set_stop_words('./stops.txt')
    comment_text = ' '.join(comments).encode('utf-8').decode('utf-8')
    segmented_text = " ".join(jieba.cut(comment_text))

    tags = jieba.analyse.extract_tags(segmented_text, topK=30, withWeight=False, allowPOS=())
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(segmented_text)
    return tags,wordcloud

ptt_content =extract_comments_from_s3(s3_folder_path)
tags,wordcloud =process_comments(ptt_content)
print(tags)


# 绘制文字云
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off') 
plt.show()
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





