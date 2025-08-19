import logging
from flask import g, current_app
import uuid
from psycopg2 import sql
import sqlparse

import sqlparse
from psycopg2 import sql  # Required for proper SQL composition

class DBManager:
    def __init__(self, connection_pool):
        self.pool = connection_pool

    def execute(self, query, params=None):
        """Generic query executor"""
        print("\033[93mExecuting query:\033[0m", query)
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cursor:
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

    def select(self, table, columns="*", where=False, where_params=None):
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
        
        return self.execute(query, where_params)
    
    def insert(self, table, data):
        logging.basicConfig(level=logging.INFO)

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



    def update(self, table, data, where):
        # query = f"UPDATE {table} SET {', '.join([f'{k} = %s' for k in data.keys()])} WHERE {where}"
        query = sql.SQL("UPDATE {table} SET {fields} WHERE {where}").format(
            table=sql.Identifier(table),
            fields=sql.SQL(', ').join([sql.SQL(f"{k} = %s") for k in data.keys()]),
            where=sql.SQL(where)
        )
        return self.execute(query, tuple(data.values()))

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