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

class FoodPandaSpider():

    def __init__(self, longitude, latitude) -> None:
        """
        :param longitude: 自身所在經度
        :param latitude: 自身所在緯度
        """
        self.longitude = longitude
        self.latitude = latitude
        self.s3 = boto3.client('s3',
                    region_name='ap-northeast-1',
                    aws_access_key_id=os.getenv('iam_drink_key'),
                    aws_secret_access_key=os.getenv('iam_drink_secretkey'))



    def request_get(self, url, params=None, headers=None):
        """送出 GET 請求，取得回傳 JSON 資料

        """
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

    def request_post(self, url, params=None, data=None, headers=None):
        """送出 POST 請求，取得回傳 JSON 資料

        """
        r = requests.post(url, params=params, data=data, headers=headers)
        if r.status_code != requests.codes.ok:
            print(f'網頁載入發生問題：{url}')
            return None
        try:
            data = r.json()
        except Exception as e:
            print(e)
            return None
        return data
    
    def search_restaurants(self, keyword, limit=1, offset=0):
        """搜尋餐廳

        :param keyword: 餐廳關鍵字
        :return restaurants: 搜尋結果餐廳列表
        """
        url = 'https://disco.deliveryhero.io/search/api/v1/feed'
        payload = {
            'q': keyword,
            'location': {
                'point': {
                    'longitude': self.longitude,  # 經度
                    'latitude': self.latitude  # 緯度
                }
            },
            'config': 'Variant17',
            'vertical_types': ['restaurants'],
            'include_component_types': ['vendors'],
            'include_fields': ['feed'],
            'language_id': '6',
            'opening_type': 'delivery',
            'platform': 'web',
            'language_code': 'zh',
            'customer_type': 'regular',
            'limit': limit,  # 一次最多顯示幾筆(預設 48 筆)
            'offset': offset,  # 偏移值，想要獲取更多資料時使用
            'dynamic_pricing': 0,
            'brand': 'foodpanda',
            'country_code': 'tw',
            'use_free_delivery_label': False
        }
        headers = {
            'content-type': "application/json",
        }
        data = self.request_post(url=url, data=json.dumps(payload), headers=headers)
        if not data:
            print('搜尋餐廳失敗')
            return []

        try:
            restaurants = data['feed']['items'][0]['items']
        except Exception as e:
            print(f'資料格式有誤：{e}')
            return []
        return restaurants




    def get_nearby_restaurants(
            self, way='外送', sort='', cuisine='181', food_characteristic='',
            budgets='', has_discount=False, limit=100, offset=0):
        """取得附近所有餐廳

        :param way: 取餐方式(外送、外帶自取、生鮮雜貨)
        :param sort: 餐廳排序(rating_desc、delivery_time_asc、distance_asc)
        :param cuisine: 料理種類
        :param food_characteristic: 特色
        :param budgets: 預算
        :param has_discount: 是否有折扣
        :return restaurants: 附近所有餐廳結果
        """
        url = 'https://disco.deliveryhero.io/listing/api/v1/pandora/vendors'
        query = {
            'longitude': self.longitude,
            'latitude': self.latitude,
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
        if way == '外送':
            query['vertical'] = 'restaurants'
        elif way == '外帶自取':
            query['vertical'] = 'restaurants'
            query['opening_type'] = 'pickup'
        else:
            query['vertical'] = 'shop'
        if has_discount:
            query['has_discount'] = 1

        data = self.request_get(url=url, params=query, headers=headers)
        if not data:
            print('取得附近所有餐廳失敗')
            return []

        try:
            restaurants = data['data']['items']
        except Exception as e:
            print(f'資料格式有誤：{e}')
            return []
        return restaurants


    def get_info_menu(self, restaurant_code):
        """取得餐廳基本資料與菜單

        :param restaurant_code: 餐廳代碼
        :return info_menu: 餐廳基本資料與菜單
        """
        url = f'https://tw.fd-api.com/api/v5/vendors/{restaurant_code}'
        query = {
            'include': 'menus',
            'language_id': '6',
            'dynamic_pricing': '0',
            'opening_type': 'delivery'
            # 'longitude': self.longitude,    # 非必要(影響顯示距離)
            # 'latitude': self.latitude
        }
        data = self.request_get(url=url, params=query)
        if (not data) or ('data' not in data):
            print('取得餐廳菜單失敗')
            return {}
        info_menu = data['data']
        json_data = json.dumps(info_menu, ensure_ascii=False, indent=2)
        bucket_name = 'wannadrink'
        s3_object_key=f'foodpanda/{restaurant_code}_menu.json'
        self.s3.put_object(
            Bucket=bucket_name,
            Key=s3_object_key,
            Body=json_data,
            ContentType='application/json'
        )
        print(f"成功将信息保存到S3：s3://{bucket_name}/{s3_object_key}")


        return info_menu


if __name__ == '__main__':
    station = (121.51613, 25.04745)  # 台北車站的經緯度

    foodpanda_spider = FoodPandaSpider(station[0], station[1])


    # restaurants = foodpanda_spider.get_nearby_restaurants(
    #     sort='rating_desc', 
    #     cuisine='181'  
    # )

    with open('/Users/tracy4528/Desktop/appwork/01personal/poc/store_list.json', 'r') as file:
        data = json.load(file)

    for item in data['store'][:50]:
        restaurants = foodpanda_spider.search_restaurants(item)
        for restaurant in restaurants:
            code=restaurant['code']
            name=restaurant['name']
            cursor = conn.cursor()
            insert_product_sql = ("INSERT INTO `foodpanda_store_code` (store_code,store_name,original_name)VALUES (%s,%s,%s)")
            cursor.execute(insert_product_sql,(code, name,item))
            print(f'==={item}===')
    conn.commit()

    # for restaurant in restaurants[:10]:
    #     code=restaurant['code']
    #     name=restaurant['name']
    #     cursor = conn.cursor()
    #     insert_product_sql = ("INSERT INTO `foodpanda_store_code` (store_code,store_name,original_name)VALUES (%s,%s,%s)")
    #     cursor.execute(insert_product_sql,(code, name))
    #     foodpanda_spider.get_info_menu(restaurant['code'])
    #     print(name)
    # conn.commit()




    """

    搜尋餐廳
    restaurants = foodpanda_spider.search_restaurants('星巴克')
    ## print(json.dumps(restaurants[0]))
    for restaurant in restaurants[:5]:
        print(restaurant['name'])



    取得分類推薦的餐廳
    recommendations = foodpanda_spider.get_recommendation_restaurants()
    for recommendation in recommendations[:5]:
        print(recommendation['headline'])

   """



