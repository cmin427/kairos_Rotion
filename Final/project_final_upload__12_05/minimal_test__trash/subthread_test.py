import threading
import time

def background_task():
    """서브 스레드 작업"""
    count = 0
    while True:
        count += 1
        print(f"서브 스레드 실행 중... ({count})")
        time.sleep(1)  # 1초 대기

# 메인 스레드에서 서브 스레드 시작
def main():
    print("메인 스레드 시작.")
    thread = threading.Thread(target=background_task)
    thread.start()  # 서브 스레드 시작

    print("메인 스레드 작업 완료 후 종료.")
    time.sleep(3)  # 메인 스레드 작업
    print("메인 스레드 종료!")

if __name__ == "__main__":
    main()
