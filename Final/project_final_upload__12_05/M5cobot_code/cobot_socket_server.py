import socket
import time
# from pymycobot.mycobot import MyCobot
import sys

# mc = MyCobot('/dev/ttyAMA0',115200)

# def pick_and_place():
#     mc. 
#     # 여기에 팔 움직여서 컨베이어에 놓는 코드 




# 서버 설정
server_ip = "172.30.1.57"  # 서버 IP
server_port = 9999  # 서버 포트 번호

server_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # 클라이언트 한개만 붙는 소켓이라고 최적화
server_socket.bind((server_ip,server_port))
server_socket.listen() # 클라이언트 1개만 허용

print(f"서버가 {server_ip}:{server_port}에서 대기 중입니다...")

conn, addr = server_socket.accept()
print(f"클라이언트 {addr}와 연결되었습니다.")


alive=True

while alive:
    
    while True:
        try:
            message, server_address = conn.recvfrom(1024)
            if message.decode() == "PICK":
                print("서버로부터 'PICK' 메시지를 받았습니다. 작업 시작...")
                break
            if message.decode()=="EXIT":
                # 소켓 닫기
                conn.close()
                sys.exit(1)
        except ConnectionResetError as ex:
                break
        except Exception as ex:
            # print(ex)
            pass
    alive=False   
    
 
    # 작업을 마친 후 "DONE" 메시지 서버로 보내기
    # pick_and_place(mc)
    print("코봇이 작업중...")
    for i in range(3):
        print(i+1)
        time.sleep(1)
    
    conn.sendall(bytes("DONE", "utf-8"))
    
    
    print("서버에게 'DONE' 메시지를 보냈습니다.")


