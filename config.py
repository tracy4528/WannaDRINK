import os
from dotenv import load_dotenv
import logging


load_dotenv()

        
class MysqlpoolConfig:
    def __init__(self):
        self.DB_HOST = os.environ.get('mysql_host')
        self.DB_USERNAME = os.environ.get('mysql_user')
        self.DB_PASSWORD = os.environ.get('mysql_password')
        self.DB_DATABASE = os.environ.get('mysql_database')
        self.db_config = {
                        "pool_name":"wannadrink",
                        "pool_size":5,
                        "user": self.DB_USERNAME,
                        "host": self.DB_HOST,
                        "password": self.DB_PASSWORD,
                        "database": self.DB_DATABASE}
        

class OpenaiConfig:
    def __init__(self):
        self.Openai_token = os.environ.get('openai_key')


class S3Config:
    def __init__(self):
        self.AWS_ACCESS_KEY = os.getenv("iam_drink_key")
        self.AWS_SECRET_KEY = os.getenv("iam_drink_secretkey")
        self.s3_config = {
                        "region_name":"ap-northeast-1",
                        "aws_access_key_id":self.AWS_ACCESS_KEY,
                        "aws_secret_access_key":self.AWS_SECRET_KEY}

