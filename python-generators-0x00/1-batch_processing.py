from seed import connect_to_prodev
import sys
import uuid

def stream_users_in_batches(batch_size):
    """Generator that yields batches of users from database"""
    connection = None
    cursor = None
    offset = 0
    
    try:
        connection = connect_to_prodev()
        if not connection:
            raise Exception("Failed to connect to database")
        
        cursor = connection.cursor(dictionary=True, buffered=True)
        
        while True:  # Batch fetching loop
            cursor.execute("SELECT * FROM user_data LIMIT %s OFFSET %s", (batch_size, offset))
            
            rows = cursor.fetchall()
            if not rows:
                break
            
            # Convert UUID bytes to string if needed
            for row in rows:
                if isinstance(row['user_id'], bytes):
                    row['user_id'] = str(uuid.UUID(bytes=row['user_id']))
            
            yield rows
            offset += batch_size
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def batch_processing(batch_size, output_limit=None):
    """Process batches and print users over 25"""
    count = 0
    try:
        for batch in stream_users_in_batches(batch_size):  # Batch processing loop
            for user in batch:  # User processing loop
                if user['age'] > 25:
                    print(user)
                    count += 1
                    if output_limit and count >= output_limit:
                        return
    except BrokenPipeError:
        # Handle pipe closure gracefully
        sys.stderr.close()
        sys.exit(0)
    except (BrokenPipeError, OSError) as e:
        if isinstance(e, OSError) and e.errno != 22:
            print(f"Error: {e}", file=sys.stderr)
    sys.stderr.close()
    sys.exit(0)


if __name__ == "__main__":
    # Process in batches of 50, output first 5 matches
    batch_processing(50, output_limit=5)
