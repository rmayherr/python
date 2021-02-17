import socket
from rot13 import rot13


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ss:
    ss.bind((socket.gethostname(), 9999))
    ss.listen(1)
    conn, addr = ss.accept()
    with conn:
        print('Connected. IP:', addr)
        while True:
            data = conn.recv(1024)
            if not data:
                break
            conn.send(rot13(data.decode()).encode())



