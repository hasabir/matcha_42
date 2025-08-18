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

    # Specific methods
    def select(self, table, columns="*", where=None):
        """Example: select('users', where='id = %s', (1,))"""
        query = f"SELECT {columns} FROM {table}"
        if where:
            query += f" WHERE {where}"
        return self.execute(query)
    
    def insert(self, table, data):
        query = f"INSERT INTO {table} ({', '.join(data.keys())}) VALUES ({', '.join(['%s'] * len(data))})"
        return self.execute(query, tuple(data.values()))

    # Add insert/update/delete methods...