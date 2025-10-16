"""
Database Manager - Base class for CRUD operations
Provides common database operations for all CRUD classes
"""
import logging
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


class DBManager:
    """Base class for database operations with connection pooling"""
    
    def __init__(self, connection_pool):
        """
        Initialize DBManager with a connection pool
        
        Args:
            connection_pool: psycopg2 connection pool
        """
        self.connection_pool = connection_pool
    
    def _get_connection(self):
        """Get a connection from the pool"""
        return self.connection_pool.getconn()
    
    def _return_connection(self, conn):
        """Return a connection to the pool"""
        self.connection_pool.putconn(conn)
    
    def execute(self, query, params=None, fetch=False):
        """
        Execute a raw SQL query
        
        Args:
            query: SQL query string
            params: Query parameters tuple
            fetch: Whether to fetch results
        
        Returns:
            Query results if fetch=True, else None
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, params or ())
            
            if fetch:
                result = cursor.fetchall()
                return [dict(row) for row in result]
            
            conn.commit()
            return None
            
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {str(e)}")
            raise
        finally:
            if conn:
                self._return_connection(conn)
    
    def select(self, table, columns='*', where=None, where_params=None, order_by=None, limit=None):
        """
        Select records from a table
        
        Args:
            table: Table name
            columns: Columns to select (string or list)
            where: WHERE clause
            where_params: Parameters for WHERE clause
            order_by: ORDER BY clause
            limit: LIMIT value
        
        Returns:
            List of dictionaries representing rows
        """
        if isinstance(columns, list):
            columns = ', '.join(columns)
        
        query = f"SELECT {columns} FROM {table}"
        params = []
        
        if where:
            query += f" WHERE {where}"
            if where_params:
                params.extend(where_params if isinstance(where_params, tuple) else (where_params,))
        
        if order_by:
            query += f" ORDER BY {order_by}"
        
        if limit:
            query += f" LIMIT {limit}"
        
        return self.execute(query, tuple(params), fetch=True)
    
    def insert(self, table, data, on_conflict=None, conflict_target=None, returning_column=None):
        """
        Insert a record into a table
        
        Args:
            table: Table name
            data: Dictionary of column:value pairs
            on_conflict: Conflict resolution strategy ('nothing', 'update', etc.)
            conflict_target: Columns that define the conflict (for ON CONFLICT clause)
            returning_column: Column name to return (defaults to table-specific ID column)
        
        Returns:
            ID of inserted row (or None if ON CONFLICT DO NOTHING skips insert)
        """
        if not data:
            raise ValueError("No data provided for insert")
        
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        values = tuple(data.values())
        
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        # Add ON CONFLICT clause if specified
        if on_conflict and conflict_target:
            conflict_cols = ', '.join(conflict_target)
            if on_conflict.lower() == 'nothing':
                query += f" ON CONFLICT ({conflict_cols}) DO NOTHING"
            elif on_conflict.lower() == 'update':
                # Create SET clause for UPDATE
                set_clause = ', '.join([f"{col} = EXCLUDED.{col}" for col in data.keys()])
                query += f" ON CONFLICT ({conflict_cols}) DO UPDATE SET {set_clause}"
        
        # Determine the ID column name based on table
        if returning_column:
            id_column = returning_column
        else:
            # Map table names to their ID column names
            id_column_map = {
                'images': 'image_id',
                'profiles': 'profile_id',
                'tags': 'tag_id',
                'conversations': 'conversation_id',
                'messages': 'message_id',
                'notifications': 'notification_id',
                'user_locations': 'location_id'
            }
            id_column = id_column_map.get(table, 'id')
        
        query += f" RETURNING {id_column}"
        
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(query, values)
            result = cursor.fetchone()
            conn.commit()
            return result[0] if result else None
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Insert error: {str(e)}")
            raise
        finally:
            if conn:
                self._return_connection(conn)
    
    def update(self, table, set_data, where=None, where_params=None):
        """
        Update records in a table
        
        Args:
            table: Table name
            set_data: Dictionary of column:value pairs to update
            where: WHERE clause
            where_params: Parameters for WHERE clause
        
        Returns:
            Number of rows affected
        """
        if not set_data:
            raise ValueError("No data provided for update")
        
        set_clause = ', '.join([f"{col} = %s" for col in set_data.keys()])
        params = list(set_data.values())
        
        query = f"UPDATE {table} SET {set_clause}"
        
        if where:
            query += f" WHERE {where}"
            if where_params:
                params.extend(where_params if isinstance(where_params, tuple) else (where_params,))
        
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(query, tuple(params))
            rows_affected = cursor.rowcount
            conn.commit()
            return rows_affected
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Update error: {str(e)}")
            raise
        finally:
            if conn:
                self._return_connection(conn)
    
    def delete(self, table, where=None, where_params=None):
        """
        Delete records from a table
        
        Args:
            table: Table name
            where: WHERE clause
            where_params: Parameters for WHERE clause
        
        Returns:
            Number of rows deleted
        """
        query = f"DELETE FROM {table}"
        params = []
        
        if where:
            query += f" WHERE {where}"
            if where_params:
                params.extend(where_params if isinstance(where_params, tuple) else (where_params,))
        
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(query, tuple(params))
            rows_affected = cursor.rowcount
            conn.commit()
            return rows_affected
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Delete error: {str(e)}")
            raise
        finally:
            if conn:
                self._return_connection(conn)
