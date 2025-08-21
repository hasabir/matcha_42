import logging
from flask import g, current_app
import uuid
from psycopg2 import sql
import psycopg2.extras
import sqlparse

import sqlparse
from psycopg2 import sql  # Required for proper SQL composition
logging.basicConfig(level=logging.DEBUG)



class DBManager:
    def __init__(self, connection_pool):
        self.pool = connection_pool

    def execute(self, query, params=None):
        """Generic query executor"""
        print("\033[93mExecuting query:\033[0m", query)
        conn = self.pool.getconn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                logging.debug("----------- >Executed query: %s with params: %s", query, params)
                cursor.execute(query, params or ())
                
                if hasattr(query, 'as_string') and "SELECT" in str(query).upper():
                    return cursor.fetchall()

                conn.commit()
                return cursor.rowcount  # Return affected rows for INSERT/UPDATE/DELETE
                
        except Exception as e:
            conn.rollback()
            print(f"\033[91mDatabase error:\033[0m {e}")
            raise
        finally:
            self.pool.putconn(conn)

    def select(self, table, columns="*", where=None, where_params=None):
        """Safe parameterized query builder"""
        query = sql.SQL("SELECT {fields} FROM {table}").format(
            fields=sql.SQL(', ').join(
                [sql.Identifier(col.strip()) for col in columns.split(',')]
            ) if columns != "*" else sql.SQL("*"),
            table=sql.Identifier(table)
        )
        
        if where:
            query = sql.SQL("{base_query} WHERE {where_clause}").format(
                base_query=query,
                where_clause=sql.SQL(where)
            )
        
        logging.info("Executing select query: %s with params: %s", query, where_params)
        
        return self.execute(query, where_params)
    
    def insert(self, table, data):

        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")
        if not data:
            raise ValueError("Data cannot be empty")

        columns = list(data.keys())
        values = list(data.values())

        query = sql.SQL("INSERT INTO {table} ({fields}) VALUES ({placeholders})").format(
            table=sql.Identifier(table),
            fields=sql.SQL(", ").join(map(sql.Identifier, columns)),
            placeholders=sql.SQL(", ").join(sql.Placeholder() * len(values))
        )

        logging.info("Inserting into %s: %s", table, data)
        return self.execute(query, values)



    def update(self, table, data, where=None, where_params=None):
        
        
        """
        Safe UPDATE function with parameterized WHERE clause
        
        :param table: Table name
        :param data: Dict of {column: value} to update
        :param where: SQL string for WHERE clause (use placeholders %s)
        :param where_params: Parameters for WHERE clause placeholders
        """
        if not data:
            raise ValueError("No data provided for update")
        
        # Build SET clause
        set_clause = sql.SQL(", ").join([
            sql.SQL("{} = %s").format(sql.Identifier(key))
            for key in data.keys()
        ])
        
        # Build WHERE clause
        if where:
            where_clause = sql.SQL("WHERE {}").format(sql.SQL(where))
        else:
            where_clause = sql.SQL("")  # No WHERE clause (use with caution!)
        
        # Build complete query
        query = sql.SQL("UPDATE {} SET {} {}").format(
            sql.Identifier(table),
            set_clause,
            where_clause
        )
        
        # Combine parameters
        params = list(data.values())
        if where_params:
            if isinstance(where_params, (list, tuple)):
                params.extend(where_params)
            else:
                params.append(where_params)
        
        return self.execute(query, params)

    def delete(self, table, where):
        # query = f"DELETE FROM {table} WHERE {where}"
        query = sql.SQL("DELETE FROM {table} WHERE {where}").format(
            table=sql.Identifier(table),
            where=sql.SQL(where)
        )
        return self.execute(query)
    

    def get_db_connection():
        """Get a DB connection for the current request (reuses if already opened)."""
        if not hasattr(g, '_database_connection'):
            pool = current_app.config["CONNECTION_POOL"]
            g._database_connection = pool.getconn()
        return g._database_connection