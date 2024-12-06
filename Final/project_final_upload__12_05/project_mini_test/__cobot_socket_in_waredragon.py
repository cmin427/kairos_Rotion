# from robot_module.robotParts import AGV_PositionController, SocketManagerToKiosk,RobotArmController,CameraManager,ArucoDetector,SocketManagerToCobot
import time
import socket


server_ip='172.30.1.57'
server_port=9999

        

# 클라이언트 소켓 생성
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((server_ip, server_port))  # 클라이언트의 포트 번호
print("\n코봇과 소켓 통신으로 연결됨. 코봇의 포트: ",server_ip,".",server_port,'\n\n')

#코봇에 PICK 명령어 전송
client_socket.sendall(bytes("PICK", "utf-8"))
print("\n코봇에 'PICK' 전송\n")

while True:
    
    message, addr = client_socket.recvfrom(1024)
    msg_decoded=message.decode()
    print("cobot said: ",msg_decoded)
    if msg_decoded == "DONE":
        print("\n 코봇으로부너 'DONE' 메시지를 받았습니다. ")
        break



# cobot=SocketManagerToCobot()
# while True:
#     instring=input("명령어 입력")
#     if instring=="P":
#         cobot.send_pickup_request_to_cobot_and_wait()
#     elif instring=="Q":
#         break
#     else:
#         pass 