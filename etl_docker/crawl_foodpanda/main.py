import time
import os
import json
import requests
from dotenv import load_dotenv
import io
import bs4
import boto3
import pymysql

load_dotenv()


conn = pymysql.connect(host=os.getenv('mysql_host'), 
                user=os.getenv('mysql_user'),
                password=os.getenv('mysql_password'), 
                database='product')

def request_get(url, params=None, headers=None):
    r = requests.get(url, params=params, headers=headers)
    if r.status_code != requests.codes.ok:
        print(f'網頁載入發生問題：{url}')
        return None
    try:
        data = r.json()
    except Exception as e:
        print(e)
        return None
    return data

def get_nearby_restaurants(longitude, latitude, way='外送', sort='', cuisine='181', food_characteristic='',
                          budgets='', has_discount=False, limit=100, offset=0):
    url = 'https://disco.deliveryhero.io/listing/api/v1/pandora/vendors'
    query = {
        'longitude': longitude,
        'latitude': latitude,
        'language_id': 6,
        'include': 'characteristics',
        'dynamic_pricing': 0,
        'configuration': 'Variant1',
        'country': 'tw',
        'budgets': budgets,
        'cuisine': cuisine,
        'sort': sort,
        'food_characteristic': food_characteristic,
        'use_free_delivery_label': False,
        'vertical': 'restaurants',
        'limit': limit,
        'offset': offset,
        'customer_type': 'regular'
    }
    headers = {
        'x-disco-client-id': 'web',
    }

    if has_discount:
        query['has_discount'] = 1

    data = request_get(url=url, params=query, headers=headers)
    if not data:
        print('get nearby restaurants fail')
        return []

    try:
        restaurants = data['data']['items']
    except Exception as e:
        print(f'error: {e}')
        return []

    return restaurants

def get_info_menu(restaurant_code):
    url = f'https://tw.fd-api.com/api/v5/vendors/{restaurant_code}'
    query = {
        'include': 'menus',
        'language_id': '6',
        'dynamic_pricing': '0',
        'opening_type': 'delivery'
    }
    data = request_get(url=url, params=query)
    if (not data) or ('data' not in data):
        print('get menu fail')
        return {}
    info_menu = data['data']
    json_data = json.dumps(info_menu, ensure_ascii=False, indent=2)
    bucket_name = 'wannadrink'
    s3_object_key = f'foodpanda/{restaurant_code}_menu.json'
    s3 = boto3.client('s3', region_name='ap-northeast-1',
                      aws_access_key_id=os.getenv('iam_drink_key'),
                      aws_secret_access_key=os.getenv('iam_drink_secretkey'))
    s3.put_object(
        Bucket=bucket_name,
        Key=s3_object_key,
        Body=json_data,
        ContentType='application/json'
    )

    return info_menu


if __name__ == '__main__':
    stations=[(121.56716, 25.04106),(121.53442,25.01482),(120.2129832,22.9970861),(120.68481,24.13693),(120.21146, 22.98962) ]
    for station in stations:
        print(station[0], station[1])
        longitude, latitude = station[0], station[1]
        restaurants = get_nearby_restaurants(
            longitude, latitude,
            sort='rating_desc',
            cuisine='181'
        )
        for restaurant in restaurants:
            code=restaurant['code']
            name=restaurant['name']
            rating=restaurant['rating']
            review_number=restaurant['review_number']
            print(restaurant)
        #     cursor = conn.cursor()
        #     insert_product_sql = ("INSERT INTO `foodpanda_store_code` (store_code,store_name,rating,review_number)VALUES (%s,%s,%s,%s)")
        #     cursor.execute(insert_product_sql,(code, name,rating,review_number))
        #     print(f'==={name}===')
        # conn.commit()

    # sql='SELECT MIN(store_code) AS store_code, original_name\
    #     FROM product.foodpanda_store_code\
    #     GROUP BY original_name;'
    # cursor = conn.cursor()
    # cursor.execute(sql)
    # store = cursor.fetchall()
    
    # for item in store[200:]:
    #     foodpanda_spider.get_info_menu(item[0])
    #     print(f'==={item[1]}===')
    








# def handler(event=None, context=None):
