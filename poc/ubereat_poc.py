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
url='https://www.ubereats.com/search?diningMode=DELIVERY&pl=JTdCJTIyYWRkcmVzcyUyMiUzQSUyMiVFNSU4RiVCMCVFNSU4QyU5NyVFNSU4NSVBQyVFOSVBNCVBOCVFNSVBNCU5QyVFNSVCOCU4MiUyMiUyQyUyMnJlZmVyZW5jZSUyMiUzQSUyMkNoSUpWVlZWVlJXc1FqUVJ3UUg2V1RmVGZQQSUyMiUyQyUyMnJlZmVyZW5jZVR5cGUlMjIlM0ElMjJnb29nbGVfcGxhY2VzJTIyJTJDJTIybGF0aXR1ZGUlMjIlM0EyNS4wMTM3ODczJTJDJTIybG9uZ2l0dWRlJTIyJTNBMTIxLjUzNDc4NjUlN0Q%3D&q=Bubble%20Tea&sc=SHORTCUTS'
# url='https://www.ubereats.com/tw/store/%E4%BA%94%E6%A1%90%E8%99%9Fwootea-%E5%85%AC%E9%A4%A8%E5%BA%97/kDCmfj9BTEWDGOXyeF99vA'
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
        tests=soup.find_all("div", class_="hm o8 o9")
        print(tests)
        for test in tests:
            rate = soup.find("a", class_="spacer _4")
            link=soup.find('a', {'data-testid': 'store-card'})['href']
            print(link)


        # test=soup.find_all("h1", class_="bl bn bm bk", limit=2)
        # name = soup.find_all("span", class_="p9 i7 pa be by bg db b1", limit=2)
        # rate = soup.find_all("div", class_="spacer _4", limit=2)

        # html_file_name = 'example.html'
        # html_content = str(soup).encode('utf-8')

        # bucket_name = 'wannadrink'
        # s3_object_key = 'ubereat/' + html_file_name

        # s3.upload_fileobj(io.BytesIO(html_content), bucket_name, s3_object_key)
        html_file_name='/Users/tracy4528/Downloads/uber_list.json'
        with open(html_file_name, 'w') as html_file:
            html_file.write(soup.prettify())


        print('done')
    else:
        print("not found")






if __name__ == "__main__":
    get_uber_cookie()
    uber_spider_check()


