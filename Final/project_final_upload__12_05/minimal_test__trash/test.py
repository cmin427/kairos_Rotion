from _thread import *
import json
import socket
import time


class socketClient:

    HOST = "172.30.1.57"
    # HOST = "127.0.0.1"
    PORT = 9999
    # 서버에 전송할 데이터를 딕셔너리로 해서 json 형태로 변환해서 전송함.
    json_object = {"state": "change", "ticker": "BTC", "buy_limit": 2000}

    def __init__(self):
        # super().__init__()
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.HOST, self.PORT))
        self.alive = True  # 무한루프 종료용

    def client_run(self):
        # 서버에서 오는 데이터가 있다면 recv_data 쓰레드 호출해서 처리함.
        start_new_thread(self.recv_data, (self.client_socket,))
        print(">> Connect Server")

        while self.alive:
            print("json: ", self.json_object)
            # 전송할 데이터를 json형태로 dump함
            json_string = json.dumps(self.json_object)
            # 인코딩해서 서버로 보냄
            self.client_socket.send(json_string.encode())
            time.sleep(10)  # 10초 주기로 반복

    # 서버에서 오는 데이터 처리하는 쓰레드
    def recv_data(self, client_socket):
        while True:
            try:
                data = client_socket.recv(1024)
                # repr: 받은 데이터(obj)를 디코드해서 str로 변환함
                print("receive: ", repr(data.decode()))
            except ConnectionResetError as ex:
                break
            except Exception as ex:
                print(ex)
        self.alive = False


client = socketClient()
client.client_run()
