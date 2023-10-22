from pytrends.request import TrendReq
from pprint import pprint
import pymysql
from dotenv import load_dotenv
import os
from datetime import datetime
import time

load_dotenv()
batch_size = 5

conn = pymysql.connect(host=os.getenv('mysql_host'), 
                       user=os.getenv('mysql_user'),
                       password=os.getenv('mysql_password'), 
                       database='product')
cursor = conn.cursor()

pytrend = TrendReq(hl='en-US', tz=360)
keywords = ['茶湯會','迷客夏','一沐日','再睡5分鐘','五十嵐','茶的魔手','大苑子','龜記','五桐號','不要對我尖叫','珍煮丹','大茗','烏弄','coco都可']

def get_googletrend(keywords,batch_size):
     for i in range(0, len(keywords), batch_size):
          keyword_batch = keywords[i:i + batch_size]
          
          for keyword in keyword_batch:
               print(keyword)
          
          time.sleep(10)
          
          # Build payload for the current batch of keywords
          pytrend.build_payload(
               kw_list=keyword_batch,
               cat=0,
               timeframe='today 3-m',
               geo='TW',
               gprop=''
          )
          
          interest_over_time_df = pytrend.interest_over_time()
          
          for keyword in keyword_batch:
               print(keyword)
               for index, row in interest_over_time_df.iterrows():
                    trend_num = row[keyword]
                    insert_product_sql = ("INSERT INTO `google_trend` (store, trend_date, trend_num) "
                                        "VALUES (%s, %s, %s)")
                    cursor.execute(insert_product_sql, (keyword, index, trend_num))
          
          conn.commit()
     conn.close()

get_googletrend(keywords,batch_size)


