
# 데모 키오스크 

import threading
import os
import time
import socket
import msvcrt
import json

# 서버 IP 주소와 포트 설정 (서버가 실행되는 Raspberry Pi의 IP 주소를 입력)
server_ip = '172.30.1.57'
server_port = 9999
# 소켓 생성 및 연결
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # 클라이언트 한개만 붙는 소켓이라고 최적화
server_socket.bind((server_ip,server_port))
server_socket.listen() # 클라이언트 1개만 허용
print(f"서버가 {server_ip}:{server_port}에서 대기 중입니다...")

conn, addr = server_socket.accept()
print(f"클라이언트 {addr}와 연결되었습니다.")

ID_file="pass_id.txt"

if not os.path.exists(ID_file):
    with open(ID_file, 'x') as f:
        f.write("")
else:
    with open(ID_file,"w") as f:
        f.write("")

def thread_IDfile_reading(kiosk): #데몬으로 설정하기 
    while True:
        with open(ID_file,"r") as f:
            txt_received=f.read()
        
        if txt_received !="": # 228 등 
            goods_id=int(txt_received)
            kiosk.current_buying_item_id =goods_id    
            kiosk.selected_item=goods_id
            with open(ID_file,"w") as f:
                f.write("")
                
                
class Kiosk:
    def __init__(self):
        self.current_buying_item_id=None
        self.selected_item=None
    def sendDataToChangryong(self, db_send_to_Changryong):
        # 데이터 직렬화 (JSON 문자열로 변환)
        try:
            serialized_data = json.dumps(db_send_to_Changryong)
            print("Serialized data to send:", serialized_data)
        except Exception as e:
            print("JSON 직렬화 오류:", e)
            return

        
        try:
           
            
            # 데이터 전송
            conn.sendall(serialized_data.encode())
            print("데이터를 전송했습니다:", serialized_data)
 
        except ConnectionResetError as ex:
            print("현재 연결은 원격 호스트에 의해 강제로 끊겼습니다. 서버 소켓을 해제하고 시스템 종료.")
            conn.close()
            sys.exit(1)

           
if __name__ == "__main__":
    
    
    
    window = Kiosk()
    th_id=threading.Thread(target=thread_IDfile_reading,args=(window,))
    th_id.daemon=True
    
    
    th_id.start()
    
    while True:
        char = msvcrt.getch()
        if char=='\n':
            