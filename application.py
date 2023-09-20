from flask import Flask, render_template
import json
import pymysql
from dotenv import load_dotenv
import os
import flask.json.provider


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
    sql = "SELECT name FROM foodpanda limit 5 "
    cursor.execute(sql)
    products = cursor.fetchall()
    drink= [
        {
            "keyword": v["name"]
        }
        for v in products
    ]


    # drink = [product['name'] for product in products]
    response = {
        'data': drink
    }

    return response
    # for product in products:
    #     print(product)

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=8000)