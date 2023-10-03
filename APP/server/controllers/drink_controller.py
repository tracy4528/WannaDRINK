from server import app
from flask import request, render_template, jsonify
import os
import datetime
import pymysql
from config import MysqlConfig,S3Config,LoggingConfig
import logging


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



@app.route('/api/v1/hotword', methods=['GET'])
def get_keyword():
    # sql = "SELECT keyword FROM hot_keyword order by id desc limit 3 "
    # cursor.execute(sql)
    # products = cursor.fetchall()
    # text1=products[1]['keyword'].split('格式：')[-1]
    # text = products[0]['keyword'].split('\n')[0].split('：')[1].split('、')
    drink=['無糖茶','烏弄','Tea Top','白巷子','奶蓋烏龍','檸檬烏龍','一沐日','草仔粿奶茶']

    response = {
        'data': drink,
                }
    return response

@app.route("/api/v1/hot_article")
def hot_article():
    try:
        today_date = datetime.date.today().strftime('%Y%m%d')
        sql = f"SELECT * FROM ptt_articles WHERE crawl_date = {today_date} ORDER BY push DESC LIMIT 5"

        cursor.execute(sql)
        article = cursor.fetchall()
        ptt= [
            {
                "title": v["title"],
                'path':v["url"]
            }
            for v in article
        ]
        response = {
            'data': ptt,
            'date':today_date
        }
    except Exception as e:
        response = {
            'error': str(e)
        }
        wannadrink_logger.warning(f"[Error] Query hot article : {e}")
    return response


@app.route("/api/v1/user_drink", methods=["POST"])
def submit():

    drink1 = request.form.get("drink1")
    drink="%"+drink1+"%"
    sql = f"SELECT store,name,image_url,product_id FROM drink_list where name like '{drink}' order by store_review_number desc limit 5;"
    cursor.execute(sql)
    drink = cursor.fetchall()
    data= [
        {
            "store": v["store"],
            'name':v["name"],
            'imageUrl':v["image_url"]
        }
        for v in drink
    ]
    response={
        'data':data
    }
        
    return render_template('recom.html',response=response)


@app.route("/search", methods=["POST"])
def search_bar():

    search = request.form.get("search")
    search="%"+search+"%"
    sql = f"SELECT * FROM drink_list where name like '{search}'or store like'{search}' group by store  limit 15;"
    cursor.execute(sql)
    keyword = cursor.fetchall()
    data= [
        {
            "store": v["store"],
            "img":v["image_url"]
                            }
        for v in keyword
    ]
    response={
        'data':data
    }
    return render_template('search_result.html',response=response)

@app.route("/api/v1/menu", methods=['GET'])
def store_list_menu():
    keyword = request.args.get('keyword', '').strip()
    sql1 = "SELECT * FROM drink_list where store LIKE %s;"
    cursor.execute(sql1, f"%{keyword}%")
    drink_data = cursor.fetchall()
    data = [
        {
            "name": v["name"],
            "description": v['description'],
            "img": v['image_url']
        }
        for v in drink_data
    ]
    response = {
        'data': data  
    }
    return render_template('menu.html',response=response) 


@app.route("/submit_rating", methods=["POST"])
def submit_rating():
    rating = request.form.get("rating")
    item_id = request.form.get("item_id")
    

    return redirect("/")  