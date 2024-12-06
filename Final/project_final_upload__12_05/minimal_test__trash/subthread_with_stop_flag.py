import time
import threading

stop_flag = False

def background_task_with_flag():
    global stop_flag
    count = 0
    while not stop_flag:
        count += 1
        print(f"서브 스레드 실행 중... ({count})")
        time.sleep(1)

def main_with_flag():
    global stop_flag
    thread = threading.Thread(target=background_task_with_flag)
    thread.start()

    time.sleep(3)
    print("메인 스레드에서 서브 스레드 종료 요청.")
    stop_flag = True
    thread.join()
    print("메인 스레드 종료!")

main_with_flag()
