from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import requests
import re
import pymysql
from dotenv import load_dotenv
import os
from datetime import datetime
import time

load_dotenv()
currentDateAndTime = datetime.now()



conn = pymysql.connect(host=os.getenv('mysql_host'), 
                       user=os.getenv('mysql_user'),
                       password=os.getenv('mysql_password'), 
                       database='product',
                       cursorclass=pymysql.cursors.DictCursor)

def drive():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')  
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def handler(event=None, context=None):
    cursor = conn.cursor()
    sql_store = f"SELECT distinct store FROM drink_list "
    cursor.execute(sql_store)
    stores = cursor.fetchall()

    try:
        for store in stores:
            driver=drive()
            driver.implicitly_wait(10)
            driver.get('https://www.google.com/')
            print(driver.title)
            html = driver.page_source

            search = driver.find_element(By.NAME, 'q')
            

            store_name=store['store']
            search.send_keys(store_name+' 推薦')
            search.send_keys(Keys.ENTER)

            items = driver.find_elements(By.CLASS_NAME, "LC20lb")
            addrs = driver.find_elements(By.CLASS_NAME, "yuRUbf")
            stat = driver.find_element(By.ID, "result-stats")

            all = zip(items, addrs)

            for item in all:
                addr = item[1].find_element(By.TAG_NAME, 'a').get_attribute('href')
                title=item[0].text
                stat_text = stat.text
                stat_text=stat_text.split('(')[0]
                stat_text = re.sub(r'[^\d]', '', stat_text)  
                stat_number = int(stat_text)
                print(f'{title} - {addr}')
                google_cursor = conn.cursor()
                google_cursor.execute("INSERT INTO google_search_article (store, article_title, article_link, article_stat, created_time) VALUES (%s, %s, %s, %s, %s)",
                        (store_name, title, addr, stat_number,currentDateAndTime))

            print(f'Stat: {stat_number}')
            conn.commit()

            driver.quit()

            time.sleep(10)


    except NoSuchElementException:
        print('無法定位')

    driver.quit()
    conn.close()


handler(event=None, context=None)