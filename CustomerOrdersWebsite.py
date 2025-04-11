"""
Name: Pablo Guardia
Date: 04/07/2025
Assignment: Module 13: Send Encrypted Message
Due Date: 04/13/2025

About this project: This script is a basic website written in Flask that
allows users to manage customers and the ordering of items from a hypothetical
database. Each user has a set security level that gives them different
privileges, enabling role-based access control.

Update 1.3:
- Added the "Submit An Order" page, which is similar to "Add New Order", but it
allows level 2 users to submit an order for ANY customer ID, which is then
processed by another Python script that acts like a server. The server is what
performs the addition of records to the database in this menu option, and the
appropriate data is encrypted when being sent to the server.

Assumptions: N/A
All work below was performed by Pablo Guardia
"""

from flask import (Flask, render_template, request,
                   redirect, url_for, session, flash)
import sqlite3 as sql
import os
from CustomerOrdersEncryption import cipher
import pandas as pd
from socket import socket, AF_INET, SOCK_STREAM

app = Flask(__name__)

"""
Nearly all functions now have login checks, which check if there's a user
logged into the website who can therefore access the internal pages. Also,
certain pages can now only be accessed by users with the correct security
level, so functionality has been changed slightly to perform said checks.
"""

# Index function
@app.route('/')
def index():
    # Redirects to home if user is logged in, login if not
    if session.get('logged_in'):
        return redirect(url_for("home"))
    else:
        return redirect(url_for("login"))

# Login page
@app.route('/login')
def login():
    if not session.get('logged_in'):
        return render_template("login.html")
    # If the user was already logged in, redirect them to the homepage and
    # prompt them to click "Log out" if they really want to log in again
    else:
        flash("You are already logged in. Click \"Log out\" to log out.")
        return redirect(url_for("home"))

# Login check function that checks if the user exists in the database
@app.route('/loginCheck', methods = ['POST', 'GET'])
def login_check():
    if not session.get('logged_in'):
        if request.method == "POST":
            conn = sql.connect("CustOrders.db")
            conn.row_factory = sql.Row
            cur = conn.cursor()

            # Takes in the user's input from the form
            username = request.form.get('Username', "", str)
            password = request.form.get('Password', "", str)

            # Encrypts the username and password the user entered in so that
            # they match the entries in the database
            encrypted_username = cipher.encrypt(username)
            encrypted_password = cipher.encrypt(password)

            # Checks if there is a record in the database matching the
            # encrypted username and password
            cur.execute('''
                SELECT * FROM Customers
                WHERE Name == ? AND LoginPassword == ?;
            ''', (encrypted_username, encrypted_password))
            check = cur.fetchone()

            # If there is such a record, create session variables based on the user's data
            # Signal to the Flask website that the user is logged in with another session variable
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
                return redirect(url_for("home"))

            # Prompt the user to try again if the username or password are invalid
            else:
                session['logged_in'] = False
                flash("Login failed. Invalid username or password.")
                conn.close()
                return redirect(url_for("login"))
        # If the method was somehow not POST, redirect to the login page
        else:
            flash("Login error. Request method is not POST.")
            flash("User might have attempted to access /loginCheck illegally.")
            return redirect(url_for("login"))
    # If the user was already logged in, redirect them to the homepage and
    # prompt them to click "Log out" if they really want to log in again
    else:
        flash("You are already logged in. Click \"Log out\" to log out.")
        return redirect(url_for("home"))

# Home page
@app.route('/home')
def home():
    if session.get('logged_in'):
        # Decrypt the current session's username to display it on top of the homepage
        decrypted_username = cipher.decrypt(session.get('username'))
        return render_template("homepage.html",
            username = decrypted_username)
    else:
        flash("You must be logged in to access this page.")
        return redirect(url_for("login"))

# Page that lists all orders placed by the current user in the session
@app.route('/listUserOrders')
def list_user_orders():
    if session.get('logged_in'):
        conn = sql.connect("CustOrders.db")
        conn.row_factory = sql.Row
        cur = conn.cursor()

        # No longer uses row objects by themselves, but now uses a Pandas
        # DataFrame. This allows for easier decryption of credit card
        # numbers, while still allowing indexing by column name
        cur.execute('''SELECT * FROM Orders WHERE CustId == ?;''', (session['id'],))
        user_order_rows = pd.DataFrame(cur.fetchall(), columns = [
            "OrderId",
            "CustId",
            "ItemSkewNum",
            "Quantity",
            "Price",
            "CreditCardNum"])
        conn.close()

        # Decryption of data
        for i, row in user_order_rows.iterrows():
            user_order_rows._set_value(i, "CreditCardNum", cipher.decrypt(row["CreditCardNum"]))
        decrypted_username = cipher.decrypt(session.get('username'))

        return render_template("listUserOrders.html",
            records = user_order_rows,
            username = decrypted_username)
    else:
        flash("You must be logged in to access this page.")
        return redirect(url_for("login"))

# Page containing a form to add a new customer to the database
@app.route('/newCustomer')
def new_customer():
    if session.get('logged_in') and session.get('security_level') >= 2:
        return render_template("newCustomer.html")
    # Redirect the user to a "Not Found" page if their security level is invalid,
    # or back to the login page if they were not logged in at all
    elif session.get('security_level') < 2:
        return redirect("/notFound")
    elif not session.get('logged_in'):
        flash("You must be logged in to access this page.")
        return redirect(url_for("login"))
    else:
        return redirect("/notFound")

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

                    # Encrypts the data entered by the user so that it is
                    # stored securely in the database
                    encrypted_name = cipher.encrypt(new_name)
                    encrypted_number = cipher.encrypt(new_number)
                    encrypted_password = cipher.encrypt(new_password)

                    cur.execute('''
                        INSERT INTO Customers (Name, Age, PhNum, SecurityLevel, LoginPassword)
                        VALUES (?, ?, ?, ?, ?);
                    ''', (encrypted_name, new_age, encrypted_number, new_level,
                          encrypted_password))

                    conn.commit()
                    msg = "Customer successfully created!"
                except Exception as excpt:
                    # If something went wrong, display the exception
                    conn.rollback()
                    msg = f"Error creating a new customer: {excpt}"
                    return render_template("formResults.html",
                        message = msg,
                        errors_table = [])
                finally:
                    conn.close()
                    return render_template("formResults.html",
                        message = msg,
                        errors_table = [])
            # Otherwise, if err_table contains errors, display them all on the results page
            else:
                msg = "Error creating a new customer:"
                return render_template("formResults.html",
                    message = msg,
                    errors_table = err_table)
        # If the method was somehow not POST, address that and display an error
        else:
            msg = "Error creating a new customer: Request method is not POST."
            msg += " User attempted to access /newCustResult incorrectly."
            return render_template("formResults.html",
                message = msg,
                errors_table = [])
    # If the user was not logged in, redirect them to the login page with an error
    else:
        flash("You must be logged in to access this page.")
        return redirect(url_for("login"))

# Page listing the customers stored in the database
@app.route('/listCustomers')
def list_customers():
    if session.get('logged_in') and session.get('security_level') == 1:
        conn = sql.connect("CustOrders.db")
        conn.row_factory = sql.Row
        cur = conn.cursor()

        # No longer uses row objects by themselves, but now uses a Pandas
        # DataFrame. This allows for easier decryption of credit card
        # numbers, while still allowing indexing by column name
        cur.execute('''SELECT * FROM Customers;''')
        cust_rows = pd.DataFrame(cur.fetchall(), columns = [
            "CustId",
            "Name",
            "Age",
            "PhNum",
            "SecurityLevel",
            "LoginPassword"])
        conn.close()

        # Decryption of data
        for i, row in cust_rows.iterrows():
            cust_rows._set_value(i, "Name", cipher.decrypt(row["Name"]))
            cust_rows._set_value(i, "PhNum", cipher.decrypt(row["PhNum"]))
            cust_rows._set_value(i, "LoginPassword", cipher.decrypt(row["LoginPassword"]))

        return render_template("listCustomers.html",
            records = cust_rows)
    # Redirect the user to a "Not Found" page if their security level is invalid,
    # or back to the login page if they were not logged in at all
    elif session.get('security_level') != 1:
        return redirect("/notFound")
    elif not session.get('logged_in'):
        flash("You must be logged in to access this page.")
        return redirect(url_for("login"))
    else:
        return redirect("/notFound")

# Page containing a form to let the user place a new order
# Said order is added to the database
@app.route('/newOrder')
def new_order():
    if session.get('logged_in'):
        return render_template("newOrder.html")
    else:
        flash("You must be logged in to access this page.")
        return redirect(url_for("login"))

# Page displaying the results of placing a new order (or failing to do so!)
@app.route('/newOrderResult', methods = ['POST', 'GET'])
def new_order_result():
    if session.get('logged_in'):
        if request.method == 'POST':
            # Stores error messages in a table
            err_table = []

            # Obtains the fields from the form filled out
            new_cust_id = session.get('id')
            new_sku_num = request.form.get('SKUNum', "", str)
            new_quantity = request.form.get('Quantity', -1, int)
            new_price = request.form.get('Price', -1.0, float)
            new_card_num = request.form.get('CardNum', "", str)

            # Validates input according to constraints defined in assignment instructions
            # Examples: No empty strings, quantity greater than 0, etc.
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

            # If err_table has no elements, meaning no errors occurred...
            if len(err_table) == 0:
                try:
                    # Try inserting the new record into the database.
                    conn = sql.connect("CustOrders.db")
                    cur = conn.cursor()

                    # Encrypts the data entered by the user so that it is
                    # stored securely in the database
                    encrypted_card_num = cipher.encrypt(new_card_num)

                    cur.execute('''
                        INSERT INTO Orders (CustId, ItemSkewNum, Quantity, Price, CreditCardNum)
                        VALUES (?, ?, ?, ?, ?);
                    ''', (new_cust_id, new_sku_num, new_quantity, new_price,
                          encrypted_card_num))

                    conn.commit()
                    msg = "Order successfully placed!"
                except Exception as excpt:
                    # If something went wrong, display the exception
                    conn.rollback()
                    msg = f"Error placing new order: {excpt}"
                    return render_template("formResults.html",
                        message = msg,
                        errors_table = [])
                finally:
                    conn.close()
                    return render_template("formResults.html",
                        message = msg,
                        errors_table = [])
            # Otherwise, if err_table contains errors, display them all on the results page
            else:
                msg = "Error placing new order:"
                return render_template("formResults.html",
                    message = msg,
                    errors_table = err_table)
        # If the method was somehow not POST, address that and display an error
        else:
            msg = "Error placing new order: Request method is not POST."
            msg += " User might have attempted to access /newOrderResult incorrectly."
            return render_template("formResults.html",
                message = msg,
                errors_table = [])
    # If the user was not logged in, redirect them to the login page with an error
    else:
        flash("You must be logged in to access this page.")
        return redirect(url_for("login"))

# Page listing the customer orders stored in the database
@app.route('/listOrders')
def list_orders():
    if session.get('logged_in') and session.get('security_level') == 2:
        conn = sql.connect("CustOrders.db")
        conn.row_factory = sql.Row
        cur = conn.cursor()

        # No longer uses row objects by themselves, but now uses a Pandas
        # DataFrame. This allows for easier decryption of credit card
        # numbers, while still allowing indexing by column name
        cur.execute('''SELECT * FROM Orders;''')
        order_rows = pd.DataFrame(cur.fetchall(), columns = [
            "OrderId",
            "CustId",
            "ItemSkewNum",
            "Quantity",
            "Price",
            "CreditCardNum"
        ])
        conn.close()

        # Decryption of data
        for i, row in order_rows.iterrows():
            order_rows._set_value(i, "CreditCardNum", cipher.decrypt(row["CreditCardNum"]))

        return render_template("listOrders.html",
            records = order_rows)
    # Redirect the user to a "Not Found" page if their security level is invalid,
    # or back to the login page if they were not logged in at all
    elif session.get('security_level') != 2:
        return redirect("/notFound")
    elif not session.get('logged_in'):
        flash("You must be logged in to access this page.")
        return redirect(url_for("login"))
    else:
        return redirect("/notFound")

# Page containing a form to let the user submit a new order
# Similar to "Add New Order", but works with a server
@app.route('/submitOrder')
def submit_order():
    if session.get('logged_in') and session.get('security_level') == 2:
        return render_template("submitOrder.html")
    # Redirect the user to a "Not Found" page if their security level is invalid,
    # or back to the login page if they were not logged in at all
    elif session.get('security_level') != 2:
        return redirect("/notFound")
    elif not session.get('logged_in'):
        flash("You must be logged in to access this page.")
        return redirect(url_for("login"))
    else:
        return redirect("/notFound")

# Page displaying the results of submitting a new order (or failing to do so!)
@app.route('/submitOrderResult', methods = ['POST', 'GET'])
def submit_order_result():
    if session.get('logged_in'):
        if request.method == 'POST':
            # Stores error messages in a table
            err_table = []
            conn = sql.connect("CustOrders.db")
            cur = conn.cursor()

            # Obtains the fields from the form filled out
            sub_cust_id = request.form.get('CustID', -1, int)
            sub_sku_num = request.form.get('SKUNum', "", str)
            sub_quantity = request.form.get('Quantity', -1, int)
            sub_price = request.form.get('Price', -1.0, float)
            sub_card_num = request.form.get('CardNum', "", str)

            # Performs a quick SELECT query on the database to check if the
            # Customer ID the user entered exists in the database
            cur.execute('''
                SELECT * FROM Customers WHERE CustId = ?;
            ''', (sub_cust_id,))
            cust_id_check = cur.fetchone()
            conn.close()

            # Validates input according to constraints defined in assignment instructions
            # Examples: No empty strings, quantity greater than 0, etc.
            if sub_cust_id is None or sub_cust_id == -1:
                err_table.append("Can't submit order; 'Customer ID' field is blank or invalid")
            elif not isinstance(sub_cust_id, int):
                err_table.append("customer ID should be an integer")
            elif sub_cust_id <= 0:
                err_table.append("Can't submit order; customer ID must be greater than 0")
            elif cust_id_check is None:
                err_table.append("Can't submit order; customer ID not found in database.")

            if sub_sku_num is None or sub_sku_num.strip() == "":
                err_table.append("Can't submit order; 'Item SKU Number' field is blank or invalid")

            if sub_quantity is None or sub_quantity == -1:
                err_table.append("Can't submit order; 'Quantity' field is blank or invalid")
            elif not isinstance(sub_quantity, int):
                err_table.append("Can't submit order; quantity should be an integer")
            elif sub_quantity <= 0:
                err_table.append("Can't submit order; quantity must be greater than 0")

            if sub_price is None or sub_price == -1.0:
                err_table.append("Can't submit order; 'Price' field is blank or invalid")
            elif not isinstance(sub_price, float):
                err_table.append("Can't submit order; price should be a real number with at least 2 decimal places")
            elif sub_price <= 0.0:
                err_table.append("Can't submit order; price must be greater than 0")

            if sub_card_num is None or sub_card_num.strip() == "":
                err_table.append("Can't submit order; 'Credit Card Number' field is blank or invalid")

            # If err_table has no elements, meaning no errors occurred...
            if len(err_table) == 0:
                try:
                    # Connect to a "localhost" server with port 9999
                    HOST, PORT = "localhost", 9999
                    sock = socket(AF_INET, SOCK_STREAM)
                    sock.connect((HOST, PORT))
                    sock_msg = ""

                    # Construct the message to be sent, made up of the values
                    # the user entered. The entire message will be encrypted
                    # before being sent
                    sock_msg += f"Customer ID: {sub_cust_id}\n"
                    sock_msg += f"Item SKU Number: {sub_sku_num}\n"
                    sock_msg += f"Quantity: {sub_quantity}\n"
                    sock_msg += f"Price: {sub_price}\n"
                    sock_msg += f"Card Number: {sub_card_num}\n"
                    sock_msg = cipher.encrypt(sock_msg)

                    # Sends the message and closes the connection to the server
                    sock.sendall(sock_msg)
                    sock.close()
                    msg = "Order successfully submitted!"
                except Exception as excpt:
                    # If something went wrong, display the exception
                    msg = f"Error submitting order: {excpt}"
                    return render_template("formResults.html",
                        message = msg,
                        errors_table = [])
                finally:
                    return render_template("formResults.html",
                        message = msg,
                        errors_table = [])
            # Otherwise, if err_table contains errors, display them all on the results page
            else:
                msg = "Error submitting order"
                return render_template("formResults.html",
                    message = msg,
                    errors_table = err_table)
        # If the method was somehow not POST, address that and display an error
        else:
            msg = "Error submitting order: Request method is not POST."
            msg += " User might have attempted to access /submitOrderResult incorrectly."
            return render_template("formResults.html",
                message = msg,
                errors_table = [])
    # If the user was not logged in, redirect them to the login page with an error
    else:
        flash("You must be logged in to access this page.")
        return redirect(url_for("login"))

# Logs the user out while clearing all session variables
@app.route('/logout')
def logout():
    if session.get('logged_in'):
        session.clear()
        flash("You have been logged out.")

    return redirect(url_for("login"))

# Main driver function
if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug = True)
