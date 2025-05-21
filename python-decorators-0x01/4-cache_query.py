import time
import sqlite3 
import functools
from functools import lru_cache  # Alternative approach

# Global query cache dictionary
query_cache = {}

def cache_query(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Extract the query from args or kwargs
        query = kwargs.get('query', None)
        if query is None and len(args) > 1:  # First arg is 'conn'
            query = args[1] if isinstance(args[1], str) else None
        
        if query is None:
            return func(*args, **kwargs)  # No caching if no query
        
        # Check cache first
        if query in query_cache:
            print(f"Returning cached result for query: {query[:50]}...")
            return query_cache[query]
        
        # Execute and cache if not in cache
        result = func(*args, **kwargs)
        query_cache[query] = result
        return result
    return wrapper

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

# First call will cache the result
users = fetch_users_with_cache(query="SELECT * FROM users")

# Second call will use the cached result
users_again = fetch_users_with_cache(query="SELECT * FROM users")