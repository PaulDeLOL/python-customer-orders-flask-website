"""
Name: Pablo Guardia
Date: 03/12/2025
Assignment: Module 9: SQLite3 Database
Due Date: 03/16/2025
About this project: This script creates a SQLite3 table in a database called
CustOrders.db, with the table being a set of orders made by customers, which
contain the items' SKU numbers, the quantity available, the price, etc. Every
item contains a foreign key that references a customer in the Customers table.
Assumptions: N/A
All work below was performed by Pablo Guardia
"""

import sqlite3

# Connect to CustOrders.db file, creating it if it doesn't already exist
conn = sqlite3.connect('CustOrders.db')
cur = conn.cursor()

# Drops the Orders table only if it exists. Alternative to a try-except block
# Creates the Orders table if it doesn't exist yet
cur.execute('''DROP TABLE IF EXISTS Orders;''')
cur.execute('''
CREATE TABLE IF NOT EXISTS Orders (
             OrderId INTEGER PRIMARY KEY AUTOINCREMENT,
             CustId INTEGER,
             ItemSkewNum TEXT,
             Quantity INTEGER,
             Price REAL,
             CreditCardNum TEXT,
             FOREIGN KEY (CustId) REFERENCES Customers(CustId)
);
''')
conn.commit()
print("Orders table created!!")

# Adds a few records to the Orders table by adding a list of tuples
orders = [
    (4, '111-22-1111', 10, 9.99, '4589 2244 8998 7111'),
    (2, '3498-77-54564', 20, 14.99, '6742 3123 3332 2276'),
    (2, '111-22-3498', 57, 249.99, '6876 3453 4589 1444'),
    (3, '77-1111-54564', 34, 69.99, '8888 8959 6801 4923')
]
cur.executemany('''
    INSERT INTO Orders (CustId, ItemSkewNum, Quantity, Price, CreditCardNum)
    VALUES (?, ?, ?, ?, ?);
''', orders)
conn.commit()
print("Records added to Orders table")

# Prints the records to the screen, then the connection is closed
for row in cur.execute('''SELECT * FROM Orders;'''):
    print(row)

conn.close()
print("Connection closed...\n")