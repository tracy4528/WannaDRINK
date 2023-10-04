from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import json 
import time
import undetected_chromedriver as uc
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

driver = uc.Chrome()



driver.get("https://www.dcard.tw/f/boba")
today_date = datetime.now().strftime("%Y%m%d")

unique_urls=set()
unique_urls_list = []
def get_dcard_articles():
    try:
        articles_data = []  # 用來儲存要插入的數據
        for _ in range(1):
            wait = WebDriverWait(driver, 20)
            articles = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "article")))
            for article in articles:
                url = article.find_element(By.TAG_NAME, "a").get_attribute("href")
                title_element = article.find_element(By.TAG_NAME, "h2")
                title = title_element.get_attribute("innerText")  # 使用 get_attribute 取得標題文本
                like_num = article.find_element(By.CSS_SELECTOR, "div[class='atm_lk_i2wt44 c1jkhqx5']")
                push = like_num.text

                unique_urls.add(url)
                articles_data.append((title, url, push, today_date))  # 將數據添加到列表中

            driver.execute_script("window.scrollBy(0,600);")
            time.sleep(5)

        print(set(articles_data))

        unique_articles_data=set(articles_data)
        
        insert_product_sql = ("INSERT INTO `dcard_articles` (title, url, push, crawl_date) VALUES (%s, %s, %s, %s)")
        cursor = conn.cursor()
        cursor.executemany(insert_product_sql, unique_articles_data)
        conn.commit()
            
        unique_urls_list = list(unique_urls)
        print("=========")
        print(unique_urls_list)
        
    except Exception as e:
        print("error:", e)

        
    return unique_urls_list






def dcard_post_comment(dcard_topic_page):
    comments = []
    driver.get(dcard_topic_page)
    WebDriverWait(driver, 3)
    title=driver.find_element(By.CSS_SELECTOR, "h1[class='atm_w6_1hnarqo atm_7l_1e0g2gl atm_cs_b2t90y atm_c8_xi843o atm_g3_16tj23q bipaz8j']")
    content=driver.find_element(By.CSS_SELECTOR, "div[class='atm_c8_exct8b atm_g3_1f4h9lt atm_7l_1u09hbr c1h57ajp']")
    # article_time=driver.find_element(By.CSS_SELECTOR, "time[class='atm_7l_1w35wrm atm_vv_1q9ccgz atm_sq_1l2sidv atm_ks_15vqwwr atm_11ec84c_17s1f44 atm_5oq6dp_awxwf5 ifw06em']")
    driver.execute_script("window.scrollBy(0,500);")

    for _ in range(2):
        # driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        driver.execute_script("window.scrollBy(0,200);")
        commant=driver.find_elements(By.CSS_SELECTOR,"div[class='atm_7l_1u09hbr atm_c8_exct8b atm_g3_1f4h9lt c201erw']")
    for com in commant:
        comments.append({
            'content': com.text,
        })

    data = {
        'title': title.accessible_name,
        'content': content.text,
        'comments': comments,
    }
    
    return data


    


def handler(event=None, context=None):
    article_list=get_dcard_articles()
    # article_list=[ 'https://www.dcard.tw/f/boba/p/253353184','https://www.dcard.tw/f/boba/p/253356515']
    

    today_date = datetime.now().strftime("%Y%m%d")
    
    for article in article_list:
        try:
            print("=======start=======")
            json_data=dcard_post_comment(article)
            json_bytes = json.dumps(json_data, ensure_ascii=False, indent=4)
            article_code=article.split('/')[-1]
            bucket_name = 'wannadrink'
            s3_object_key=f'dcard/{today_date}/{article_code}.json'
            folder_path = os.path.join('dcard/', today_date)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            else:
                s3.put_object(
                    Bucket=bucket_name,
                    Key=s3_object_key,
                    Body=json_bytes,
                    ContentType='application/json'
                )
            print(f'======={article_code}=======')
        except Exception as e:
            print(f'Error encountered: {e}')
            continue

