"""
Name: Pablo Guardia
Date: 03/19/2025
Assignment: Module 10: Basic Flask Website
Due Date: 03/23/2025
About this project: This script is a basic website written in Flask that
contains 5 pages total. It can perform 3 functions:
- Add a new customer to a database by filling out a form.
- List the customers currently stored in the database.
- List the customer orders currently stored in the database.
The other 2 pages are for displaying the 3 options and the result of adding
a record to the Customers table, displaying errors if necessary.
Assumptions: N/A
All work below was performed by Pablo Guardia
"""

from flask import Flask, render_template, request
import sqlite3 as sql

app = Flask(__name__)

# Home page
@app.route('/')
def homepage():
    return render_template("homepage.html")

# Page containing a form to add a new customer to the database
@app.route('/newCustomer')
def new_customer():
    return render_template("newCustomer.html")

# Page displaying the results of adding a new customer (or failing to do so!)
@app.route('/newCustResult', methods=['POST', 'GET'])
def new_cust_result():
    if request.method == 'POST':
        # Stores error messages in a table
        err_table = []

        # Obtains the fields from the form filled out
        new_name = request.form.get('Name', "", str)
        new_age = request.form.get('Age', -1, int)
        new_number = request.form.get('Number', "", str)
        new_level = request.form.get('SecurLevel', -1, int)
        new_password = request.form.get('Password', "", str)

        # Validates input according to constraints defined in assignment instructions
        # Examples: No empty strings, age between 1 and 121, etc.
        if new_name is None or new_name.strip() == "":
            err_table.append("Can't create new customer; 'Name' field is blank or invalid")

        if new_age is None or new_age == -1:
            err_table.append("Can't create new customer; 'Age' field is blank or invalid")
        elif new_age < 1 or new_age > 121:
            err_table.append("Can't create new customer; 'Age' must be between 0 and 121")

        if new_number is None or new_number.strip() == "":
            err_table.append("Can't create new customer; 'Phone Number' field is blank or invalid")

        if new_level is None or new_level == -1:
            err_table.append("Can't create new customer; 'Security Level' field is blank or invalid")
        elif new_level < 1 or new_level > 3:
            err_table.append("Can't create new customer; 'Security Level' must be between 0 and 3")

        if new_password is None or new_password.strip() == "":
            err_table.append("Can't create new customer; 'Login Password' field is blank or invalid")

        # If err_table has no elements, meaning no errors occurred...
        if len(err_table) == 0:
            try:
                # Try inserting the new record into the database.
                conn = sql.connect("CustOrders.db")
                cur = conn.cursor()

                cur.execute('''
                    INSERT INTO Customers (Name, Age, PhNum, SecurityLevel, LoginPassword)
                    VALUES (?, ?, ?, ?, ?);
                ''', (new_name, new_age, new_number, new_level, new_password))

                conn.commit()
                msg = "Customer successfully created!"
            except Exception as excpt:
                # If something went wrong, display the exception
                conn.rollback()
                msg = f"Error creating a new customer: {excpt}"
                print(msg)
                return render_template("newCustResult.html", message = msg, errors_table = [])
            finally:
                conn.close()
                return render_template("newCustResult.html", message = msg, errors_table = [])
        # Otherwise, if err_table contains errors, display them all on the results page
        else:
            msg = "Error creating a new customer:"
            return render_template("newCustResult.html", message = msg, errors_table = err_table)
    # If the method was somehow not POST, address that and display an error
    else:
        msg = "Error creating a new customer: Request method is not POST"
        return render_template("newCustResult.html", message = msg, errors_table = [])

# Page listing the customers stored in the database
@app.route('/listCustomers')
def list_customers():
    # Displays the customers using sql.Row objects
    # This allows name indexing in the HTML page
    conn = sql.connect("CustOrders.db")
    conn.row_factory = sql.Row
    cur = conn.cursor()

    cur.execute("SELECT * FROM Customers;")
    cust_rows = cur.fetchall()
    conn.close()

    return render_template("listCustomers.html", records = cust_rows)

# Page listing the customer orders stored in the database
@app.route('/listOrders')
def list_orders():
    # Displays the orders using sql.Row objects
    # This allows name indexing in the HTML page
    conn = sql.connect("CustOrders.db")
    conn.row_factory = sql.Row
    cur = conn.cursor()

    cur.execute("SELECT * FROM Orders;")
    order_rows = cur.fetchall()
    conn.close()

    return render_template("listOrders.html", records = order_rows)

# Main driver function
if __name__ == "__main__":
    app.run(debug = True)