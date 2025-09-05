import os
from dotenv import load_dotenv
from backend.db_helper import get_db_connection

# Load environment variables from .env file
load_dotenv()

def test_connection():
    try:
        print("Attempting to connect to the database...")
        connection = get_db_connection()
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"Successfully connected to MySQL Server version {db_info}")
            
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            record = cursor.fetchone()
            print(f"Connected to database: {record[0]}")
            
            # Test query
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            print("\nTables in the database:")
            for table in tables:
                print(f"- {table[0]}")
                
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("\nMySQL connection is closed")

if __name__ == "__main__":
    test_connection()
