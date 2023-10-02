import os
from dotenv import load_dotenv
import pymysql
import logging


load_dotenv()

class MysqlConfig:
    def __init__(self):
        self.DB_HOST = os.environ.get('mysql_host')
        self.DB_HOST = os.environ.get('mysql_host')
        self.DB_USERNAME = os.environ.get('mysql_user')
        self.DB_PASSWORD = os.environ.get('mysql_password')
        self.DB_DATABASE = os.environ.get('mysql_database')
        self.db_config = {"host": self.DB_HOST,
                        "user": self.DB_USERNAME,
                        "password": self.DB_PASSWORD,
                        "database": self.DB_DATABASE,
                        'cursorclass':pymysql.cursors.DictCursor}
        

class OpenaiConfig:
    def __init__(self):
        self.Openai_token = os.environ.get('openai_key')


class S3Config:
    def __init__(self):
        self.AWS_ACCESS_KEY = os.getenv("iam_drink_key")
        self.AWS_SECRET_KEY = os.getenv("iam_drink_secretkey")

class LoggingConfig:
    def __init__(self):
        self.level = logging.INFO
        self.datefmt = "%Y-%m-%d %H:%M"
        self.format = "%(asctime)s %(levelname)s %(message)s"
        self.handlers = [logging.FileHandler("log/wannadrink.log", "w", "utf-8")]
        self.logging_config = {"level": self.level,
                               "datefmt": self.datefmt,
                               "format": self.format,
                               "handlers": self.handlers}