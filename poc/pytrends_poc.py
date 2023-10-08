from pytrends.request import TrendReq
from pprint import pprint
import pymysql
from dotenv import load_dotenv
import os
from datetime import datetime
import time

load_dotenv()

conn = pymysql.connect(host=os.getenv('mysql_host'), 
                       user=os.getenv('mysql_user'),
                       password=os.getenv('mysql_password'), 
                       database='product')
cursor = conn.cursor()

pytrend = TrendReq(hl='en-US', tz=360)
keywords=['WooTea五桐號','清心福全','可不可']
# keywords = [ '茶湯會','迷客夏','一沐日','再睡5分鐘','五十嵐','茶的魔手',
#             '大苑子','龜記','五桐號','不要對我尖叫','珍煮丹','大茗,'烏弄','coco都可']

for keyword in keywords:
     print(keyword)
     time.sleep(10)
     pytrend.build_payload(
          kw_list=keywords,
          cat=0,
          timeframe='today 3-m',
          geo='TW',
          gprop='')
     
interest_over_time_df = pytrend.interest_over_time()
for keyword in keywords:
     print(keyword)
     for index, row in interest_over_time_df.iterrows():
          insert_product_sql = ("INSERT INTO `google_trend` (store, trend_date,trend_num) "
                                             "VALUES (%s,%s,%s)")
          cursor.execute(insert_product_sql,(keyword,index,row[keyword]) )
     conn.commit() 




