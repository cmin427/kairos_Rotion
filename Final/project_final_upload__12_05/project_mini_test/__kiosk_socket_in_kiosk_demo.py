import socket
import msvcrt  # Windows 환경에서 콘솔 입력을 위한 모듈
import json
import sys
server_ip = "172.30.1.57"  # 서버 IP
server_port = 9999  # 서버 포트 번호

server_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # 클라이언트 한개만 붙는 소켓이라고 최적화
server_socket.bind((server_ip,server_port))
server_socket.listen() # 클라이언트 1개만 허용


print(f"서버가 {server_ip}:{server_port}에서 대기 중입니다...")

conn, addr = server_socket.accept()
print(f"클라이언트 {addr}와 연결되었습니다.")




while True:
    print("ESC: 프로그램 종료\nq: order list 전송하기\n")
    key = msvcrt.getch()  # 키 입력 받기

    if key == b'\x1b':  # Esc 키 코드 (b'\x1b'는 Esc의 16진수 코드)
        conn.close()
        print("프로그램을 종료합니다.")
        break
    elif key == b'q':
        order_list=[]
        print("포지션, 수량 입력. (예시: A1 5) \"SEND\"를 입력하면 전체가 창룡이로 전송됨 ")
        while True:   
            order = input("입력:")
            if order=='SEND':
                try:
                    serialized_data = json.dumps(order_list)
                    conn.sendall(serialized_data.encode())
                    break
                except ConnectionResetError as ex:
                    print("현재 연결은 원격 호스트에 의해 강제로 끊겼습니다. 시스템 종료.")
                    conn.close()
                    sys.exit(1)
                    
                
                
            else:
                order_split=order.split()
                order_list.append(order_split)
        
    else:
        pass  # 다른 입력은 무시
    
conn.close()