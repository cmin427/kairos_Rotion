from robot_module.robotParts import CameraManager
import msvcrt
import time


cam=CameraManager()

print("cam init done")

time.sleep(5)
print("s")

cam.close()

print('d')