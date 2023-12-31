from server import app
from flask import request, render_template, jsonify
import os
import datetime
import pymysql
from config import LoggingConfig
import logging
import mysql.connector
from mysql.connector import pooling
from server.utils.util import initialize_mysql_pool






conn_pool = initialize_mysql_pool()

my_logging_conf = LoggingConfig()
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
    conn = conn_pool.get_connection()
    sql = "SELECT store,drink_name,img  FROM hot_drink_frontend order by id desc limit 5;"
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql)
    drink = cursor.fetchall()
    

    response = {
        'data': drink,
                }
    cursor.close()
    conn.close() 
    return response



@app.route("/search", methods=["POST"])
def search_bar():
    response = {
        'data': []
    }

    try:
        search = request.form.get("search")
        search = "%" + search + "%"
        conn = conn_pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        sql_keyword = f"SELECT store, image_s3 FROM drink_list WHERE name LIKE '{search}' OR store LIKE '{search}' GROUP BY store LIMIT 5;"
        cursor.execute(sql_keyword)
        keyword = cursor.fetchall()

        if keyword:
            data = [
                {
                    "store": v["store"],
                    "img": v["image_s3"]
                }
                for v in keyword
            ]
            response['data'] = data


    except Exception as e:
        response = {
            'error': str(e)
        }
        wannadrink_logger.warning(f"[Error] searching bar: {e}")

    finally:
        cursor.close()
        conn.close() 

    return render_template('search_result.html', response=response)

@app.route("/api/v1/store_recom", methods=['GET'])
def store_recom():
    response = {
        'article': [],
        'recom': [],
    }
    try:
        search = request.args.get('keyword', '').strip()
        conn = conn_pool.get_connection()
        sql_cursor = conn.cursor(dictionary=True)
        sql_google = f"SELECT store, article_link, article_title FROM google_search_article WHERE store LIKE '%{search}%' LIMIT 4;"
        sql_cursor.execute(sql_google)
        hot = sql_cursor.fetchall()

        top_cursor = conn.cursor(dictionary=True)
        sql_top = f"SELECT name, image_s3,drink_rating_review FROM drink_list WHERE store LIKE '%{search}%' and drink_rating_review is not null;"
        top_cursor.execute(sql_top)
        recom = top_cursor.fetchall()

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
            top_data = [
                {
                    'name': v['name'],
                    'img': v['image_s3'],
                    'rank': v['drink_rating_review']
                }
                for v in recom
            ]
            response['recom'] = top_data

    except Exception as e:
        response = {
            'error': str(e)
        }
        wannadrink_logger.warning(f"[Error] searching store recommendation drink and article : {e}")
    finally:
        conn.close()
    return render_template('store.html',response=response) 


@app.route("/api/v1/menu", methods=['GET'])
def store_list_menu():
    try:
        keyword = request.args.get('keyword', '').strip()
        sql1 = "SELECT * FROM drink_list where store LIKE %s;"
        conn = conn_pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql1, f"%{keyword}%")
        drink_data = cursor.fetchall()
        data = [
            {
                "name": v["name"],
                "description": v['description'],
                "img": v['image_s3'],
                'rank': v['drink_rating_review']
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
        conn.close() 
    return render_template('menu.html',response=response) 

