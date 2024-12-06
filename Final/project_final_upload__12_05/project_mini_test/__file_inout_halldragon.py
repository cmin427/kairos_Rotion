import time

info_file = "info.txt"
stop_sign_file="done.txt"

# 파일 두개 내용 초기화 
with open(info_file, 'w') as f: 
    f.write("")
with open(stop_sign_file, 'w') as f:
    f.write("") 
    
    
while True:
    
    while True:
        with open(info_file, 'r') as file:
            # 파일 전체 내용 읽어오기
            contents = file.read()
            
        if contents != "":
            print(contents)
            break
        else:
            time.sleep(1)
            print("라인트레이싱 정보 대기중")
            
    for i in range(5):
        print(f"목표 지점까지 라인트레이싱중...{5-i}초 남음")
        time.sleep(1)
    
    print("목표 지점 도착")
    
    #챗봇에 목표지점 도착 신호 보내기 
    with open(stop_sign_file, 'w') as f:
                f.write("1")
            
    # 운행 종료라고 화면 띄워주는중 
    time.sleep(10)
    
    for i in range(5):
        print(f"초기 위치까지 라인트레이싱중...{5-i}초 남음")
        time.sleep(1)
        
    print("초기 위치 도착")
    
    #info 파일 초기화 하고 chatbot에 초기 위치 도착 신호 보내기 
    with open(info_file, 'w') as f: 
                f.write("")
            
    with open(stop_sign_file, 'w') as f:
        f.write("0")