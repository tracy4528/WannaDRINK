from server import app
from flask import request, render_template, jsonify
import os
import datetime
import pymysql
from config import MysqlConfig,S3Config,LoggingConfig
import logging
import mysql.connector.pooling


my_db_conf = MysqlConfig()
my_aws_conf = S3Config()
my_logging_conf = LoggingConfig()

conn = pymysql.connect(**my_db_conf.db_config)
# db_pool = mysql.connector.pooling.MySQLConnectionPool(
#     pool_name="wannadrink",
#     pool_size=5,
#     host=os.getenv('mysql_host'), 
#     user=os.getenv('mysql_user'),
#     password=os.getenv('mysql_password'), 
#     database='product'
# )
# conn= db_pool.get_connection()
cursor = conn.cursor()

# create logger
logging.basicConfig(**my_logging_conf.logging_config)
wannadrink_logger = logging.getLogger("wannadrink")
wannadrink_logger.setLevel(wannadrink_logger.level)



@app.route("/")
def hello():
    return render_template("index.html")


@app.route('/map.html')
def map():
    return render_template('map.html')


@app.route('/api/v1/hotword', methods=['GET'])
def get_keyword():
    # sql = "SELECT keyword FROM hot_keyword order by id desc limit 2 "
    # cursor.execute(sql)
    # products = cursor.fetchall()
    # text1=products[1]['keyword'].split('格式：')[-1]
    # text = products[0]['keyword'].split('\n')[0].split('：')[1].split('、')
    drink=['清心-蜜桃凍紅茶','烏弄','Tea Top','八曜','山焙','坪林手','鶴茶樓-桂花烏龍','一沐日-粉粿']

    response = {
        'data': drink,
                }
    return response

@app.route("/api/v1/hot_article")
def hot_article():
    try:
        today_date = datetime.date.today().strftime('%Y%m%d')
        sql = f"SELECT * FROM ptt_articles WHERE crawl_date = {today_date} ORDER BY push DESC LIMIT 5"
        cursor = conn.cursor()
        cursor.execute(sql)
        article = cursor.fetchall()

        data= [
            {
                "title": v["title"],
                'path':v["url"]
            }
            for v in article
        ]


        # sql_dcard = "SELECT * FROM dcard_articles WHERE crawl_date ='20231003' ORDER BY push DESC LIMIT 2"
        # cursor_dcard = conn.cursor()
        # cursor_dcard.execute(sql_dcard)
        # dcard_articles = cursor_dcard.fetchall()

        # data += [
        #     {
        #         "title": v["title"],
        #         'path': v["url"]
        #     }
        #     for v in dcard_articles
        # ]
        response = {
            'data': data,
            'date':today_date
        }

    except Exception as e:
        response = {
            'error': str(e)
        }
        wannadrink_logger.warning(f"[Error] Query hot article : {e}")
    finally:
        cursor.close()

    return response





@app.route("/search", methods=["POST"])
def search_bar():
    try:
        search = request.form.get("search")
        search="%"+search+"%"
        cursor = conn.cursor()
        sql = f"SELECT store,image_s3 FROM drink_list where name like '{search}'or store like'{search}' group by store  limit 5;"
        cursor.execute(sql)
        keyword = cursor.fetchall()

        sql_cursor = conn.cursor()
        sql_google=f"SELECT store,article_link,article_title FROM google_search_article where store like '{search}' limit 4;"
        sql_cursor.execute(sql_google)
        hot= sql_cursor.fetchall()

        top_cursor = conn.cursor()
        sql = f"SELECT name,image_s3 FROM drink_list where store like '{search}' and category_name like '%推薦%';"
        top_cursor.execute(sql)
        recom= top_cursor.fetchall()

        data = [
            {
                "store": v["store"],
                "img": v["image_s3"]
            }
            for v in keyword
        ]

        article = [
            {
                'title':v['article_title'],
                "url": v["article_link"]
            }
            for v in hot
        ]

        rank = [97, 98, 99, 95, 99,97,96]

        top_data = [
            {
            'name': v['name'],
            'img': v['image_s3'],
            'rank': r

        }
        for v, r in zip(recom, rank)
        ]

        if not data:
            response['data'] = "no match"
        if not article:
            response['article'] = "no match"
        if not top_data:
            response['recom'] = "no match"

        response = {
            'data': data,
            'article':article,
            'recom':top_data
        }

    except Exception as e:
        response = {
            'error': str(e)
        }
        wannadrink_logger.warning(f"[Error] searching bar: {e}")
    finally:
        cursor.close()
    
    return render_template('search_result.html',response=response)

@app.route("/api/v1/menu", methods=['GET'])
def store_list_menu():
    try:
        keyword = request.args.get('keyword', '').strip()
        sql1 = "SELECT * FROM drink_list where store LIKE %s;"
        cursor = conn.cursor()
        cursor.execute(sql1, f"%{keyword}%")
        drink_data = cursor.fetchall()
        data = [
            {
                "name": v["name"],
                "description": v['description'],
                "img": v['image_s3']
            }
            for v in drink_data
        ]
        response = {
            'data': data  
        }
    except Exception as e:
        response = {
            'error': str(e)
        }
        wannadrink_logger.warning(f"[Error] searching menu: {e}")
    finally:
        cursor.close()
    return render_template('menu.html',response=response) 

