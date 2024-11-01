from pymycobot.myagv import MyAgv

mc = MyAgv('/dev/ttyAMA2', 115200)

mc.pan_left(1, 10)

if ord('q'):
    mc.stop()
    mc.restore()  # AGV 동작 중지