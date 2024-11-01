import threading
import time
from pymycobot.myagv import MyAgv

def read_motor_current(mc):
    while mc.is_moving:  # is_moving이 True일 때만 전류를 읽음
        current_values = mc.get_motors_current()
        print(f'Motor currents: {current_values}')
        time.sleep(0.5)  # 0.5초마다 전류 값 읽기

# MyAgv 인스턴스 생성
mc = MyAgv('/dev/ttyAMA2', 115200)

# 모터가 움직이고 있는지 확인하기 위한 플래그
mc.is_moving = True

# 전류 읽기를 위한 스레드 시작
current_thread = threading.Thread(target=read_motor_current, args=(mc,))
current_thread.start()

# 모터 앞으로 이동
mc.go_ahead(1, 10)

# 모터가 이동하는 동안 다른 작업을 수행할 수 있음
time.sleep(10)  # 예를 들어 10초 동안 이동

# 모터 정지
mc.stop()
mc.is_moving = False  # 모터가 멈췄음을 표시

# 스레드 종료 대기
current_thread.join()

# 최종 전류 값 출력
final_current_values = mc.get_motors_current()
print(f'Final motor currents: {final_current_values}')

# 복원
mc.restore()
