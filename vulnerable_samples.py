#!/usr/bin/env python3

# Sample 1: Remote Code Execution vulnerability
def execute_command():
    user_input = input("Enter a mathematical expression: ")
    result = eval(user_input)  # Vulnerable: RCE risk
    print(f"Result: {result}")

# Sample 2: A safer alternative
def execute_command_safely():
    import subprocess
    user_input = input("Enter command: ")
    subprocess.run(user_input.split())  # Safer but still has risks

# Let's create a simple web application with SQL injection
import sqlite3

def vulnerable_db_query():
    user_id = input("Enter user ID: ")
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # Vulnerable to SQL injection
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    
# Main function to demonstrate vulnerabilities
if __name__ == "__main__":
    print("This file contains deliberate security vulnerabilities for testing.")
    # Don't actually run the vulnerable code in production! 