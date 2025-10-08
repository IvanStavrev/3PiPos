from app.config.database import get_db_connection
import bcrypt
from datetime import datetime
import re

class User:
    def __init__(self, user_id=None, name=None, familyname=None, family_name=None, phone=None, password=None, role=None, created_at=None, updated_at=None):
        self.user_id = user_id
        self.name = name
        # Support both database column name and form field name
        self.familyname = familyname or family_name
        self.phone = phone
        self.password = password
        self.role = role
        self.created_at = created_at
        self.updated_at = updated_at
    
    # Property for template compatibility
    @property
    def family_name(self):
        return self.familyname
    
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

    # Keep the old instance methods for compatibility
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
                # Use alias to map database column to Python attribute
                sql = "SELECT user_id, name, familyname as family_name, phone, role, created_at FROM users ORDER BY created_at DESC"
                cursor.execute(sql)
                users_data = cursor.fetchall()
                users = []
                for user_data in users_data:
                    users.append(User(**user_data))
                return users
        finally:
            connection.close()

    @staticmethod
    def get_by_id(user_id):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                # Use alias to map database column to Python attribute
                sql = "SELECT user_id, name, familyname as family_name, phone, role, created_at FROM users WHERE user_id = %s"
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

    # NEW STATIC METHODS for admin.py compatibility
    @staticmethod
    def create_user(name, family_name, phone, password, role):
        """Static method for creating users - used by admin.py"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                INSERT INTO users (name, familyname, phone, password, role) 
                VALUES (%s, %s, %s, %s, %s)
                """
                hashed_password = User.hash_password(password)
                
                print(f"=== PYMySQL CREATE USER DEBUG ===")
                print(f"SQL: {sql}")
                print(f"Values: ({name}, {family_name}, {phone}, {hashed_password[:20]}..., {role})")
                
                cursor.execute(sql, (
                    name, 
                    family_name,
                    phone, 
                    hashed_password, 
                    role
                ))
                connection.commit()
                
                user_id = cursor.lastrowid
                print(f"User created successfully with ID: {user_id}")
                print(f"===================================")
                
                return user_id
                
        except Exception as e:
            print(f"=== PYMySQL CREATE USER ERROR ===")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            print(f"===================================")
            
            if connection:
                connection.rollback()
            raise e
        finally:
            if connection:
                connection.close()

    @staticmethod
    def update_user(user_id, update_data):
        """Static method for updating users - used by admin.py"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                if 'password' in update_data:
                    sql = """
                    UPDATE users 
                    SET name = %s, familyname = %s, phone = %s, password = %s, role = %s 
                    WHERE user_id = %s
                    """
                    hashed_password = User.hash_password(update_data['password'])
                    cursor.execute(sql, (
                        update_data['name'], 
                        update_data['family_name'],
                        update_data['phone'], 
                        hashed_password, 
                        update_data['role'], 
                        user_id
                    ))
                else:
                    sql = """
                    UPDATE users 
                    SET name = %s, familyname = %s, phone = %s, role = %s 
                    WHERE user_id = %s
                    """
                    cursor.execute(sql, (
                        update_data['name'], 
                        update_data['family_name'],
                        update_data['phone'], 
                        update_data['role'], 
                        user_id
                    ))
                connection.commit()
                return cursor.rowcount > 0
        except Exception as e:
            if connection:
                connection.rollback()
            raise e
        finally:
            if connection:
                connection.close()

    @staticmethod
    def delete_user(user_id):
        """Static method for deleting users - used by admin.py"""
        return User.delete(user_id)

    @staticmethod
    def is_phone_unique(phone, exclude_user_id=None):
        """Check if phone number is unique"""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                if exclude_user_id:
                    sql = "SELECT user_id FROM users WHERE phone = %s AND user_id != %s"
                    cursor.execute(sql, (phone, exclude_user_id))
                else:
                    sql = "SELECT user_id FROM users WHERE phone = %s"
                    cursor.execute(sql, (phone,))
                
                return cursor.fetchone() is None
        finally:
            connection.close()

    @staticmethod
    def validate_user_data(name, family_name, phone, password, role):
        errors = []
        
        # Name validation - UPDATED FOR CYRILLIC
        if not name or len(name.strip()) < 2:
            errors.append("Name must be at least 2 characters long")
        elif len(name) > 50:
            errors.append("Name must be less than 50 characters")
        elif not re.match(r'^[a-zA-Z\u0400-\u04FF\s]+$', name):
            errors.append("Name can only contain letters and spaces")
        
        # Family name validation - UPDATED FOR CYRILLIC
        if not family_name or len(family_name.strip()) < 2:
            errors.append("Family name must be at least 2 characters long")
        elif len(family_name) > 50:
            errors.append("Family name must be less than 50 characters")
        elif not re.match(r'^[a-zA-Z\u0400-\u04FF\s]+$', family_name):
            errors.append("Family name can only contain letters and spaces")
        
        # Phone validation
        if not phone:
            errors.append("Phone number is required")
        elif not re.match(r'^\+?[0-9\s\-\(\)]{10,}$', phone):
            errors.append("Please enter a valid phone number")
        
        # Password validation (only for new users or when password is provided)
        if password and len(password) < 6:
            errors.append("Password must be at least 6 characters long")
        
        # Role validation
        valid_roles = ['admin', 'waiter', 'bar', 'kitchen']
        if role not in valid_roles:
            errors.append("Invalid role selected")
        
        return errors