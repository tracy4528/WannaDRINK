from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver

import time
import undetected_chromedriver as uc
# from bs4 import BeautifulSoup
import boto3
from dotenv import load_dotenv
import os
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
cursor = conn.cursor()

driver = uc.Chrome(headless=True)
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--headless')


driver.get("https://www.dcard.tw/f/boba")

unique_urls = set()

def get_dcard_articles():
    try:
        for _ in range(2):
            wait = WebDriverWait(driver, 20)           
            articles = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "article")))
            for article in articles:
                print(article)
                url = article.find_element(By.TAG_NAME, "a").get_attribute("href")
                unique_urls.add(url)
            driver.execute_script("window.scrollBy(0,600);")
            time.sleep(5)
        unique_urls_list = list(unique_urls)

    except Exception as e:
        print("error:", e)
    driver.quit()
    print(unique_urls_list)
    return unique_urls_list





def dcard_post_comment(dcard_topic_page):
    comments = []
    driver.get(dcard_topic_page)
    WebDriverWait(driver, 3)
    title=driver.find_element(By.CSS_SELECTOR, "h1[class='atm_w6_1hnarqo atm_7l_1e0g2gl atm_cs_b2t90y atm_c8_xi843o atm_g3_16tj23q bipaz8j']")
    content=driver.find_element(By.CSS_SELECTOR, "div[class='atm_c8_exct8b atm_g3_1f4h9lt atm_7l_1u09hbr c1h57ajp']")
    # article_time=driver.find_element(By.CSS_SELECTOR, "time[class='atm_7l_1w35wrm atm_vv_1q9ccgz atm_sq_1l2sidv atm_ks_15vqwwr atm_11ec84c_17s1f44 atm_5oq6dp_awxwf5 ifw06em']")
    driver.execute_script("window.scrollBy(0,500);")

    for _ in range(10):
        # driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        driver.execute_script("window.scrollBy(0,200);")
        commant=driver.find_elements(By.CSS_SELECTOR,"div[class='atm_7l_1u09hbr atm_c8_exct8b atm_g3_1f4h9lt c201erw']")
        time.sleep(1)
    for com in commant:
        comments.append({
            'content': com.text,
        })

    data = {
        'title': title.accessible_name,
        'content': content.text,
        'comments': comments,
    }
    
    print(data)
    return data



if __name__ == "__main__":
    # article_list=get_dcard_articles()
    article_list=['https://www.dcard.tw/f/boba/p/253356515', 'https://www.dcard.tw/f/boba/p/253353184']
    

    today_date = datetime.now().strftime("%Y%m%d")
    dcard_post_comment(article_list[0])

    # for article in article_list:
    #     json_data=dcard_post_comment(article)
    #     article_code=article.split('/')[-1]
    #     bucket_name = 'wannadrink'
    #     s3_object_key=f'dcard/{today_date}/{article_code}.json'
    #     folder_path = os.path.join('dcard/', today_date)
    #     if not os.path.exists(folder_path):
    #         os.makedirs(folder_path)
    #     else:
    #         s3.put_object(
    #             Bucket=bucket_name,
    #             Key=s3_object_key,
    #             Body=json_data,
    #             ContentType='application/json'
    #         )
    #     print(f'======={article_code}=======')
    

