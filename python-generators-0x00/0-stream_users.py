seed = __import__('seed')

connection = seed.connect_db()
if connection:
    seed.create_database(connection)
    connection.close()
    print(f"connection successful")


def stream_users():
    """Generator function that streams users from the database one by one"""
    try:
   
        connection = seed.connect_to_prodev()
        if connection is None:
            raise Exception("Failed to connect to the database")
        
        cursor = connection.cursor(dictionary=True)
        
        # Execute query and stream results
        cursor.execute("SELECT * FROM user_data")
        
        # Single loop using yield to stream rows
        while True:
            row = cursor.fetchone()
            if row is None:
                break
            yield row
            
    except e as e:
        print(f"Database error: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()


            
