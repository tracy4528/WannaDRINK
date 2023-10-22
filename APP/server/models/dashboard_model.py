import os
from datetime import datetime
from dotenv import load_dotenv
import pymysql
import sys
# sys.path.append('/01personal/APP')
from server import app
from config import MysqlpoolConfig
import pandas as pd
import mysql.connector
from mysql.connector import pooling
import plotly.graph_objects as go




load_dotenv()
today_date = datetime.now().strftime("%Y%m%d")
my_db_conf = MysqlpoolConfig()
conn_pool = pooling.MySQLConnectionPool(**my_db_conf.db_config)
conn = conn_pool.get_connection()

def all_store():
    cursor = conn.cursor()

    sql = """SELECT count(*) FROM store_info;"""
    cursor.execute(sql)
    data = cursor.fetchone()

    brand_cursor = conn.cursor()
    sql_brand="SELECT count(distinct store) as num FROM drink_list ;"
    brand_cursor.execute(sql_brand)
    brand_data = brand_cursor.fetchone()
    
    drink_cursor = conn.cursor()
    sql_drink="SELECT count(*) as drink_num FROM drink_list;"
    drink_cursor.execute(sql_drink)
    drink_data = drink_cursor.fetchone()

    cursor.close()
    return data['count(*)'], brand_data['num'], drink_data['drink_num']

def drink_google_result():
    cursor = conn.cursor()
    sql = """SELECT avg(trend_num) as trend_index,store FROM product.google_trend group by store order by trend_index desc;"""
    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()
    result = {}
    for item in data:
        store=item['store']
        stat=item['trend_index']
        result[store] = stat
    return result


def store_google_trend():
    cursor = conn.cursor()

    sql = """SELECT * FROM google_trend where trend_date between '2023-09-01' AND '2023-09-30' """
    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()
    store_data = {  'Date': pd.date_range('2023-09-01', periods=30)}
    for item in data:
        store = item['store']
        trend_num = item['trend_num']
        if store not in store_data:
            store_data[store] = []
        store_data[store].append(trend_num)
    
    return store_data

def update_line_plot(selected_groups):
    data = {}
    df = pd.DataFrame(data)
    store_data=store_google_trend()
    for store, trend_nums in store_data.items():
            store_series = pd.Series(trend_nums, name=store)
            df = pd.concat([df, store_series], axis=1)
    lines = []
    for group in selected_groups:
        trace = go.Scatter(
            x=df['Date'],
            y=df[group],
            mode='lines+markers',
            name=group
        )
        lines.append(trace)

    layout = go.Layout(
        title='上個月手搖飲品牌聲量走勢, 資料來源：google trend 手搖飲主題,此資料已對結果進行標準化為範圍從 0 到 100 的相對值',
        xaxis=dict(title='Date'),
        yaxis=dict(title='Value'),
    )

    return lines,layout



def drink_quiz():
    cursor = conn.cursor()
    sql = """SELECT * FROM drink_quiz """
    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()
    url = [item['url'] for item in data ]
    title = [item['title'] for item in data ]

    return url,title
