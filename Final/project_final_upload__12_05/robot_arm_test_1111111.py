from robot_module.robotParts import SerialUtils,RobotArmController
import serial
import time
# ser = serial.Serial(
#         port='/dev/ttyAMA4',
#         baudrate=9600,
#         parity=serial.PARITY_NONE,
#         stopbits=serial.STOPBITS_ONE,
#         bytesize=serial.EIGHTBITS,
#         timeout=1
#         )
# time.sleep(2)
# while True:
#     while ser.in_waiting==0:
#         time.sleep(1)
#     print("something received")
#     incoming_data = ser.readline()
#     print("in:",incoming_data.decode().strip())
arm=RobotArmController()


arm.pick_target_goods()

# arm.set_robot_arm_angle(base=45,shoulder=70,elbow=125,wrist=70,finger=180)
# while True:
#     arm.setGripperOpen()    
#     arm.setGripperClosed()
# arm.set_robot_arm_angle(base=45,shoulder=70,elbow=125,wrist=70,finger=180)
# arm.setGripperClosed()
# arm.set_robot_arm_angle(base=45,shoulder=120,elbow=160,wrist=70,finger=0)
# while True:
#     # in1=input("base:")
#     # in2=input("sholder:")
#     in3=input("elbow:")
#     # in4=input("wrist:")
#     # in5=input("finger:")
#     arm.set_robot_arm_angle(base=45,shoulder=70,elbow=int(in3),wrist=70,finger=180)
#     # base=140,shoulder=150,elbow=180,wrist=70,finger=180
#     # base=45,shoulder=70,elbow=125,wrist=70,finger=180