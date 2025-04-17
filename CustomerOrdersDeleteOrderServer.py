"""
Name: Pablo Guardia
Date: 04/15/2025
Assignment: Module 14: Send Authenticated Message
Due Date: 04/20/2025

About this project: This script is an implementation of a socketserver that
processes the delete order requests made by a user. Here is where the
encrypted ID is decrypted and checked for its authentication tag. Then, if
all is well, the order with the corresponding ID is removed from the database.

Assumptions: N/A
All work below was performed by Pablo Guardia
"""

from socketserver import BaseRequestHandler, TCPServer
from CustomerOrdersEncryption import cipher
import sqlite3 as sql
import hmac, hashlib

# Function that verifies the authentication tag of the ID sent
def verify(msg, sig):
    authentication_key = b'dc6f3f59'
    computed_sha = hmac.new(authentication_key, msg, digestmod = hashlib.sha3_512).digest()

    if sig != computed_sha:
        return False
    else:
        return True

# TCP Handler for socketserver
class MyTCPHandler(BaseRequestHandler):
    def handle(self):
        # Reads in the encrypted message being sent by the client
        received_message = self.request.recv(1024)

        # Splits the message into its encrypted part and its authentication tag
        encrypted_message = received_message[:len(received_message) - 64]
        authentication_tag = received_message[-64:]

        # If the authentication tag is successfully verified, processing can start
        if verify(cipher.decrypt(encrypted_message).encode("UTF-8"), authentication_tag):
            # The message is decrypted and the order ID is obtained
            order_id = int(cipher.decrypt(encrypted_message))

            # Performs a quick SELECT query on the database to check if the
            # Order ID the user entered exists in the database
            conn = sql.connect("CustOrders.db")
            cur = conn.cursor()
            cur.execute('''
                SELECT * FROM Orders WHERE OrderId = ?;
            ''', (order_id,))
            order_id_check = cur.fetchone()

            # Stores error messages in a table
            # Validates input according to constraints defined in assignment instructions
            # In this case, Order ID should be greater than 0 and exist in the database
            err_table = []
            if order_id is None or order_id == -1:
                err_table.append("Can't delete order; 'Order ID' field is blank or invalid")
            elif not isinstance(order_id, int):
                err_table.append("Can't delete order; order ID should be an integer")
            elif order_id <= 0:
                err_table.append("Can't delete order; order ID must be greater than 0")
            elif order_id_check is None:
                err_table.append("Can't delete order; order ID not found in database.")

            # If err_table has no elements, meaning no errors occurred...
            if len(err_table) == 0:
                try:
                    # Try deleting the order whose ID matches the one the user entered
                    cur.execute('''
                        DELETE FROM Orders WHERE OrderId == ?;
                    ''', (order_id,))
                    conn.commit()
                    print("Record successfully deleted")
                except Exception as excptn:
                    # If something went wrong, display the exception
                    conn.rollback()
                    print(f"Error deleting record: {excptn}")
                finally:
                    conn.close()
            # Otherwise, if err_table contains errors, display them all on the results page
            else:
                print("\n", end = "")
                print("Error deleting record:")
                for err in err_table:
                    print(f"    - {err}")
                print("\n", end = "")
        # If the authentication tag was invalid or couldn't be verified, don't delete anything
        # and warn the user via a terminal message
        else:
            print("Unauthenticated 'Delete Order' message received! Be on alert! Watch out for bad guys!!!")

# Main server program
if __name__ == '__main__':
    try:
        # Starts hosting a server on "localhost" with port 8888
        # It'll handle any requests that come in from clients and keep serving
        # forever until the script is terminated in PyCharm
        HOST, PORT = "localhost", 8888
        server = TCPServer((HOST, PORT), MyTCPHandler)
        server.serve_forever()
    except Exception as excpt:
        # If something went wrong, display the exception and stop the server
        print(f"Server error: {excpt}")
        exit(1)
    finally:
        server.server_close()
