from app.config.database import get_db_connection
from datetime import datetime

class Category:
    def __init__(self, id=None, category_name=None, created_at=None, updated_at=None):
        self.id = id
        self.category_name = category_name
        self.created_at = created_at
        self.updated_at = updated_at
    
    def create(self):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "INSERT INTO categories (category_name) VALUES (%s)"
                cursor.execute(sql, (self.category_name,))
                connection.commit()
                self.id = cursor.lastrowid
                return self.id
        finally:
            connection.close()
    
    @staticmethod
    def get_all():
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM categories ORDER BY category_name"
                cursor.execute(sql)
                return cursor.fetchall()
        finally:
            connection.close()
    
    @staticmethod
    def get_by_id(category_id):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM categories WHERE id = %s"
                cursor.execute(sql, (category_id,))
                category_data = cursor.fetchone()
                if category_data:
                    return Category(**category_data)
                return None
        finally:
            connection.close()
    
    def update(self):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "UPDATE categories SET category_name = %s WHERE id = %s"
                cursor.execute(sql, (self.category_name, self.id))
                connection.commit()
                return True
        finally:
            connection.close()
    
    @staticmethod
    def delete(category_id):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "DELETE FROM categories WHERE id = %s"
                cursor.execute(sql, (category_id,))
                connection.commit()
                return cursor.rowcount > 0
        finally:
            connection.close()