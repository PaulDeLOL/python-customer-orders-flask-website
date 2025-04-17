"""
Name: Pablo Guardia
Date: 04/07/2025
Assignment: Module 13: Send Encrypted Message
Due Date: 04/13/2025

About this project: This script is an implementation of a socketserver that
processes the submit order requests made by a level 2 user. Here is where
the encrypted message is decrypted and processed before being added to
the database if all is well.

Assumptions: N/A
All work below was performed by Pablo Guardia
"""

from socketserver import BaseRequestHandler, TCPServer
from CustomerOrdersEncryption import cipher
import sqlite3 as sql

# TCP Handler for socketserver
class MyTCPHandler(BaseRequestHandler):
    def handle(self):
        # Reads in the encrypted message being sent by the client
        # Decrypts it to obtain the values entered by the user
        encrypted_message = self.request.recv(1024)
        message = cipher.decrypt(encrypted_message)

        # Using the colons and the newline characters as separators, reads in
        # each field in an order record submitted by the user
        values = []
        i = 0
        while i < len(message):
            if message[i] == ':':
                i += 2
                new_value = ""
                while message[i] != '\n':
                    new_value += message[i]
                    i += 1
                values.append(new_value)
            i += 1

        # Performs a quick SELECT query on the database to check if the
        # Customer ID the user entered exists in the database
        conn = sql.connect("CustOrders.db")
        cur = conn.cursor()
        cur.execute('''
            SELECT * FROM Customers WHERE CustId = ?;
        ''', (values[0],))
        cust_id_check = cur.fetchone()

        # Stores error messages in a table
        # Validates input according to constraints defined in assignment instructions
        # Examples: No empty strings, quantity greater than 0, etc.
        err_table = []
        if values[0] is None or values[0].strip() == "-1":
            err_table.append("'Customer ID' field is blank or invalid")
        else:
            try:
                values[0] = int(values[0])
            except ValueError:
                err_table.append("Customer ID should be an integer")
        if values[0] <= 0:
            err_table.append("Customer ID must be greater than 0")
        elif cust_id_check is None:
            err_table.append("Customer ID not found in database")

        if values[1] is None or values[1].strip() == "":
            err_table.append("'Item SKU Number' field is blank or invalid")

        if values[2] is None or values[2].strip() == "-1":
            err_table.append("'Quantity' field is blank or invalid")
        else:
            try:
                values[2] = int(values[2])
            except ValueError:
                err_table.append("Quantity should be an integer")
        if values[2] <= 0:
            err_table.append("Quantity must be greater than 0")

        if values[3] is None or values[3].strip() == "-1.0":
            err_table.append("'Price' field is blank or invalid")
        else:
            try:
                values[3] = float(values[3])
            except ValueError:
                err_table.append("Price should be a real number with at least 2 decimal places")
        if values[3] <= 0.0:
            err_table.append("Price must be greater than 0")

        if values[4] is None or values[4].strip() == "":
            err_table.append("'Credit Card Number' field is blank or invalid")

        # Prints the encrypted message and the address of the client who sent it
        print(f"{self.client_address[0]} sent a message: {encrypted_message}")

        # If err_table has no elements, meaning no errors occurred...
        if len(err_table) == 0:
            try:
                # Print the Customer ID of the customer whose order is being submitted
                # Encrypt the Credit Card Number field of the order
                print(f"Customer ID: {values[0]}")
                values[4] = cipher.encrypt(values[4])

                # Try inserting the new record into the database.
                cur.execute('''
                    INSERT INTO Orders (CustId, ItemSkewNum, Quantity, Price, CreditCardNum)
                    VALUES (?, ?, ?, ?, ?);
                ''', (values[0], values[1], values[2], values[3], values[4]))
                conn.commit()

                print("Record successfully added")
            except Exception as excptn:
                # If something went wrong, display the exception
                conn.rollback()
                print(f"Error adding record: {excptn}")
            finally:
                conn.close()
                print("\n", end = "")
        # Otherwise, if err_table contains errors, display them all on the results page
        """
        else:
            print("Error adding record:")
            for err in err_table:
                print(f"    - {err}")
            print("\n", end = "")
        """

# Main server program
if __name__ == '__main__':
    try:
        # Starts hosting a server on "localhost" with port 9999
        # It'll handle any requests that come in from clients and keep serving
        # forever until the script is terminated in PyCharm
        HOST, PORT = "localhost", 9999
        server = TCPServer((HOST, PORT), MyTCPHandler)
        server.serve_forever()
    except Exception as excpt:
        # If something went wrong, display the exception and stop the server
        print(f"Server error: {excpt}")
        exit(1)
    finally:
        server.server_close()
