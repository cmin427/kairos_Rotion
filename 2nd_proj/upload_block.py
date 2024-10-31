from pymycobot.mycobot import MyCobot
import time

def move_arm(pos):
    mc.send_angles(pos, 30)
    time.sleep(3)

def move_gripper(flag,w=100):
    if flag == "OPEN":
        mc.set_eletric_gripper(1)
        mc.set_gripper_value(w,20)
    elif flag == "CLOSE":
        mc.set_eletric_gripper(0)
        mc.set_gripper_value(0,20)
    else:
        print("invalid")
    time.sleep(3)

cobot2_pos_pick1 = [-130,-5,-5,0,90,30]
cobot2_pos_pick2 = [-130,-70,-10,-5,90,50]
cobot2_pos_origin = [0,0,0,0,0,0]
cobot2_pos_drop1 = [90,0,0,0,-90,0]
cobot2_pos_drop2 = [90,20,28,40,-90,0]

mc = MyCobot('COM7',115200)
mc.set_gripper_calibration()
mc.set_gripper_mode(0)
mc.init_eletric_gripper()

move_arm(cobot2_pos_origin)
move_gripper("OPEN")

move_arm(cobot2_pos_pick1)

move_arm(cobot2_pos_pick2)
move_gripper("CLOSE")

move_arm(cobot2_pos_pick1)
move_arm(cobot2_pos_origin)

move_arm(cobot2_pos_drop1)
move_arm(cobot2_pos_drop2)
move_gripper("OPEN",80)
move_arm(cobot2_pos_drop1)
move_arm(cobot2_pos_origin)
print("done")
