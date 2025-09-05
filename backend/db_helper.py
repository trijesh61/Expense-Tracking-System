import os
import sqlite3
from contextlib import contextmanager
from logging_setup import setup_logger
import pandas as pd
from pathlib import Path

logger = setup_logger('db_helper')

# Get the path to the database file
DB_PATH = Path(__file__).parent / 'expense_tracker.db'

def get_db_connection():
    """Create and return a SQLite database connection."""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        # Enable foreign key constraints
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except Exception as e:
        logger.error(f"Error connecting to SQLite database: {str(e)}")
        raise

def init_db():
    """Initialize the database with required tables."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Create expenses table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            expense_date DATE NOT NULL,
            amount DECIMAL(10, 2) NOT NULL,
            category VARCHAR(50) NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        conn.commit()
        logger.info("Database tables created successfully")

@contextmanager
def get_db_cursor(commit=False):
    """Context manager for database cursor."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        yield cursor
        if commit:
            conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()


def fetch_expenses_for_date(expense_date):
    logger.info(f"fetch_expenses_for_date called with {expense_date}")
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM expenses WHERE date(expense_date) = date(?)", (expense_date,))
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def delete_expenses_for_date(expense_date):
    logger.info(f"delete_expenses_for_date called with {expense_date}")
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("DELETE FROM expenses WHERE date(expense_date) = date(?)", (expense_date,))
        return cursor.rowcount


def insert_expense(expense_date, amount, category, notes):
    logger.info(f"insert_expense called with date: {expense_date}, amount: {amount}, category: {category}, notes: {notes}")
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            """
            INSERT INTO expenses (expense_date, amount, category, notes) 
            VALUES (date(?), ?, ?, ?)
            """,
            (expense_date, amount, category, notes)
        )
        return cursor.lastrowid


def fetch_expense_summary(start_date, end_date):
    logger.info(f"fetch_expense_summary called with start: {start_date} end: {end_date}")
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT 
                category,
                SUM(amount) as total_amount,
                COUNT(*) as transaction_count
            FROM expenses
            WHERE date(expense_date) BETWEEN date(?) AND date(?)
            GROUP BY category
            ORDER BY total_amount DESC
        """, (start_date, end_date))
        
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

def fetch_monthly_expense_summary():
    logger.info("fetch_monthly_expense_summary")
    with get_db_cursor() as cursor:
        cursor.execute(
            '''
            SELECT 
                strftime('%Y-%m', expense_date) as month,
                SUM(amount) as total,
                COUNT(*) as transaction_count
            FROM expenses
            GROUP BY strftime('%Y-%m', expense_date)
            ORDER BY month DESC
            '''
        )
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

# Initialize the database when this module is imported
init_db()

if __name__ == "__main__":
    expenses = fetch_expenses_for_date("2024-09-30")
    print(expenses)
    # delete_expenses_for_date("2024-08-25")
    summary = fetch_expense_summary("2024-08-01", "2024-08-05")
    for record in summary:
        print(record)
