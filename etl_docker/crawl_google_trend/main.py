from pytrends.request import TrendReq
import pymysql
from dotenv import load_dotenv
import os
from datetime import datetime
import time
import requests

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
          
          pytrend.build_payload(
               kw_list=keyword_batch,
               cat=0,
               timeframe='today 1-m',
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



def line_notify(message):
    token = os.getenv('line_token')
    headers = {"Authorization": "Bearer " + token}
    data = {'message': message}
    requests.post("https://notify-api.line.me/api/notify", headers=headers, data=data)

def handler(event=None, context=None):
    get_googletrend(keywords,batch_size)
    message_finish = f'Finished google trend crawl! Successfully inserted  into MySQL'
    line_notify(message_finish)

