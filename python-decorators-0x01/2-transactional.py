import sqlite3
import functools

def with_db_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            if 'conn' not in kwargs and not (len(args) > 0 and isinstance(args[0], sqlite3.Connection)):
                kwargs['conn'] = conn
            return func(*args, **kwargs)
        finally:
            conn.close()
    return wrapper

def transactional(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Find the connection in either args or kwargs
        conn = kwargs.get('conn', None)
        if conn is None:
            for arg in args:
                if isinstance(arg, sqlite3.Connection):
                    conn = arg
                    break
        
        if conn is None:
            raise ValueError("No database connection provided")
        
        try:
            result = func(*args, **kwargs)
            conn.commit()  # Commit if no exceptions
            return result
        except Exception as e:
            conn.rollback()  # Rollback on error
            raise e  # Re-raise the exception
    return wrapper

@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))

# Update user's email with automatic transaction handling
update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')