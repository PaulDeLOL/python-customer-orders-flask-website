from flask import Flask, render_template
import sqlite3 as sql
app = Flask(__name__)

@app.route('/')
def homepage():
    return render_template("home.html")

@app.route('/newCustomer')
def new_customer():
    return "Hello New Customer"

@app.route('/listCustomers')
def list_customers():
    return "Hello List Customers"

@app.route('/listOrders')
def list_orders():
    return "Hello List Orders"

if __name__ == "__main__":
    app.run(debug = True)