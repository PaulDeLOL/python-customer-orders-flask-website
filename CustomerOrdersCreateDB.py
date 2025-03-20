"""
Name: Pablo Guardia
Date: 03/19/2025
Assignment: Module 10: Basic Flask Website
Due Date: 03/23/2025
About this project: This script is a unification of CustomerCreateDB.py and
OrderCreateDB.py from Module 9's assignment.
Assumptions: N/A
All work below was performed by Pablo Guardia
"""

import sqlite3

# Connect to CustOrders.db file, creating it if it doesn't already exist
conn = sqlite3.connect('CustOrders.db')
cur = conn.cursor()


# Drop tables only if they exist. Alternative to a try-except block
cur.execute('''DROP TABLE IF EXISTS Customers;''')
cur.execute('''DROP TABLE IF EXISTS Orders;''')


# Create tables if they don't exist yet
cur.execute('''
CREATE TABLE IF NOT EXISTS Customers (
             CustId INTEGER PRIMARY KEY AUTOINCREMENT,
             Name TEXT,
             Age INTEGER,
             PhNum TEXT,
             SecurityLevel INTEGER,
             LoginPassword TEXT
);
''')
conn.commit()
print("Customers table created!!")

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
print("Orders table created!!\n")


# Add a few records to the tables
customers = [
    ('Bethany Garner', 34, '5123-6789', 1, 'bethanyPass423'),
    ('Kohei Yamashita', 65, '5555-9101', 2, 'XZ_yaMaSHita89_ZX'),
    ('Andrés de la Cruz', 29, '1122-6412', 1, '971cocoSecure###'),
    ('Kang Si-woo', 20, '3873-9292', 3, 'hwuen817@&*!&nwk13')
]
cur.executemany('''
    INSERT INTO Customers (Name, Age, PhNum, SecurityLevel, LoginPassword)
    VALUES (?, ?, ?, ?, ?);
''', customers)
conn.commit()
print("Records added to Customers table")

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
print("Records added to Orders table\n")


# Print all records to the terminal
for row in cur.execute('''SELECT * FROM Customers;'''):
    print(row)
print()
for row in cur.execute('''SELECT * FROM Orders;'''):
    print(row)


conn.close()
print("\nConnection closed...")