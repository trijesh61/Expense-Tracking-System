"""Initialize the SQLite database for the Expense Tracking System."""
from backend.db_helper import init_db, insert_expense, fetch_expenses_for_date
from datetime import date, timedelta

def main():
    print("Initializing database...")
    init_db()
    
    # Add some test data
    today = date.today()
    test_expenses = [
        (today, 15.50, "Food", "Lunch"),
        (today, 45.00, "Transport", "Monthly pass"),
        (today - timedelta(days=1), 25.30, "Food", "Groceries"),
        (today - timedelta(days=2), 12.00, "Entertainment", "Movie"),
    ]
    
    print("Adding test expenses...")
    for expense in test_expenses:
        insert_expense(*expense)
    
    # Verify the data was added
    print("\nToday's expenses:")
    expenses = fetch_expenses_for_date(today.isoformat())
    for expense in expenses:
        print(f"- {expense['category']}: ${expense['amount']} - {expense['notes']}")
    
    print("\nDatabase initialization complete!")

if __name__ == "__main__":
    main()
