        from seed import connect_to_prodev
# import mysql.connector 
from mysql.connector import Error

def stream_users():
    """Generator function that streams users from the database one by one"""
    connection = None
    cursor = None
    try:
        connection = connect_to_prodev()
        if not connection:
            raise Exception("Failed to connect to the database")
        
        cursor = connection.cursor(dictionary=True, buffered=True)
        
        # Execute query and stream results
        cursor.execute("SELECT * FROM user_data")
        
        # Single loop using yield to stream rows
        while True:
            row = cursor.fetchone()
            if row is None:
                # Ensure all rows are processed
                while cursor.fetchoneone() is not None:
                    pass
                break
            yield row
            
    except Error as e:
        print(f"Database error: {e}")
    finally:
        if cursor:
             cursor.close()
        if connection and connection.is_connected():
            connection.close()


            
