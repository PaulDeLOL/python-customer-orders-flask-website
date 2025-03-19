from flask import Flask, render_template
import sqlite3 as sql
app = Flask(__name__)

@app.route('/')
def homepage():
    return render_template("homepage.html")

@app.route('/newCustomer')
def new_customer():
    return render_template("newCustomer.html")

@app.route('/listCustomers')
def list_customers():
    return "Hello List Customers"

@app.route('/listOrders')
def list_orders():
    return "Hello List Orders"

if __name__ == "__main__":
    app.run(debug = True)