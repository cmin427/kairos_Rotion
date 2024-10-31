from pymycobot import MyCobot, MyCobotSocket
import time

mc = MyCobot("COM7",115200)
mc.set_ssid_pwd("ConnectValue_B401_2G","CVB401!@#$")
mc = MyCobotSocket("172.30.1.31",9000)
print(mc.get_angles())

import os
import sys

# Add relevant ranger module to PATH... there surely is a better way to do this...
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pymycobot import utils

port = utils.get_port_list()
print("ports: ",port)

detect_result = utils.detect_port_of_basic()
print(detect_result)

