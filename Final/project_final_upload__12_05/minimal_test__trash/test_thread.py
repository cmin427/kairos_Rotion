"""
시작-> 인스턴스 생성 -> 스레드 시작 -> q 입력 기다림 -> q 입력 -> 스레드 종료 -> 클래스 소멸자 발동 
"""

import time
import threading

class Server:
    def __init__(self):
        print("__init__")
        self.stop_flag=False
        
        self.thread = threading.Thread(target=self.background_task)
        self.thread.start()  # 서브 스레드 시작
        
        self.wait_for_quit()
        

    def wait_for_quit(self):
        """사용자 입력을 대기하며 'q' 입력 시 종료"""
        while not self.stop_flag:
            user_input = input("종료하려면 'q'를 입력하세요: ").strip().lower()
            if user_input == 'q':
                print("종료 신호 감지! 스레드를 종료합니다...")
                self.stop_flag = True
                break
        
    def __del__(self):
        print("__del__")
        self.thread.join
 
        
    def background_task(self):
        """서브 스레드 작업"""
        count = 0
        while not self.stop_flag:
            count += 1
            print(f"서브 스레드 실행 중... ({count})")
            time.sleep(1)  # 1초 대기

        



if __name__ == "__main__":
    sv=Server()
