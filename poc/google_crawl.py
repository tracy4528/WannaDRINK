import os
import re
import time
import pandas as pd
from datetime import datetime
from selenium import webdriver
from bs4 import BeautifulSoup as Soup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC



driver = webdriver.Chrome()
search_url = "https://www.google.com.tw/maps"
driver.get(search_url)
time.sleep(2)
driver.maximize_window()

Search_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "searchboxinput")))
Search_box.clear()
key ='十方盒餐'
Search_box.send_keys(key)
Search_box.send_keys(Keys.ENTER)
print('2')

# This will expand the list of reviews on the Google Maps page."//*[@id='QA0Szd']/div/div/div[1]/div[2]/div/div[1]/div/div/div[55]/div/button/div/span"
More_reviews= WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@jsaction ='pane.reviewChart.moreReviews']")))
More_reviews.click()
#This will open a dropdown menu with sorting options.
Sorted= WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='QA0Szd']/div/div/div[1]/div[2]/div/div[1]/div/div/div[45]/div[2]/button")))
Sorted.click()
#This will select the option to sort the reviews by the most recent ones. 
Latest= WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//*[@id='action-menu']/div[2]']")))[1]
Latest.click()
print('3')
time.sleep(3)


text = []
new_text =[]
for i in range(50):
    #locates the scrollable body element of the Google Maps review section 
    scroll_body= WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH,'//[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]')))
    #click all the "Extend" buttons one by one
    extends = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, 
                 "//*[@id='ChZDSUhNMG9nS0VJQ0FnSUN3dV9qMUZnEAE']/span[2]/button")))
    for extend in extends:
        extend.click()
        time.sleep(3) 
    #finds all the review cards on the page
    Review_cards = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='GHT2ce']")))
    for i in Review_cards:
        text_obj = i.find_element(By.XPATH, ".//span[@jsan='7.wiI7pd']")
        text.append(text_obj.text)
    #executes a JavaScript script to scroll the page down to load more reviews. 
    driver.execute_script('arguments[0].scrollBy(0,7100);', scroll_body)
    time.sleep(3)
# for the last date of review
Date_end = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//*[@id='QA0Szd']/div/div/div[1]/div[2]/div/div[1]/div/div/div[5]/div[9]/div[1]/div[2]/div[3]/div[4]/div[1]/span[3]/span[1]")))
Date_text = Date_end.text
print(Date_text)
#remove duplicate reviews from the text list and store the unique reviews in the new_text list.
for t in text:
    if t not in new_text:
        new_text.append(t)

for new_t in new_text:
    print(new_t)