import boto3
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
load_dotenv()

s3 = boto3.client('s3',
                    region_name='ap-northeast-1',
                    aws_access_key_id=os.getenv('iam_drink_key'),
                    aws_secret_access_key=os.getenv('iam_drink_secretkey'))
article_list = []

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
    soup = BeautifulSoup(resp.text, 'html5lib')
    arts = soup.find_all('div', class_='r-ent')
    for art in arts:
        title = art.find('div', class_='title').getText().strip()
        if not title.startswith('(本文已被刪除)'):
            link = 'https://www.ptt.cc' + \
                art.find('div', class_='title').a['href'].strip()
        author = art.find('div', class_='author').getText().strip()
        article_code=art.find('div', class_='title').a['href'].strip().split('/')[-1].split('.')[1]
        article = {
            'title': title,
            'link': link,
            'author': author,
            'article_code':article_code
        }
        article_list.append(article)
    # 利用 Css Selector 定位下一頁網址
    next_url = 'https://www.ptt.cc' + \
        soup.select_one(
            '#action-bar-container > div > div.btn-group.btn-group-paging > a:nth-child(2)')['href']

    return next_url

def get_post_comment(url):
    

    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')

    meta_data = {
        'author': soup.find('div', {'class': 'article-metaline'}).find('span', {'class': 'article-meta-value'}).text,
        'title': soup.find_all('div', {'class': 'article-metaline'})[1].find('span', {'class': 'article-meta-value'}).text,
        'date': soup.find_all('div', {'class': 'article-metaline'})[2].find('span', {'class': 'article-meta-value'}).text,
    }

# Extract the post's content
    content = soup.find('div', {'id': 'main-content'}).text

# Extract the comments
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
        'content': content,
        'comments': comments,
    }

    # Convert data to JSON
    json_data = json.dumps(data, ensure_ascii=False, indent=4)

    return json_data

if __name__ == '__main__':
    url = 'https://www.ptt.cc/bbs/Drink/index.html'
    today_date = datetime.now().strftime("%Y%m%d")

    for now_page_number in range(2):
        print(f'crawing {url}')
        resp = get_resp(url)
        if resp != 'error':
            url = get_articles(resp)
        print(f'======={now_page_number+1}/10=======')
    
    for article in article_list:
        json_data=get_post_comment(article['link'])
        article_code=article['article_code']
        name=article['title']
        bucket_name = 'wannadrink'
        s3_object_key=f'ptt/{today_date}/{article_code}.json'
        folder_path = os.path.join('ptt/', today_date)
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
    

