import numpy as np
from pymycobot.myagv import MyAgv

mc = MyAgv('/dev/ttyAMA2', 115200)
# i = 0
mc.go_ahead(10, 10)
mc.stop()
mc.restore()
# while True:
#     if i < 101:
#         mc.go_ahead(10, 0.1)
#         print(f"i>0일 때, i 값 :{i}")
#         i += 1

#     if i == 101:
#         mc.stop()
#         mc.restore()
#         break
#     if i == 101:
#         mc.go_ahead(10, 10)
#         print(f"i=101일 때, i 값 :{i}")
#         mc.stop()
#         mc.restore()
#         break