from flask import g, current_app
class DBManager:
    def __init__(self, connection_pool):
        self.pool = connection_pool

    def execute(self, query, params=None):
        """Generic query executor"""
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params or ())
                if query.strip().upper().startswith(("SELECT", "WITH")):
                    return cursor.fetchall()
                conn.commit()
        finally:
            self.pool.putconn(conn)

    def select(self, table, columns="*", where=None):
        """Example: select('users', where='id = %s', (1,))"""
        query = f"SELECT {columns} FROM {table}"
        if where:
            query += f" WHERE {where}"
        return self.execute(query)
    
    def insert(self, table, data):
        query = f"INSERT INTO {table} ({', '.join(data.keys())}) VALUES ({', '.join(['%s'] * len(data))})"
        return self.execute(query, tuple(data.values()))


    def update(self, table, data, where):
        query = f"UPDATE {table} SET {', '.join([f'{k} = %s' for k in data.keys()])} WHERE {where}"
        return self.execute(query, tuple(data.values()))

    def delete(self, table, where):
        query = f"DELETE FROM {table} WHERE {where}"
        return self.execute(query)
    

    def get_db_connection():
        """Get a DB connection for the current request (reuses if already opened)."""
        if not hasattr(g, '_database_connection'):
            pool = current_app.config["CONNECTION_POOL"]
            g._database_connection = pool.getconn()
        return g._database_connection