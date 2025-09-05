import os
import mysql.connector
from contextlib import contextmanager
from logging_setup import setup_logger
import ssl

logger = setup_logger('db_helper')

def get_db_connection():
    """Create and return a database connection using environment variables."""
    try:
        ssl_config = {}
        if os.getenv('DB_SSL_CA'):
            ssl_config = {
                'ssl_ca': os.getenv('DB_SSL_CA'),
                'ssl_verify_cert': True
            }
            
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'expense_manager'),
            port=int(os.getenv('DB_PORT', '3306')),
            **ssl_config
        )
        return connection
    except Exception as e:
        logger.error(f"Error connecting to database: {str(e)}")
        raise

@contextmanager
def get_db_cursor(commit=False):
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        yield cursor
        if commit:
            connection.commit()
    except Exception as e:
        if connection and connection.is_connected():
            connection.rollback()
        logger.error(f"Database error: {str(e)}")
        raise
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def fetch_expenses_for_date(expense_date):
    logger.info(f"fetch_expenses_for_date called with {expense_date}")
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM expenses WHERE expense_date = %s", (expense_date,))
        expenses = cursor.fetchall()
        return expenses


def delete_expenses_for_date(expense_date):
    logger.info(f"delete_expenses_for_date called with {expense_date}")
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("DELETE FROM expenses WHERE expense_date = %s", (expense_date,))


def insert_expense(expense_date, amount, category, notes):
    logger.info(f"insert_expense called with date: {expense_date}, amount: {amount}, category: {category}, notes: {notes}")
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            "INSERT INTO expenses (expense_date, amount, category, notes) VALUES (%s, %s, %s, %s)",
            (expense_date, amount, category, notes)
        )


def fetch_expense_summary(start_date, end_date):
    logger.info(f"fetch_expense_summary called with start: {start_date} end: {end_date}")
    with get_db_cursor() as cursor:
        cursor.execute(
            '''SELECT category, SUM(amount) as total 
               FROM expenses WHERE expense_date
               BETWEEN %s and %s  
               GROUP BY category;''',
            (start_date, end_date)
        )
        data = cursor.fetchall()
        return data

def fetch_monthly_expense_summary():
    logger.info(f"fetch_expense_summary_by_months")
    with get_db_cursor() as cursor:
        cursor.execute(
            '''SELECT month(expense_date) as expense_month, 
               monthname(expense_date) as month_name,
               sum(amount) as total FROM expenses
               GROUP BY expense_month, month_name;
            '''
        )
        data = cursor.fetchall()
        return data



if __name__ == "__main__":
    expenses = fetch_expenses_for_date("2024-09-30")
    print(expenses)
    # delete_expenses_for_date("2024-08-25")
    summary = fetch_expense_summary("2024-08-01", "2024-08-05")
    for record in summary:
        print(record)
