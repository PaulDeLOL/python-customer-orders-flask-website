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

from flask import (Flask, render_template, request,
                   redirect, url_for, session, flash)
import sqlite3 as sql
import os

app = Flask(__name__)

@app.route('/')
def index():
    if session.get('logged_in'):
        return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))

@app.route('/login')
def login():
    if not session.get('logged_in'):
        return render_template("login.html")
    else:
        flash("You are already logged in. Click \"Log out\" to log out.")
        return redirect(url_for('home'))

@app.route('/loginCheck', methods = ['POST', 'GET'])
def login_check():
    if not session.get('logged_in'):
        if request.method == "POST":
            conn = sql.connect("CustOrders.db")
            conn.row_factory = sql.Row
            cur = conn.cursor()

            username = request.form.get('Username', "", str)
            password = request.form.get('Password', "", str)

            cur.execute('''
                SELECT * FROM Customers
                WHERE Name == ? AND LoginPassword == ?
            ''', (username, password))
            check = cur.fetchone()

            if check is not None:
                session['logged_in'] = True

                session['id'] = check['CustId']
                session['username'] = check['Name']
                session['age'] = check['Age']
                session['number'] = check['PhNum']
                session['security_level'] = check['SecurityLevel']
                session['password'] = check['LoginPassword']

                flash("Successfully logged in!!!")
                conn.close()
                return redirect(url_for('home'))
            else:
                session['logged_in'] = False
                flash("Login failed. Invalid username or password.")
                conn.close()
                return redirect(url_for('login'))
        else:
            flash("Login error. Request method is not POST.")
            flash("User might have attempted to access /loginCheck illegally.")
            return redirect(url_for('login'))
    else:
        flash("You are already logged in. Click \"Log out\" to log out.")
        return redirect(url_for('home'))

# Home page
@app.route('/home')
def home():
    if session.get('logged_in'):
        return render_template("homepage.html")
    else:
        flash("You must be logged in to access this page.")
        return redirect(url_for('login'))

# Page containing a form to add a new customer to the database
@app.route('/newCustomer')
def new_customer():
    if session.get('logged_in') and session.get('security_level') >= 2:
        return render_template("newCustomer.html")
    elif session.get('security_level') < 2:
        redirect(url_for('invalid'))
    elif not session.get('logged_in'):
        flash("You must be logged in to access this page.")
        return redirect(url_for('login'))
    else:
        redirect(url_for('invalid'))

# Page displaying the results of adding a new customer (or failing to do so!)
@app.route('/newCustResult', methods = ['POST', 'GET'])
def new_cust_result():
    if session.get('logged_in'):
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
                    return render_template("formResults.html", message = msg, errors_table = [])
                finally:
                    conn.close()
                    return render_template("formResults.html", message = msg, errors_table = [])
            # Otherwise, if err_table contains errors, display them all on the results page
            else:
                msg = "Error creating a new customer:"
                return render_template("formResults.html", message = msg, errors_table = err_table)
        # If the method was somehow not POST, address that and display an error
        else:
            msg = "Error creating a new customer: Request method is not POST."
            msg += " User attempted to access /newCustResult incorrectly."
            return render_template("formResults.html", message = msg, errors_table = [])
    else:
        flash("You must be logged in to access this page.")
        return redirect(url_for('login'))

# Page listing the customers stored in the database
@app.route('/listCustomers')
def list_customers():
    if session.get('logged_in') and session.get('security_level') == 1:
        # Displays the customers using sql.Row objects
        # This allows name indexing in the HTML page
        conn = sql.connect("CustOrders.db")
        conn.row_factory = sql.Row
        cur = conn.cursor()

        cur.execute("SELECT * FROM Customers;")
        cust_rows = cur.fetchall()
        conn.close()

        return render_template("listCustomers.html", records = cust_rows)
    elif session.get('security_level') != 1:
        redirect(url_for('invalid'))
    elif not session.get('logged_in'):
        flash("You must be logged in to access this page.")
        return redirect(url_for('login'))
    else:
        redirect(url_for('invalid'))

@app.route('/newOrder')
def new_order():
    if session.get('logged_in'):
        return render_template("newOrder.html")
    else:
        flash("You must be logged in to access this page.")
        return redirect(url_for('login'))

@app.route('/newOrderResult', methods = ['POST', 'GET'])
def new_order_result():
    if session.get('logged_in'):
        if request.method == 'POST':
            err_table = []

            new_cust_id = session.get('id')
            new_sku_num = request.form.get('SKUNum', "", str)
            new_quantity = request.form.get('Quantity', -1, int)
            new_price = request.form.get('Price', -1.0, float)
            new_card_num = request.form.get('CardNum', "", str)

            if new_sku_num is None or new_sku_num.strip() == "":
                err_table.append("Can't place new order; 'Item SKU Number' field is blank or invalid")

            if new_quantity is None or new_quantity == -1:
                err_table.append("Can't place new order; 'Quantity' field is blank or invalid")
            elif new_quantity <= 0:
                err_table.append("Can't place new order; 'Quantity' must be greater than 0")

            if new_price is None or new_price == -1.0:
                err_table.append("Can't place new order; 'Price' field is blank or invalid")
            elif new_price <= 0.0:
                err_table.append("Can't place new order; 'Price' must be greater than 0")

            if new_card_num is None or new_card_num.strip() == "":
                err_table.append("Can't place new order; 'Credit Card Number' field is blank or invalid")

            if len(err_table) == 0:
                try:
                    conn = sql.connect("CustOrders.db")
                    cur = conn.cursor()

                    cur.execute('''
                        INSERT INTO Orders (CustId, ItemSkewNum, Quantity, Price, CreditCardNum)
                        VALUES (?, ?, ?, ?, ?);
                    ''', (new_cust_id, new_sku_num, new_quantity, new_price, new_card_num))

                    conn.commit()
                    msg = "Order successfully placed!"
                except Exception as excpt:
                    conn.rollback()
                    msg = f"Error placing new order: {excpt}"
                    return render_template("formResults.html", message = msg, errors_table = [])
                finally:
                    conn.close()
                    return render_template("formResults.html", message = msg, errors_table = [])
            else:
                msg = "Error placing new order:"
                return render_template("formResults.html", message = msg, errors_table = err_table)
        else:
            msg = "Error placing new order: Request method is not POST."
            msg += " User might have attempted to access /newOrderResult incorrectly."
            return render_template("formResults.html", message = msg, errors_table = [])
    else:
        flash("You must be logged in to access this page.")
        return redirect(url_for('login'))

# Page listing the customer orders stored in the database
@app.route('/listOrders')
def list_orders():
    if session.get('logged_in') and session.get('security_level') == 2:
        # Displays the orders using sql.Row objects
        # This allows name indexing in the HTML page
        conn = sql.connect("CustOrders.db")
        conn.row_factory = sql.Row
        cur = conn.cursor()

        cur.execute("SELECT * FROM Orders;")
        order_rows = cur.fetchall()
        conn.close()

        return render_template("listOrders.html", records = order_rows)
    elif session.get('security_level') != 2:
        redirect(url_for('invalid'))
    elif not session.get('logged_in'):
        flash("You must be logged in to access this page.")
        return redirect(url_for('login'))
    else:
        redirect(url_for('invalid'))

@app.route('/logout')
def logout():
    if session.get('logged_in'):
        session.clear()
        flash("You have been logged out.")

    return redirect(url_for('login'))

# Main driver function
if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug = True)