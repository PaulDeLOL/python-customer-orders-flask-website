"""
Name: Pablo Guardia
Date: 03/12/2025
Assignment: Module 9: SQLite3 Database
Due Date: 03/16/2025
About this project: This script creates a SQLite3 table in a database called
CustOrders.db, with the table being a set of customers with name, age,
phone number, etc.
Assumptions: N/A
All work below was performed by Pablo Guardia
"""

import sqlite3

# Connect to CustOrders.db file, creating it if it doesn't already exist
conn = sqlite3.connect('CustOrders.db')
cur = conn.cursor()

# Drops the Customers table only if it exists. Alternative to a try-except block
# Creates the Customers table if it doesn't exist yet
cur.execute('''DROP TABLE IF EXISTS Customers;''')
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

# Adds a few records to the Customers table by adding a list of tuples
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

# Prints the records to the screen, then the connection is closed
for row in cur.execute('''SELECT * FROM Customers;'''):
    print(row)

conn.close()
print("Connection closed...\n")