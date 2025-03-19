from flask import Flask, render_template, request, flash, redirect, url_for
import sqlite3 as sql
app = Flask(__name__)

@app.route('/')
def homepage():
    return render_template("homepage.html")

@app.route('/newCustomer')
def new_customer():
    return render_template("newCustomer.html")

@app.route('/newCustResult', methods=['POST', 'GET'])
def new_cust_result():
    if request.method == 'POST':
        err_table = []

        new_name = request.form.get('Name', "", str)
        new_age = request.form.get('Age', -1, int)
        new_number = request.form.get('Number', "", str)
        new_level = request.form.get('SecurLevel', -1, int)
        new_password = request.form.get('Password', "", str)

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

        if len(err_table) == 0:
            try:
                conn = sql.connect("CustOrders.db")
                cur = conn.cursor()

                cur.execute('''
                    INSERT INTO Customers (Name, Age, PhNum, SecurityLevel, LoginPassword)
                    VALUES (?, ?, ?, ?, ?);
                ''', (new_name, new_age, new_number, new_level, new_password))

                conn.commit()
                msg = "Customer successfully created!"
            except Exception as excpt:
                conn.rollback()
                msg = f"Error creating a new customer: {excpt}"
                print(msg)
                return render_template("newCustResult.html", message = msg, errors_table = [])
            finally:
                conn.close()
                return render_template("newCustResult.html", message = msg, errors_table = [])
        else:
            msg = "Error creating a new customer:"
            return render_template("newCustResult.html", message = msg, errors_table = err_table)
    else:
        msg = "Error creating a new customer: Request method is not POST"
        return render_template("newCustResult.html", message = msg, errors_table = [])

@app.route('/listCustomers')
def list_customers():
    conn = sql.connect("CustOrders.db")
    conn.row_factory = sql.Row
    cur = conn.cursor()

    cur.execute("SELECT * FROM Customers;")
    cust_rows = cur.fetchall()
    conn.close()

    return render_template("listCustomers.html", records = cust_rows)

@app.route('/listOrders')
def list_orders():
    conn = sql.connect("CustOrders.db")
    conn.row_factory = sql.Row
    cur = conn.cursor()

    cur.execute("SELECT * FROM Orders;")
    order_rows = cur.fetchall()
    conn.close()

    return render_template("listOrders.html", records = order_rows)

if __name__ == "__main__":
    app.run(debug = True)