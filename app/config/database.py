import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseConfig:
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', '3piposuser')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '3piposuser')
    DB_NAME = os.getenv('DB_NAME', '3pipos')
    DB_CHARSET = 'utf8mb4'

def get_db_connection():
    return pymysql.connect(
        host=DatabaseConfig.DB_HOST,
        user=DatabaseConfig.DB_USER,
        password=DatabaseConfig.DB_PASSWORD,
        database=DatabaseConfig.DB_NAME,
        charset=DatabaseConfig.DB_CHARSET,
        cursorclass=pymysql.cursors.DictCursor
    )