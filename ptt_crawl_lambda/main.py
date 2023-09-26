import boto3
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import json
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
article_list = []
article_data = []

def get_resp(url):
    cookies = {
        'over18': '1'
    }
    resp = requests.get(url, cookies=cookies)
    if resp.status_code != 200:
        return 'error'
    else:
        return resp

def get_articles(resp):
    today_date = datetime.now().strftime("%Y%m%d")
    soup = BeautifulSoup(resp.text, 'html5lib')
    arts = soup.find_all('div', class_='r-ent')
    next_url = 'https://www.ptt.cc' + \
        soup.select_one('#action-bar-container > div > div.btn-group.btn-group-paging > a:nth-child(2)')['href']

    
    for art in arts:
        title = art.find('div', class_='title').getText().strip()
        if not (title.startswith('(本文已被刪除)') or title.startswith('[公告]')):
            link = 'https://www.ptt.cc' + \
                art.find('div', class_='title').a['href'].strip()
        author = art.find('div', class_='author').getText().strip()
        article_code=art.find('div', class_='title').a['href'].strip().split('/')[-1].split('.')[1]
        push=art.find('div', class_="nrec").getText().strip()
        date=art.find('div', class_="date").getText().strip()
        article = {
            'title': title,
            'link': link,
            'author': author,
            'article_code':article_code
        }

        article_list.append(article)
        article_data.append((title, link, push, date, today_date))
    
    return next_url

def insert_ptt_article(article_data):
    try:
        insert_product_sql = ("INSERT INTO `ptt_articles` (title, url, push, pulish_date, crawl_date) VALUES (%s, %s, %s, %s, %s)")
        cursor = conn.cursor()
        cursor.executemany(insert_product_sql, article_data)  
        conn.commit()
        print(f'Successfully inserted {len(article_data)} articles into MySQL')
    except Exception as e:
        print(f'Error: {str(e)}')



def get_post_comment(url):

    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    article_time=soup.find_all('div', {'class': 'article-metaline'})[2].find('span', {'class': 'article-meta-value'}).text

    meta_data = {
        'author': soup.find('div', {'class': 'article-metaline'}).find('span', {'class': 'article-meta-value'}).text,
        'title': soup.find_all('div', {'class': 'article-metaline'})[1].find('span', {'class': 'article-meta-value'}).text,
        'date': article_time,
    }

    content = soup.find("div", id="main-content").get_text().split("--\n※ 發信站: 批踢踢實業坊(ptt.cc), 來自: ")
    main_content = content[0].split(article_time)[1]


    comments = []
    for comment in soup.find_all('div', {'class': 'push'}):
        push_tag = comment.find('span', {'class': 'push-tag'}).text.strip()
        push_userid = comment.find('span', {'class': 'push-userid'}).text.strip()
        push_content = comment.find('span', {'class': 'push-content'}).text.strip()
        push_time = comment.find('span', {'class': 'push-ipdatetime'}).text.strip()
        comments.append({
            'tag': push_tag,
            'userid': push_userid,
            'content': push_content,
            'time': push_time,
        })

    data = {
        'meta_data': meta_data,
        'content': main_content,
        'comments': comments,
    }
    json_data = json.dumps(data, ensure_ascii=False, indent=4)

    return json_data

def handler(event=None, context=None):
    url = 'https://www.ptt.cc/bbs/Drink/index.html'
    today_date = datetime.now().strftime("%Y%m%d")

    for now_page_number in range(1):
        print(f'crawing {url}')
        resp = get_resp(url)
        if resp != 'error':
            url = get_articles(resp)
            
        print(f'======={now_page_number+1}=======')

    insert_ptt_article(article_data)

    for article in article_list:
        try:
            json_data=get_post_comment(article['link'])
            article_code=article['article_code']
            name=article['title']
            bucket_name = 'wannadrink'
            s3_object_key=f'ptt/{today_date}/{article_code}.json'
            folder_path = f'ptt/{today_date}'
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            else:
                s3.put_object(
                    Bucket=bucket_name,
                    Key=s3_object_key,
                    Body=json_data,
                    ContentType='application/json'
            )
            print(f'======={name}=======')
        except Exception as e:
            print(f'Error encountered: {e}')
            continue

