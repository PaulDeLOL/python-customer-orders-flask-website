from socketserver import BaseRequestHandler, TCPServer
from CustomerOrdersEncryption import cipher
import sqlite3 as sql

class MyTCPHandler(BaseRequestHandler):
    def handle(self):
        encrypted_message = self.request.recv(1024)
        message = cipher.decrypt(encrypted_message)

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

        conn = sql.connect("CustOrders.db")
        cur = conn.cursor()
        cur.execute('''
            SELECT * FROM Customers WHERE CustId = ?;
        ''', (values[0],))
        cust_id_check = cur.fetchone()

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

        print(f"{self.client_address[0]} sent a message: {encrypted_message}")
        if len(err_table) == 0:
            try:
                print(f"Customer ID: {values[0]}")
                values[4] = cipher.encrypt(values[4])

                cur.execute('''
                    INSERT INTO Orders (CustId, ItemSkewNum, Quantity, Price, CreditCardNum)
                    VALUES (?, ?, ?, ?, ?);
                ''', (values[0], values[1], values[2], values[3], values[4]))
                conn.commit()

                print("Record successfully added")
            except Exception as excptn:
                conn.rollback()
                print(f"Error adding record: {excptn}")
            finally:
                conn.close()
                print("\n", end = "")
        """
        else:
            print("Error adding record:")
            for err in err_table:
                print(f"    - {err}")
            print("\n", end = "")
        """


if __name__ == '__main__':
    try:
        HOST, PORT = "localhost", 9999
        server = TCPServer((HOST, PORT), MyTCPHandler)
        server.serve_forever()
    except Exception as excpt:
        print(f"Server error: {excpt}")
        exit(1)
    finally:
        server.server_close()
