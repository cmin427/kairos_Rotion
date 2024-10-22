#from softwareserial_original import softwareSerial
from softwareserial import softwareSerial
swser = softwareSerial(txd_pin = 17, rxd_pin=27, baudrate=9600, new="/n", eol="/n", timeout=15)
buffer =""
counter = 0
num = 1
while True:
    msg = swser.read()
    buffer += msg
    counter += 1
    
    if counter == 2:
        print(num , ". buffer:",buffer)
        num += 1
        buffer =""
        counter =0
    
