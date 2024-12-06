from pymycobot import MyCobot320
import time

def move_arm(pos):
    mc.sync_send_angles(pos, 60)
    time.sleep(1)

def move_gripper(flag,w=100):
    if flag == "OPEN":
        mc.set_eletric_gripper(1)
        mc.set_gripper_value(w,50)
    elif flag == "CLOSE":
        mc.set_eletric_gripper(0)
        mc.set_gripper_value(0,50)
    else:
        print("invalid")
    time.sleep(1)

cobot2_pos_pick1 = [-130,-5,-5,0,90,30]
cobot2_pos_pick2 = [-130,-70,-10,-5,90,50]
cobot2_pos_origin = [0,0,0,0,0,0]
cobot2_pos_drop1 = [90,0,0,0,-90,0]
cobot2_pos_drop2 = [90,20,28,40,-90,0]

mc = MyCobot320('COM7',115200)
mc.set_eletric_gripper(1)
mc.set_gripper_value(100,20)
print('gripper test')
time.sleep(2)

mc.set_gripper_calibration()
mc.set_gripper_mode(0)
mc.init_eletric_gripper()
time.sleep(2)

mc.set_eletric_gripper(0)
mc.set_gripper_value(0,20)
print('.')
time.sleep(2)

mc.set_eletric_gripper(1)
mc.set_gripper_value(100,20)
print('..')
time.sleep(2)
move_arm(cobot2_pos_origin)
move_gripper("OPEN",80)
move_arm(cobot2_pos_pick1)
move_arm(cobot2_pos_pick2)
move_gripper("CLOSE")
move_arm(cobot2_pos_pick1)
move_arm(cobot2_pos_origin)
move_arm(cobot2_pos_drop1)
move_arm(cobot2_pos_drop2)
cnt = 1
while True: # open - dr1 - <>ori - open - p1 - p2 - close - p1 - ori - dr1 - dr2 - 
    a = input("press any key: ")
    if a == "l":
        print("last block")
        move_gripper("OPEN",80)
        move_arm(cobot2_pos_drop1)
        move_arm(cobot2_pos_origin)
        break
    elif a:
        print(f"block {cnt} goes")
        move_gripper("OPEN",80)
        move_arm(cobot2_pos_drop1)
        move_arm(cobot2_pos_origin)
        move_arm(cobot2_pos_pick1)
        move_arm(cobot2_pos_pick2)
        move_gripper("CLOSE")
        move_arm(cobot2_pos_pick1)
        move_arm(cobot2_pos_origin)
        move_arm(cobot2_pos_drop1)
        move_arm(cobot2_pos_drop2)
        print(cnt,": done")
        cnt += 1
    else:
        print("recommand!")
    if cnt > 10:
        break
print("Fin")
move_gripper("OPEN",80)