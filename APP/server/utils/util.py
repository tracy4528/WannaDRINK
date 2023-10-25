import os
import mysql.connector
from mysql.connector import pooling

from config import MysqlpoolConfig

def dir_last_updated(folder):
    return str(max(os.path.getmtime(os.path.join(root_path, f))
                   for root_path, dirs, files in os.walk(folder)
                   for f in files))


def initialize_mysql_pool():
    my_db_conf = MysqlpoolConfig()
    mysql_pool = pooling.MySQLConnectionPool(**my_db_conf.db_config)
    return mysql_pool



