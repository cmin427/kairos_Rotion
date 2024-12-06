from robot_module.robotParts import AGV_PositionController, SocketManagerToKiosk,RobotArmController,CameraManager,ArucoDetector,SocketManagerToCobot
import time

kiosk=SocketManagerToKiosk()

cur_list=kiosk.customers_order_list

print("current order list: ",cur_list)

while True:
    if cur_list != kiosk.customers_order_list:
        cur_list = kiosk.customers_order_list
        print(cur_list)
    
        
    time.sleep(0.5)
    
    
