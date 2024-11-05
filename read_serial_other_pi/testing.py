#from softwareserial_original import softwareSerial
# from softwareserial import softwareSerial
from softwareserial2 import softwareSerial
import time

swser = softwareSerial(txd_pin = 17, rxd_pin=27, baudrate=9600,new=" ",eol=" ")
counter = 0
buffer =""
num = 1
while True:
    msg = swser.read()
    #swser.read()


    if msg:
        buffer += msg
        counter += 1
    
    if counter == 2:
        print(num , ". received:",buffer)
        num += 1
        buffer =""
        counter =0
    # time.sleep(1)
    
