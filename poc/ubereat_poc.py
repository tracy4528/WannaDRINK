from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import requests
from bs4 import BeautifulSoup
import boto3
from fake_useragent import UserAgent
import json
import os
from dotenv import load_dotenv
import io
import bs4
load_dotenv()


s3 = boto3.client('s3',
                    region_name='ap-northeast-1',
                    aws_access_key_id=os.getenv('iam_drink_key'),
                    aws_secret_access_key=os.getenv('iam_drink_secretkey'))

with open('poc/ub_store_url.json', 'r', encoding='utf-8') as file:
    urls = json.load(file)

def get_uber_cookie():
    browser = webdriver.Chrome()
    browser.get(urls['data'][0]['url'])  
    input('按下 Enter 以繼續')  
    with open('cookies.txt', 'w') as cookief:
        cookief.write(json.dumps(browser.get_cookies()))
    headers_cookie = browser.execute_script('return document.cookie')
    with open('headers_cookies.txt', 'w') as f:
        f.write(headers_cookie)
    print('Cookies save')


def uber_spider_check():
    ua = UserAgent()
    with open('headers_cookies.txt', 'r')as f:
        cookie = f.read()
    headers = {
        'cookie': cookie,
        'User-Agent': ua.random
    }

    for url in urls['data']: 
        r = requests.get(url['url'], headers=headers)
        
        if r.status_code == 200:
            html_content = r.text
            soup = BeautifulSoup(r.content, 'lxml')

            json_data = {'html_content': html_content}
            restaurant_code=url['store']

            json_data = json.dumps(json_data, ensure_ascii=False, indent=2)
            bucket_name = 'wannadrink'


            s3_object_key=f'ubereat/{restaurant_code}_menu.json'
            s3.put_object(
                Bucket=bucket_name,
                Key=s3_object_key,
                Body=json_data,
                ContentType='application/json'
            )

        print('done')
    else:
        print("not found")






if __name__ == "__main__":
    get_uber_cookie()
    uber_spider_check()


