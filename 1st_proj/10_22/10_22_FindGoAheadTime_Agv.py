
from pymycobot.myagv import MyAgv

mc = MyAgv('/dev/ttyAMA2', 115200)

mc.go_ahead(1, 3)

if ord('q'):
    mc.stop()
    mc.restore()  # AGV 동작 중지