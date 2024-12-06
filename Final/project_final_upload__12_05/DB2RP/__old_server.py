# Receiving
# 안씀
import socket
import json

HOST = '0.0.0.0'
PORT = 65432

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)
print("Server is running, waiting for client...")

conn, addr = server_socket.accept()
print("Client Connected:", addr)

try:
    data = conn.recv(1024).decode()
    # print("Received data:", data)
    deserialized_data = json.loads(data) 
    print("Deserialized data:", deserialized_data)
    
except json.JSONDecodeError as e:
    print("JSON decoding error:", e)
    
finally:
    conn.close()
    server_socket.close()