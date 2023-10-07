from pytrends.request import TrendReq
from pprint import pprint
import pymysql
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

conn = pymysql.connect(host=os.getenv('mysql_host'), 
                       user=os.getenv('mysql_user'),
                       password=os.getenv('mysql_password'), 
                       database='product')
cursor = conn.cursor()


pytrend = TrendReq(hl='en-US', tz=360)
keywords = ['可不可', '清心福全', '茶湯會','迷客夏','一沐日']
pytrend.build_payload(
     kw_list=keywords,
     cat=0,
     timeframe='today 1-m',
     geo='TW',
     gprop='')

pprint(pytrend.interest_over_time())