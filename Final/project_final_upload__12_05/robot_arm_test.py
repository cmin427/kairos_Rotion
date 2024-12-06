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
while True:
    in1=input("base:")
    in2=input("sholder:")
    in3=input("elbow:")
    in4=input("wrist:")
    in5=input("finger:")
    arm.set_robot_arm_angle(base=int(in1),shoulder=int(in2),elbow=int(in3),wrist=int(in4),finger=int(in5))