#!/usr/bin/python3
from seed import connect_to_prodev
import sys
import uuid

def paginate_users(page_size, offset):
    connection = connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_data LIMIT %s OFFSET %s", (page_size, offset))
    rows = cursor.fetchall()

    # Optional: Convert UUID bytes to string (if needed)
    for row in rows:
        if isinstance(row['user_id'], bytes):
            row['user_id'] = str(uuid.UUID(bytes=row['user_id']))
            row['age'] = int(row['age'])


    connection.close()
    return rows


def lazy_pagination(page_size):
    """Generator that lazily fetches users in paginated batches"""
    offset = 0
    while True:  # Only one loop
        page = paginate_users(page_size, offset)
        if not page:
            break
        yield page
        offset += page_size
