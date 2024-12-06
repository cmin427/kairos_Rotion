import threading
import time
import signal

class MyServer:
    def __init__(self):
        # 전역 종료 플래그
        self.stop_flag = False

        # Ctrl+C 핸들러 등록
        signal.signal(signal.SIGINT, self.signal_handler)

        # 서브 스레드 시작
        self.thread = threading.Thread(target=self.background_task)
        self.thread.daemon=True
        self.thread.start()

    def background_task(self):
        """서브 스레드 작업"""
        count = 0
        while not self.stop_flag:
            print(self.stop_flag)
            count += 1
            print(f"서브 스레드 실행 중... ({count})")
            time.sleep(1)
        self.thread.join()  # 서브 스레드가 종료될 때까지 대기
        print("서브 스레드 종료 완료. 서버 종료.")

    def signal_handler(self, sig, frame):
        """Ctrl+C 시그널 핸들러"""
        print("\nCtrl+C 감지! 서버를 종료합니다...")
        self.stop_flag = True

    def wait_for_exit(self):
        """서버 종료를 기다림"""
        try:
            while not self.stop_flag:
                time.sleep(0.1)  # 메인 스레드 대기
        except Exception as e:
            print(f"메인 스레드 예외 발생: {e}")
        self.thread.join()  # 서브 스레드가 종료될 때까지 대기
        print("서브 스레드 종료 완료. 서버 종료.")


if __name__ == "__main__":
    server = MyServer()
    # server.wait_for_exit()
