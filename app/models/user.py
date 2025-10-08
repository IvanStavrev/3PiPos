from app.config.database import get_db_connection
import bcrypt
from datetime import datetime

class User:
    def __init__(self, user_id=None, name=None, familyname=None, phone=None, password=None, role=None, created_at=None, updated_at=None):
        self.user_id = user_id
        self.name = name
        self.familyname = familyname
        self.phone = phone
        self.password = password
        self.role = role
        self.created_at = created_at
        self.updated_at = updated_at
    
    @staticmethod
    def hash_password(password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))
    
    @staticmethod
    def authenticate_by_password(password):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM users"
                cursor.execute(sql)
                users_data = cursor.fetchall()
                
                for user_data in users_data:
                    user = User(**user_data)
                    if user.verify_password(password):
                        return user
                return None
        finally:
            connection.close()

    # ... keep all the other methods the same (create, get_all, get_by_id, update, delete) ...
    def create(self):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                INSERT INTO users (name, familyname, phone, password, role) 
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    self.name, 
                    self.familyname, 
                    self.phone, 
                    self.hash_password(self.password), 
                    self.role
                ))
                connection.commit()
                self.user_id = cursor.lastrowid
                return self.user_id
        finally:
            connection.close()
    
    @staticmethod
    def get_all():
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT user_id, name, familyname, phone, role, created_at FROM users ORDER BY created_at DESC"
                cursor.execute(sql)
                users = cursor.fetchall()
                return [User(**user) for user in users]
        finally:
            connection.close()
    
    @staticmethod
    def get_by_id(user_id):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT user_id, name, familyname, phone, role, created_at FROM users WHERE user_id = %s"
                cursor.execute(sql, (user_id,))
                user_data = cursor.fetchone()
                if user_data:
                    return User(**user_data)
                return None
        finally:
            connection.close()
    
    def update(self):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                if self.password:
                    sql = """
                    UPDATE users 
                    SET name = %s, familyname = %s, phone = %s, password = %s, role = %s 
                    WHERE user_id = %s
                    """
                    cursor.execute(sql, (
                        self.name, self.familyname, self.phone, 
                        self.hash_password(self.password), self.role, self.user_id
                    ))
                else:
                    sql = """
                    UPDATE users 
                    SET name = %s, familyname = %s, phone = %s, role = %s 
                    WHERE user_id = %s
                    """
                    cursor.execute(sql, (
                        self.name, self.familyname, self.phone, 
                        self.role, self.user_id
                    ))
                connection.commit()
                return True
        finally:
            connection.close()
    
    @staticmethod
    def delete(user_id):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "DELETE FROM users WHERE user_id = %s"
                cursor.execute(sql, (user_id,))
                connection.commit()
                return cursor.rowcount > 0
        finally:
            connection.close()