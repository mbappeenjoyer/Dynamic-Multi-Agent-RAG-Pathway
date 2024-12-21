import psycopg2

# Database connection details
db_config = {
    "dbname": "chatdb",
    "user": "postgres",
    "password": "Rish@123",
    "host": "localhost",
    "port": 5432,
}

try:
    # Establish connection
    connection = psycopg2.connect(**db_config)
    print("Connection to PostgreSQL database established successfully!")

    # Create a cursor to execute queries
    cursor = connection.cursor()

    # Example query
    query = "SELECT version();"
    cursor.execute(query)

    # Fetch and print the result
    result = cursor.fetchone()
    print(f"PostgreSQL version: {result[0]}")

except Exception as error:
    print(f"Error connecting to PostgreSQL database: {error}")
finally:
    # Close the cursor and connection
    if 'cursor' in locals() and cursor:
        cursor.close()
    if 'connection' in locals() and connection:
        connection.close()
        print("Connection closed.")
