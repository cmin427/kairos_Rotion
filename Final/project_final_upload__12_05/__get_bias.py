from robot_module.robotParts import CameraManager

cam=CameraManager()

while True:
 if cam.is_aruco_detected(101):
    print(cam.get_bias_of_aruco(101))
    