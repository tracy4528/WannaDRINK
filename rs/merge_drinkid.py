import os
import pymysql
from dotenv import load_dotenv


load_dotenv()


conn = pymysql.connect(host=os.getenv('mysql_host'), 
                       user=os.getenv('mysql_user'),
                       password=os.getenv('mysql_password'), 
                       database='product')
cursor = conn.cursor()


sql = "SELECT item1_id FROM similarity_model"
cursor.execute(sql)
cos_id = cursor.fetchall()


sql1 = "SELECT * FROM drink_list WHERE category_name LIKE '%招牌%' OR category_name LIKE '%推薦%' OR category_name LIKE'%銷%';"
cursor.execute(sql1)
drink_id = cursor.fetchall()
print(len(drink_id))
# print(drink_id)

