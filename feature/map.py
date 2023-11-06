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

sql = f"SELECT distinct store_name,store_latitude, store_longitude,store_rating,store_image,store_review_number, store_url_fp  FROM store_info  where store_latitude > 24.5 and id>=633"

cursor.execute(sql)
store = cursor.fetchall()

for row in store:
    store_name, store_latitude, store_longitude, store_rating,store_image, store_review_number,store_url = row
    
    if store_rating >= 4.9:
        icon_color = 'green'
    elif 4.8 <= store_rating < 4.9:
        icon_color = 'orange'
    else:
        icon_color = 'red'
    
    popup_content = f"""
    <div style="text-align: center;">
        <img src='{store_image}' alt='{store_name}' width='150'><br>
        <h4>{store_name}</h4><br>
        ⭐️Rating: {store_rating}<br><br>
        Reviews: {store_review_number}<br><br>
        foodpanda: <a href='{store_url}' target='_blank'>order it!</a>
    </div>
    """
    
    
    folium.Marker([store_latitude, store_longitude], 
                  tooltip=store_name,
                  icon=folium.Icon(color=icon_color),
                  popup=folium.Popup(popup_content, max_width=300) 
                 ).add_to(fmap)
    


fmap.save('APP/server/templates/map.html')
