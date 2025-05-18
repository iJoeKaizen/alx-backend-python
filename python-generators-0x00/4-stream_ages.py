from seed import connect_to_prodev

def stream_user_ages():
    """Generator that yields user ages one by one from the database."""
    connection = connect_to_prodev()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT age FROM user_data")
        for (age,) in cursor:
            yield int(age)
    finally:
        cursor.close()
        connection.close()

def calculate_average_age():
    """Calculates and prints the average age using the generator."""
    total_age = 0
    count = 0

    for age in stream_user_ages():
        total_age += age
        count += 1

    if count > 0:
        print(f"Average age of users: {total_age // count}")
    else:
        print("No users found.")

# Entry point
if __name__ == "__main__":
    calculate_average_age()
