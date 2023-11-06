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

currentDateAndTime = datetime.now()
today_date = datetime.now().strftime("%Y%m%d")


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
        article_data.append((title, link, push, date, today_date,currentDateAndTime))
    
    return next_url

def sql_ptt_article(article_data):
    try:
        insert_product_sql = ("INSERT INTO `ptt_articles` (title, url, push, pulish_date, crawl_date,created_time) VALUES (%s, %s, %s, %s, %s, %s)")
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

def line_notify(message):
    token = os.getenv('line_token')
    headers = {"Authorization": "Bearer " + token}
    data = {'message': message}
    requests.post("https://notify-api.line.me/api/notify", headers=headers, data=data)

def save_to_s3(article_list):
    for article in article_list:
        try:
            json_data=get_post_comment(article['link'])
            article_code=article['article_code']
            name=article['title']
            bucket_name = 'wannadrink'
            s3_object_key=f'ptt/{today_date}/{article_code}.json'
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

def handler(event=None, context=None):
    url = 'https://www.ptt.cc/bbs/Drink/index.html'

    for now_page_number in range(3):
        print(f'crawing {url}')
        resp = get_resp(url)
        if resp != 'error':
            url = get_articles(resp)
            
        print(f'======={now_page_number+1}=======')
    message = f'{today_date} finished ptt crawl! Successfully inserted {len(article_data)} articles into MySQL'

    save_to_s3(article_list)
    sql_ptt_article(article_data)
    line_notify(message)

handler(event=None, context=None)