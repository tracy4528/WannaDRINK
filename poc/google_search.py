from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import requests

driver = webdriver.Chrome()
driver.implicitly_wait(10)
driver.get('https://www.google.com/')
print(driver.title)
html = driver.page_source

try:
    search = driver.find_element(By.NAME, 'q')
    print(search.tag_name)
    
    search.send_keys('默沫 推薦')
    search.send_keys(Keys.ENTER)

    items = driver.find_elements(By.CLASS_NAME, "LC20lb")
    addrs = driver.find_elements(By.CLASS_NAME, "yuRUbf")

    all = zip(items, addrs)

    for item in all:
        addr = item[1].find_element(By.TAG_NAME, 'a').get_attribute('href')
        print(f'{item[0].text} - {addr}')

except NoSuchElementException:
    print('無法定位')

driver.quit()