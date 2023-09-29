from flask import Flask
from config import Config
from flask_jwt_extended import JWTManager
import pymysql
from config import MysqlConfig,S3Config

my_db_conf = MysqlConfig()
my_aws_conf = S3Config()
conn = pymysql.connect(**my_db_conf.db_config)
cursor = conn.cursor()


class User:
    def __init__(self, provider, email, password, name, picture, access_token, access_expired):
        self.provider = provider
        self.email = email
        self.password = password
        self.name = name
        self.picture = picture
        self.access_token = access_token
        self.access_expired = access_expired

def get_user(email):
    try:
        # 执行查询操作
        cursor.execute(f"SELECT * FROM user WHERE email = '{email}'")
        user_data = cursor.fetchone()
        
        if user_data:
            # 将查询结果转换为字典
            user = User(*user_data)
            return user.__dict__
        else:
            return None
    except Exception as e:
        print(e)
        return None

def create_user(user):
    try:
        # 插入新用户数据
        insert_query = f"""
            INSERT INTO User (provider, email, password, name, picture, access_token, access_expired)
            VALUES ('{user.provider}', '{user.email}', '{user.password}', '{user.name}', '{user.picture}', '{user.access_token}', {user.access_expired})
        """
        cursor.execute(insert_query)
        conn.commit()
        return cursor.lastrowid  
    except Exception as e:
        print(e)
        return None