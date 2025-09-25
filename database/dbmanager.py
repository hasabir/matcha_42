import logging
from flask import g, current_app
import uuid
from psycopg2 import sql
import psycopg2.extras

from psycopg2 import sql  # Required for proper SQL composition
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)


class DBManager:
    def __init__(self, connection_pool):
        self.pool = connection_pool

    def execute(self, query, params=None):
        """Generic query executor"""
        print("\033[93mExecuting query:\033[0m", query)
        conn = self.pool.getconn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute(query, params or ())
                #! logger.info(f"❌❌❌Executing search query: {query} with params: {params}")
                if hasattr(query, 'as_string') and "SELECT" in str(query).upper():
                    #! logger.info(f"❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌ it should be a select query")
                    return cursor.fetchall()

                conn.commit()
                return cursor.rowcount  # Return affected rows for INSERT/UPDATE/DELETE
                
        except Exception as e:
            conn.rollback()
            print(f"\033[91mDatabase error:\033[0m {e}")
            raise
        finally:
            self.pool.putconn(conn)


    def select(self, table, columns="*", where=None, where_params=None, in_params=None,
               join=None, join_on=None, join_type="INNER"):
        """Safe parameterized SELECT query builder"""
        # Build SELECT fields
        if columns == "*":
            fields = sql.SQL("*")
        else:
            fields = sql.SQL(', ').join([sql.Identifier(col.strip()) for col in columns.split(',')])

        query = sql.SQL("SELECT {fields} FROM {table}").format(
            fields=fields,
            table=sql.Identifier(table)
        )

        # if join and join_on:

        params = []
        
        # Add WHERE clause if provided
        
        if where:
            query = sql.SQL("{base_query} WHERE {where_clause}").format(
                base_query=query,
                where_clause=sql.SQL(where)
            )
            if where_params:
                if isinstance(where_params, (list, tuple)):
                    params.extend(where_params)
                else:
                    params.append(where_params)

        # Add IN clause if provided
        if in_params:
            placeholders = sql.SQL(', ').join(sql.Placeholder() * len(in_params))
            query = sql.SQL("{base_query}  IN ({placeholders})").format(
                base_query=query,
                in_field=sql.Identifier(where) if isinstance(where, str) else sql.Identifier('id'),
                placeholders=placeholders
            )
            params.extend(in_params)

        # logging.info("❌❌❌Executing select query: %s with params: %s", str(query), params)
        return self.execute(query, params if params else None)


    def insert(self, table, data, on_conflict=None, conflict_target=None, update_set=None):
        """
        Insert data into table with optional UPSERT support
        
        Args:
            table: Table name
            data: Dictionary of column: value pairs
            on_conflict: Conflict action ('NOTHING', 'UPDATE')
            conflict_target: List of columns for conflict detection
            update_set: Dictionary of columns to update on conflict
        """
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
        
        if on_conflict:
            if not conflict_target:
                raise ValueError("conflict_target is required for ON CONFLICT")
            
            if on_conflict.upper() == 'UPDATE' and not update_set:
                raise ValueError("update_set is required for ON CONFLICT UPDATE")
            
            conflict_clause = sql.SQL("({})").format(
                sql.SQL(", ").join(map(sql.Identifier, conflict_target))
            )
            
            if on_conflict.upper() == 'NOTHING':
                query = sql.SQL("{base_query} ON CONFLICT {conflict_target} DO NOTHING").format(
                    base_query=query,
                    conflict_target=conflict_clause
                )
            elif on_conflict.upper() == 'UPDATE':
                # Use EXCLUDED to reference the values that would have been inserted
                set_clauses = []
                for col in update_set.keys():
                    set_clauses.append(sql.SQL("{column} = EXCLUDED.{column}").format(
                        column=sql.Identifier(col)
                    ))
                
                query = sql.SQL("{base_query} ON CONFLICT {conflict_target} DO UPDATE SET {set_clause}").format(
                    base_query=query,
                    conflict_target=conflict_clause,
                    set_clause=sql.SQL(", ").join(set_clauses)
                )
                
                # Don't extend values as we're using EXCLUDED
            else:
                raise ValueError("on_conflict must be 'NOTHING' or 'UPDATE'")

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

    def delete(self, table, where=None, where_params=None):
        """Safe parameterized DELETE query builder"""
        # Start with the basic DELETE statement
        query = sql.SQL("DELETE FROM {table}").format(
            table=sql.Identifier(table)
        )
        
        # Add WHERE clause if provided
        if where:
            query = sql.SQL("{base_query} WHERE {where_clause}").format(
                base_query=query,
                where_clause=sql.SQL(where)
            )
        
        return self.execute(query, where_params)
            
        
        
        
        # query = sql.SQL("DELETE {feild} FROM {table} WHERE {where}").format(
        #     table=sql.Identifier(table),
        #     where=sql.SQL(where)
        # )
        # return self.execute(query)
    

    def get_db_connection():
        """Get a DB connection for the current request (reuses if already opened)."""
        if not hasattr(g, '_database_connection'):
            pool = current_app.config["CONNECTION_POOL"]
            g._database_connection = pool.getconn()
        return g._database_connection