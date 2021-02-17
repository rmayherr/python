import socket
import sys

if len(sys.argv) != 3:
    print("Usage: python3", sys.argv[0], "hostname port")
    sys.exit(1)
hostname = sys.argv[1]
port = int(sys.argv[2])
data = "Hello Pisti!\n"
data = data +  """
    Küldöm ennek a python progamnak a forráskódját a neten egy socket-en keresztül...

    import socket
    import sys

    hostname = sys.argv[1]
    port = int(sys.argv[2])
    data = "Hello Pisti!\n" 
    try:
        print('Csatlakozás', hostname, '...', end='')
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((hostname, port))
            s.sendall(data.encode())
            print('Adatküldés kész.')
    except Exception as e:
        print(f'Hiba a csatornában!')
        print(f'\t részletesebben: ' + str(e))
 """
try:
    print('Csatlakozás', hostname, '...', end='')
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((hostname, port))
        s.sendall(data.encode())
        print('Adatküldés kész.')
except Exception as e:
    print(f'Hiba a csatornában!')
    print(f'\t részletesebben: ' + str(e))
