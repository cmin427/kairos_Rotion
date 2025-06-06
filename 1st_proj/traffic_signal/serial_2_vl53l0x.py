# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import board
from digitalio import DigitalInOut
from adafruit_vl53l0x import VL53L0X
import serial

ser = serial.Serial(
        port='/dev/ttyAMA0', #Replace ttyS0 with ttyAM0 for Pi1,Pi2,Pi0
        baudrate = 9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS)
# declare the singleton variable for the default I2C bus
print("1")
i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller

print("2")
# declare the digital output pins connected to the "SHDN" pin on each VL53L0X sensor
xshut = [
    DigitalInOut(board.D17),
    DigitalInOut(board.D27),
    # add more VL53L0X sensors by defining their SHDN pins here
]

print("3")
for power_pin in xshut:
    # make sure these pins are a digital output, not a digital input
    power_pin.switch_to_output(value=False)
    # These pins are active when Low, meaning:
    #   if the output signal is LOW, then the VL53L0X sensor is off.
    #   if the output signal is HIGH, then the VL53L0X sensor is on.
# all VL53L0X sensors are now off

print("4")
# initialize a list to be used for the array of VL53L0X sensors
vl53 = []

print("5")
# now change the addresses of the VL53L0X sensors
for i, power_pin in enumerate(xshut):
    # turn on the VL53L0X to allow hardware check
    power_pin.value = True
    print("6")
    # instantiate the VL53L0X sensor on the I2C bus & insert it into the "vl53" list
    vl53.insert(i, VL53L0X(i2c))  # also performs VL53L0X hardware check
    print("7")
    # no need to change the address of the last VL53L0X sensor
   # if i < len(xshut) - 1:
        # default address is 0x29. Change that to something else
    vl53[i].set_address(i + 0x29)  # address assigned should NOT be already in use
   # print(i,power_pin)
    print("8")
# there is a helpful list of pre-designated I2C addresses for various I2C devices at
# https://learn.adafruit.com/i2c-addresses/the-list
# According to this list 0x30-0x34 are available, although the list may be incomplete.
# In the python REPR, you can scan for all I2C devices that are attached and detirmine
# their addresses using:
#   >>> import board
#   >>> i2c = board.I2C()
#   >>> if i2c.try_lock():
#   >>>     [hex(x) for x in i2c.scan()]
#   >>>     i2c.unlock()
print("for ends")
def detect_range(vl53):
    counter = 0
    while True:
        #data = ""
        #idx_alpabet = ["a","b"]
        data = "ff"
        #data = b'ff'
        for index, sensor in enumerate(vl53):
            try:
                if sensor.range < 100:
                    data = "ss"
                    #data = b'ff'
                    break
        #data = data.encode('utf-8')
        #data = bytes(data,'utf-8')
                
        #print(counter,": ",data.decode('utf-8'),data)
            except:
                pass
        ser.write(data.encode('utf-8'))
        print(counter,": ",data)
        counter += 1
        time.sleep(1)
    ser.close()
    
detect_range(vl53)