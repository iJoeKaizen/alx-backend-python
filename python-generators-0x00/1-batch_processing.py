import mysql.connector
from mysql.connector import Error
import uuid

def stream_users_in_batches(batch_size=100):
    """Generator that yields batches of users from database"""
    connection = None
    cursor = None
    try:
        # Establish database connection
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='ALX_prodev'
        )
        
        # Use buffered cursor to prevent unread results
        cursor = connection.cursor(dictionary=True, buffered=True)
        cursor.execute("SELECT * FROM user_data")
        
        # First loop: batch fetching
        while True:
            batch = []
            # Second loop: collect batch
            for _ in range(batch_size):
                row = cursor.fetchone()
                if row is None:
                    break
                if isinstance(row['user_id'], bytes):
                    row['user_id'] = str(uuid.UUID(bytes=row['user_id']))
                batch.append(row)
            
            if not batch:
                break
                
            yield batch
            
    except Error as e:
        print(f"Database error: {e}", file=sys.stderr)
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def batch_processing(batch_size=100):
    """Generator that processes batches to filter users over 25"""
    # Third loop: process batches
    for batch in stream_users_in_batches(batch_size):
        filtered_batch = [user for user in batch if user['age'] > 25]
        for user in filtered_batch:  # Yield users one by one from filtered batch
            yield user