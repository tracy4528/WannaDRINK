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

@app.route('/drink_quiz')
def drink_quiz():
    return render_template('drink_quiz.html')

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


@app.route("/api/v1/user_drink", methods=["POST"])
def submit():
    try:
        drink1 = request.form.get("drink1")
        drink="%"+drink1+"%"
        sql = f"SELECT store,name,image_url,product_id FROM drink_list where name like '{drink}' order by store_review_number desc limit 5;"
        cursor = conn.cursor()
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

    except Exception as e:
        response = {
            'error': str(e)
        }
        wannadrink_logger.warning(f"[Error] searching bar: {e}")
    finally:
        cursor.close()
        
    return render_template('recom.html',response=response)


@app.route("/search", methods=["POST"])
def search_bar():
    try:
        search = request.form.get("search")
        search="%"+search+"%"
        cursor = conn.cursor()
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
                "img": v['image_url']
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


# @app.route("/submit_rating", methods=["POST"])
# def submit_rating():
#     rating = request.form.get("rating")
#     item_id = request.form.get("item_id")
    

#     return redirect("/")  


@app.route("/api/v1/profile", methods=["GET"])
def user_recom():

    # product = request.form.get("drink1")
    productid='253'

    sql = f"SELECT item2_id FROM product.similarity_model where item1_id ='{productid}' order by similarity desc limit 5;"
    cursor = conn.cursor()
    cursor.execute(sql)
    item2_ids = cursor.fetchall()
    item2_ids.append({"item2_id": "253"})
    data = []

    for item2_id in item2_ids:
        item2_id = item2_id['item2_id']
        sql_info = f"SELECT id,name, store, image_url FROM drink_list WHERE id = '{item2_id}';"
        drink_cursor = conn.cursor()
        drink_cursor.execute(sql_info)
        info = drink_cursor.fetchone()
        # data.append(info)
        data.append({
            "id":info['id'],
            "store": info["store"],
            "name": info["name"],
            "imageUrl": info["image_url"]
            })

    recently_rated = data[:2]
    recommended = data[2:]

    response = {
        'recently_rated': recently_rated,
        'recommended': recommended
    }
    # return response

    return render_template('member.html',response=response)