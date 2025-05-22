import sqlite3

class DatabaseConnection:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None
    
    def __enter__(self):
        """Open the database connection when entering the context"""
        self.conn = sqlite3.connect(self.db_name)
        return self.conn
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close the connection when exiting the context"""
        if self.conn:
            self.conn.close()
        # Return False to propagate any exceptions, True would suppress them
        return False

# Using the context manager to query users
with DatabaseConnection('users.db') as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    results = cursor.fetchall()
    
    # Print the results
    print("Users in the database:")
    for row in results:
        print(row)