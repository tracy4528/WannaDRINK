import folium
import pymysql
from dotenv import load_dotenv
import os
load_dotenv()

fmap = folium.Map(location=[25.040614007044706, 121.56018820263856], zoom_start=16)

conn = pymysql.connect(host=os.getenv('mysql_host'), 
                       user=os.getenv('mysql_user'),
                       password=os.getenv('mysql_password'), 
                       database='product')
cursor = conn.cursor()

sql = f"SELECT store_name,store_latitude, store_longitude,store_rating,store_review_number, store_url  FROM store_info"

cursor.execute(sql)
store = cursor.fetchall()

for row in store:
    store_name, store_latitude, store_longitude, store_rating, store_review_number,store_url = row
    
    if store_rating >= 4.5:
        icon_color = 'green'
    elif 4.0 <= store_rating < 4.5:
        icon_color = 'orange'
    else:
        icon_color = 'red'

    folium.Marker([store_latitude, store_longitude], 
                tooltip=store_name,
                icon=folium.Icon(color=icon_color),
                popup=f"Rating: {store_rating}<br>Reviews: {store_review_number}<br>foodpanda: {store_url}"
                ).add_to(fmap)
    




fmap.save('map.html')
