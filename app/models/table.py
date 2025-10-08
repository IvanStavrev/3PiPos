from app.config.database import get_db_connection
from datetime import datetime

class Table:
    def __init__(self, id=None, table_name=None, table_seats=None, table_status='free', 
                 table_reservedby=None, table_unreservedby=None, table_reservationnote=None, 
                 created_at=None, updated_at=None):
        self.id = id
        self.table_name = table_name
        self.table_seats = table_seats
        self.table_status = table_status
        self.table_reservedby = table_reservedby
        self.table_unreservedby = table_unreservedby
        self.table_reservationnote = table_reservationnote
        self.created_at = created_at
        self.updated_at = updated_at
    
    def create(self):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                INSERT INTO tables (table_name, table_seats, table_status, table_reservationnote) 
                VALUES (%s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    self.table_name, 
                    self.table_seats, 
                    self.table_status, 
                    self.table_reservationnote
                ))
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
                sql = """
                SELECT t.*, 
                       ur.name as reservedby_name, 
                       uur.name as unreservedby_name
                FROM tables t
                LEFT JOIN users ur ON t.table_reservedby = ur.user_id
                LEFT JOIN users uur ON t.table_unreservedby = uur.user_id
                ORDER BY t.table_name
                """
                cursor.execute(sql)
                return cursor.fetchall()
        finally:
            connection.close()
    
    @staticmethod
    def get_by_id(table_id):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM tables WHERE id = %s"
                cursor.execute(sql, (table_id,))
                table_data = cursor.fetchone()
                if table_data:
                    return Table(**table_data)
                return None
        finally:
            connection.close()
    
    def update(self):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                UPDATE tables 
                SET table_name = %s, table_seats = %s, table_status = %s, 
                    table_reservationnote = %s 
                WHERE id = %s
                """
                cursor.execute(sql, (
                    self.table_name, self.table_seats, self.table_status,
                    self.table_reservationnote, self.id
                ))
                connection.commit()
                return True
        finally:
            connection.close()
    
    def reserve(self, user_id, note=None):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                UPDATE tables 
                SET table_status = 'reserved', 
                    table_reservedby = %s,
                    table_reservationnote = %s
                WHERE id = %s
                """
                cursor.execute(sql, (user_id, note, self.id))
                connection.commit()
                return True
        finally:
            connection.close()
    
    def occupy(self, user_id):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                UPDATE tables 
                SET table_status = 'occupied',
                    table_reservedby = %s
                WHERE id = %s
                """
                cursor.execute(sql, (user_id, self.id))
                connection.commit()
                return True
        finally:
            connection.close()
    
    def free(self, user_id):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                UPDATE tables 
                SET table_status = 'free',
                    table_unreservedby = %s,
                    table_reservedby = NULL,
                    table_reservationnote = NULL
                WHERE id = %s
                """
                cursor.execute(sql, (user_id, self.id))
                connection.commit()
                return True
        finally:
            connection.close()
    
    @staticmethod
    def delete(table_id):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "DELETE FROM tables WHERE id = %s"
                cursor.execute(sql, (table_id,))
                connection.commit()
                return cursor.rowcount > 0
        finally:
            connection.close()