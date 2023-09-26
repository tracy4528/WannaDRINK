from flask import Flask, render_template, request
import json
import pymysql
from dotenv import load_dotenv
import os
import flask.json.provider
from datetime import datetime
import re




load_dotenv()

app = Flask(__name__)
app.json.ensure_ascii = False
flask.json.provider.DefaultJSONProvider.sort_keys = False

conn = pymysql.connect(host=os.getenv('mysql_host'), 
                       user=os.getenv('mysql_user'),
                       password=os.getenv('mysql_password'), 
                       database='product',
                       cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

@app.route("/")
def hello():
    return render_template("index.html")

@app.route('/api/v1/hotword', methods=['GET'])
def get_keyword():
    sql = "SELECT keyword FROM hot_keyword order by id desc limit 1 "
    cursor.execute(sql)
    products = cursor.fetchall()
    text = products[0]['keyword'].split('\n')[0].split('：')[1].split('、')

    response = {
        'data': text
                }
    return response

@app.route("/api/v1/hot_article")
def hot_article():
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
    return response


@app.route("/submit", methods=["POST"])
def submit():

    drink1 = request.form.get("drink1")
    drink="%"+drink1+"%"
    sql = f"SELECT store,name,image_url FROM foodpanda where name like '{drink}' order by store_review_number desc limit 10;"
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
        
    return response

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=8000)