import threading
import time

def count(n):
    for i in range(n):
        print(i)
        time.sleep(1)  # 1초마다 출력

if __name__ == "__main__":
    t1 = threading.Thread(target=count, args=(10,))
    t2 = threading.Thread(target=count, args=(5,))

    t1.start()
    t2.start()

    t1.join()
    t2.join()