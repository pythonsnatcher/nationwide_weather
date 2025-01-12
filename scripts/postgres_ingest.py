import sqlite3
import psycopg2
import requests
import io
import tempfile
from datetime import datetime
from psycopg2.extras import execute_values
import os

# Set the connection parameters for PostgreSQL
host = "dpg-ctsr3jpu0jms73bcvhu0-a.oregon-postgres.render.com"
port = 5432
user = "admin"
password = os.getenv('POSTGRES_PASSWORD')  # Get password from environment variable
dbname = "nationwide_weather"

# Set the URL for the SQLite database
# url = "https://raw.githubusercontent.com/pythonsnatcher/nationwide_weather/5cce1ae87441d5fefdddb0e4d99b05ddde8d457a/data/nationwide_weather.db"
url = "https://raw.githubusercontent.com/pythonsnatcher/nationwide_weather/main/data/nationwide_weather.db"
# Download the SQLite database
response = requests.get(url)
sqlite_db = io.BytesIO(response.content)

# Create a temporary file to hold the SQLite data
with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
    tmp_file.write(sqlite_db.read())
    tmp_file_path = tmp_file.name

# Connect to SQLite database using the temporary file
sqlite_conn = sqlite3.connect(tmp_file_path)
sqlite_cursor = sqlite_conn.cursor()

# Connect to PostgreSQL database using explicit connection parameters
pg_conn = psycopg2.connect(
    host=host,
    port=port,
    user=user,
    password=password,
    dbname=dbname,
    sslmode='require'
)
pg_cursor = pg_conn.cursor()

# Fetch the table names from SQLite
sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = sqlite_cursor.fetchall()

# Function to drop a table in PostgreSQL if it exists
def drop_table_if_exists(table_name):
    drop_query = f"DROP TABLE IF EXISTS {table_name} CASCADE;"
    try:
        pg_cursor.execute(drop_query)
        print(f"Table {table_name} dropped successfully.")
    except Exception as e:
        print(f"Error dropping table {table_name}: {e}")

# Function to fetch the schema of a table and create it in PostgreSQL
def create_table_in_postgres(table_name):
    sqlite_cursor.execute(f"PRAGMA table_info({table_name});")
    columns = sqlite_cursor.fetchall()

    if not columns:
        print(f"No columns found for table: {table_name}")
        return

    pg_columns = []
    for column in columns:
        column_name = column[1]
        column_type = column[2]

        # Map SQLite types to PostgreSQL types
        if column_type == "INTEGER":
            column_type = "BIGINT"
        elif column_type == "REAL":
            column_type = "FLOAT"
        elif column_type == "TEXT":
            try:
                # Check if TEXT can represent a TIMESTAMP, TIME, or TIME (HH:MM) format
                sqlite_cursor.execute(f"SELECT {column_name} FROM {table_name} LIMIT 1;")
                value = sqlite_cursor.fetchone()[0]
                if value:
                    try:
                        # Try TIMESTAMP format
                        datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                        column_type = "TIMESTAMP"
                    except ValueError:
                        try:
                            # Try TIME format
                            datetime.strptime(value, "%H:%M:%S")
                            column_type = "TIME"
                        except ValueError:
                            try:
                                # Try TIME (HH:MM) format
                                datetime.strptime(value, "%H:%M")
                                column_type = "TIME"
                            except ValueError:
                                column_type = "TEXT"
                else:
                    column_type = "TEXT"
            except Exception:
                column_type = "TEXT"

        pg_columns.append(f"{column_name} {column_type}")

    create_table_query = f"CREATE TABLE {table_name} ({', '.join(pg_columns)});"
    try:
        pg_cursor.execute(create_table_query)
        print(f"Table {table_name} created successfully.")
    except Exception as e:
        print(f"Error creating table {table_name}: {e}")

# Function to insert data from SQLite to PostgreSQL
def insert_data_from_sqlite_to_postgres(table_name):
    sqlite_cursor.execute(f"SELECT * FROM {table_name};")
    column_names = [desc[0] for desc in sqlite_cursor.description]
    rows = sqlite_cursor.fetchall()

    converted_rows = [[None if isinstance(value, str) and value == 'N/A' else value for value in row] for row in rows]

    insert_query = f"INSERT INTO {table_name} ({', '.join(column_names)}) VALUES %s;"
    try:
        execute_values(pg_cursor, insert_query, converted_rows)
        print(f"Data inserted into table {table_name} successfully.")
        print(f"Number of rows appended to {table_name}: {len(converted_rows)}")
    except Exception as e:
        print(f"Error inserting data into table {table_name}: {e}")

# Main processing
for table in tables:
    table_name = table[0]
    if table_name.startswith("sqlite_"):
        print(f"Skipping system table: {table_name}")
        continue

    drop_table_if_exists(table_name)
    create_table_in_postgres(table_name)
    insert_data_from_sqlite_to_postgres(table_name)

# Commit and close connections
pg_conn.commit()
sqlite_cursor.close()
pg_cursor.close()
sqlite_conn.close()
pg_conn.close()

print("Data and schema successfully transferred from SQLite to PostgreSQL.")
