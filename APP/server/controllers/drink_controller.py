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


@app.route('/api/v1/hot_drink', methods=['GET'])
def get_keyword():
    # sql = "SELECT store,drink_name,img  FROM hot_drink_frontend order by id limit 5;"
    # cursor = conn.cursor()
    # cursor.execute(sql)
    # drink = cursor.fetchall()
    # cursor.close()
    drink=[
        {
        "drink_name": "\u860b\u679c\u6842\u82b1",
        "img": "https://wannadrink.s3.ap-northeast-1.amazonaws.com/hot_drink_img/2023101601.jpeg",
        "store": "\u9ed8\u6cab\u624b\u4f5c\u98f2\u54c1"
        },
        {
        "drink_name": "\u4f2f\u7235\u5976\u8336",
        "img": "https://wannadrink.s3.ap-northeast-1.amazonaws.com/hot_drink_img/2023101602.jpeg",
        "store": "\u5148\u559d\u9053"
        },
        {
        "drink_name": "\u91d1\u8431\u70cf\u9f8d",
        "img": "https://wannadrink.s3.ap-northeast-1.amazonaws.com/hot_drink_img/2023101603.jpeg",
        "store": "\u70cf\u5f04"
        },
        {
        "drink_name": "\u860b\u679c\u7d05\u8431",
        "img": "https://wannadrink.s3.ap-northeast-1.amazonaws.com/hot_drink_img/2023101604.jpeg",
        "store": "\u9f9c\u8a18\u9298\u54c1"
        }
    ]

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
    response = {
        'data': [],
        'article': [],
        'recom': [],
    }

    try:
        search = request.form.get("search")
        search = "%" + search + "%"

        cursor = conn.cursor()
        sql_keyword = f"SELECT store, image_s3 FROM drink_list WHERE name LIKE '{search}' OR store LIKE '{search}' GROUP BY store LIMIT 5;"
        cursor.execute(sql_keyword)
        keyword = cursor.fetchall()

        sql_cursor = conn.cursor()
        sql_google = f"SELECT store, article_link, article_title FROM google_search_article WHERE store LIKE '{search}' LIMIT 4;"
        sql_cursor.execute(sql_google)
        hot = sql_cursor.fetchall()

        top_cursor = conn.cursor()
        sql_top = f"SELECT name, image_s3 FROM drink_list WHERE store LIKE '{search}' AND category_name LIKE '%推薦%';"
        top_cursor.execute(sql_top)
        recom = top_cursor.fetchall()

        if keyword:
            data = [
                {
                    "store": v["store"],
                    "img": v["image_s3"]
                }
                for v in keyword
            ]
            response['data'] = data
        if hot:
            article = [
                {
                    'title': v['article_title'],
                    "url": v["article_link"]
                }
                for v in hot
            ]
            response['article'] = article
        if recom:
            rank = [97, 98, 99, 95, 99, 97, 96]
            top_data = [
                {
                    'name': v['name'],
                    'img': v['image_s3'],
                    'rank': r
                }
                for v, r in zip(recom, rank)
            ]
            response['recom'] = top_data


    except Exception as e:
        response = {
            'error': str(e)
        }
        wannadrink_logger.warning(f"[Error] searching bar: {e}")

    finally:
        cursor.close()

    return render_template('search_result.html', response=response)


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

