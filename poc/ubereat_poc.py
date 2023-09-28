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

url='https://www.ubereats.com/tw/store/%E5%A4%A7%E8%8C%97%E6%9C%AC%E4%BD%8D%E8%A3%BD%E8%8C%B6%E5%A0%82-%E5%8F%B0%E5%8C%97%E9%80%9A%E5%8C%96%E5%BA%97/7VmMUYPnW32lAWppBIvqxg?diningMode=DELIVERY&sc=SEARCH_SUGGESTION'
s3 = boto3.client('s3',
                    region_name='ap-northeast-1',
                    aws_access_key_id=os.getenv('iam_drink_key'),
                    aws_secret_access_key=os.getenv('iam_drink_secretkey'))



def get_uber_cookie():
    browser = webdriver.Chrome()
    browser.get(url)  

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
    r = requests.get(url, headers=headers)
    
    if r.status_code == 200:
        soup = BeautifulSoup(r.content, 'lxml')
        # test=soup.find_all("h1", class_="bl bn bm bk", limit=2)
        # name = soup.find_all("span", class_="p9 i7 pa be by bg db b1", limit=2)
        # rate = soup.find_all("div", class_="spacer _4", limit=2)

        # html_file_name = 'example.html'
        # html_content = str(soup).encode('utf-8')

        # bucket_name = 'wannadrink'
        # s3_object_key = 'ubereat/' + html_file_name

        # s3.upload_fileobj(io.BytesIO(html_content), bucket_name, s3_object_key)
        html_file_name='/Users/tracy4528/Downloads/uber1.json'
        with open(html_file_name, 'w') as html_file:
            html_file.write(soup.prettify())


        print('done')
    else:
        print("not found")






if __name__ == "__main__":
    get_uber_cookie()
    uber_spider_check()


