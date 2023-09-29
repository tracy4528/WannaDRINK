from server import app
from flask import request, render_template
import os
import datetime
import pymysql
from config import MysqlConfig,S3Config

my_db_conf = MysqlConfig()
my_aws_conf = S3Config()
conn = pymysql.connect(**my_db_conf.db_config)
cursor = conn.cursor()

@app.route("/")
def hello():
    return render_template("index.html")

@app.route('/api/v1/hotword', methods=['GET'])
def get_keyword():
    sql = "SELECT keyword FROM hot_keyword order by id desc limit 3 "
    cursor.execute(sql)
    products = cursor.fetchall()
    text1=products[1]['keyword'].split('格式：')[-1]
    text = products[0]['keyword'].split('\n')[0].split('：')[1].split('、')
    drink=['無糖茶','烏弄','Tea Top','白巷子','奶蓋烏龍','檸檬烏龍','一沐日','草仔粿奶茶']

    response = {
        'data': drink,
                }
    return response

@app.route("/api/v1/hot_article")
def hot_article():
    try:
        today_date = datetime.today().strftime('%Y%m%d')
        sql = f"SELECT * FROM ptt_articles WHERE crawl_date = '{today_date}' ORDER BY push DESC LIMIT 5"

        cursor.execute(sql)
        article = cursor.fetchall()
        dcard= [
            {
                "title": v["title"],
                'path':v["url"]
            }
            for v in article
        ]
        response = {
            'data': dcard,
            'date':today_date
        }
    except Exception as e:
        response = {
            'error': str(e)
        }
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