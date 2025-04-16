from socketserver import BaseRequestHandler, TCPServer
from CustomerOrdersEncryption import cipher
import sqlite3 as sql
import hmac, hashlib

def verify(msg, sig):
    authentication_key = b'dc6f3f59'
    computed_sha = hmac.new(authentication_key, msg, digestmod = hashlib.sha3_512).digest()

    if sig != computed_sha:
        return False
    else:
        return True

class MyTCPHandler(BaseRequestHandler):
    def handle(self):
        received_message = self.request.recv(1024)

        encrypted_message = received_message[:len(received_message) - 64]
        authentication_tag = received_message[-64:]

        if verify(cipher.decrypt(encrypted_message).encode("UTF-8"), authentication_tag):
            order_id = int(cipher.decrypt(encrypted_message))

            conn = sql.connect("CustOrders.db")
            cur = conn.cursor()
            cur.execute('''
                SELECT * FROM Orders WHERE OrderId = ?;
            ''', (order_id,))
            order_id_check = cur.fetchone()

            err_table = []
            if order_id is None or order_id == -1:
                err_table.append("Can't delete order; 'Order ID' field is blank or invalid")
            elif not isinstance(order_id, int):
                err_table.append("Can't delete order; order ID should be an integer")
            elif order_id <= 0:
                err_table.append("Can't delete order; order ID must be greater than 0")
            elif order_id_check is None:
                err_table.append("Can't delete order; order ID not found in database.")

            if len(err_table) == 0:
                try:
                    cur.execute('''
                        DELETE FROM Orders WHERE OrderId == ?;
                    ''', (order_id,))
                    conn.commit()
                    print("Record successfully deleted")
                except Exception as excptn:
                    conn.rollback()
                    print(f"Error deleting record: {excptn}")
                finally:
                    conn.close()
            else:
                print("\n", end = "")
                print("Error deleting record:")
                for err in err_table:
                    print(f"    - {err}")
                print("\n", end = "")
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

    # Code structure for encrypted message reception with authentication tag
    """
    body = str(3)
    print(f"Original message: {body}")
    print(f"Original message encoded: {body.encode("UTF-8")}")
    body_encrypted = cipher.encrypt(body)
    print(f"Original message encrypted: {body_encrypted}\n")

    secret = b'dc6f3f59'
    computed_signature = hmac.new(secret, body.encode("UTF-8"), digestmod = hashlib.sha3_512).digest()
    print(f"Tag of message: {computed_signature}")
    print(f"Length of tag of message: {len(computed_signature)}")
    sent_message = body_encrypted + computed_signature
    print(f"Sent message: {sent_message}\n")

    message_encrypted = sent_message[:len(sent_message) - 64]
    message = cipher.decrypt(message_encrypted)
    message = message.encode("UTF-8")
    tag = sent_message[-64:]

    if verify(message, tag):
        print("Message verified")
        print(f"Message: {message.decode("UTF-8")}\n")
    else:
        print("Unauthenticated message\n")
    """
