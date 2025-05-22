import sqlite3

class ExecuteQuery:
    def __init__(self, db_name, query, params=None):
        self.db_name = db_name
        self.query = query
        self.params = params or ()
        self.conn = None
        self.cursor = None
        self.results = None
    
    def __enter__(self):
        """Open connection, execute query, and return results"""
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute(self.query, self.params)
        self.results = self.cursor.fetchall()
        return self.results
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up resources"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        # Don't suppress any exceptions
        return False

# Usage example
query = "SELECT * FROM users WHERE age > ?"
params = (25,)

with ExecuteQuery('users.db', query, params) as results:
    print("Users over 25:")
    for row in results:
        print(row)