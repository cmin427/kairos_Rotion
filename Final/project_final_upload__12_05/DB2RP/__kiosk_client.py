# 데모 창룡

import socket
import threading 
import json
import time

class DemoWareDragon:
    def __init__(self):
        self.customers_order_list=[]
        self.socket_thread=self.socket_thread_init()
        
    def socket_thread_init(self): # 소켓 스레드 시작시키고 스레드 객체 리턴. # 작성 완
        
        self.server_ip='172.30.1.57'
        self.port=9999
        
        self.client_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       
        self.client_socket.connect((self.server_ip, self.port))
        
        print("connected to kiosk")
        
        server_th=threading.Thread(target=self.thread_ConnectedToServer)
        server_th.daemon=True # 메인 함수가 끝날때 알아서 끝남
        server_th.start()
        
        return server_th
 
    def thread_ConnectedToServer(self): # 키오스크로부터 데이터 있으면 받아서 order list에 추가 
            
            
            while True:
            # 클라이언트로부터 메시지 수신
                data = self.client_socket.recv(1024*10) # 1024*10 바이트까지 수신
                if not data:
                    print(">> Disconnected by server")
                    break
                json_string = data.decode()
                deserialized_data = json.loads(json_string) # [[A0,2],[B2,1]]
                # print(f"키오스크 said : {deserialized_data}")
                
                self. customers_order_list.insert(0,deserialized_data) 
                # print(self.customers_order_list)
                
            self.client_socket.close()
            print("서버 소켓이 닫혔습니다")



dw=DemoWareDragon()
while True:
    print("키오스크가 요청한 주문 목록:",dw.customers_order_list)
    time.sleep(1)