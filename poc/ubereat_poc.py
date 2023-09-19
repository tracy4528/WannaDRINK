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

url='https://www.ubereats.com/store/%E9%BA%BB%E5%8F%A4%E8%8C%B6%E5%9D%8Amacu-tea-%E6%9D%BE%E5%B1%B1%E8%BB%8A%E7%AB%99%E5%BA%97/xy8Uu0PwQQ273A8wJwEXeQ?diningMode=DELIVERY'

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
        html_file_name='/Users/tracy4528/Downloads/uber1.html'
        with open(html_file_name, 'w') as html_file:
            html_file.write(soup.prettify())


        print('done')
    else:
        print("not found")



'''
====================
foodpanda
====================
'''


def get_fp_cookie():
    browser = webdriver.Chrome()
    browser.get('https://www.foodpanda.com.tw')  

    input('按下 Enter 以繼續')  
    with open('cookies.txt', 'w') as cookief:
        cookief.write(json.dumps(browser.get_cookies()))
    headers_cookie = browser.execute_script('return document.cookie')
    with open('headers_cookies.txt', 'w') as f:
        f.write(headers_cookie)
    print('Cookies save')

def fp_spider_check():
    ua = UserAgent()
    with open('headers_cookies.txt', 'r')as f:
        cookie = f.read()
    headers = {
        'cookie': cookie,
        'User-Agent': ua.random
    }
    CityURL= 'https://www.foodpanda.com.tw'
    result = requests.get(CityURL,headers=headers)


    sp = bs4.BeautifulSoup(result.content , "html.parser")								
    all_a = sp.find_all("a",class_="city-tile")											
    all_link = [CityURL+a.get("href") for a in all_a ]	
    print(all_link)



if __name__ == "__main__":
    uber_spider_check()


