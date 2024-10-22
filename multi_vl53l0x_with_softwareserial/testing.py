from softwareserial_original import softwareSerial
#from softwareserial import softwareSerial
swser = softwareSerial(txd_pin = 17, rxd_pin=27, baudrate=9600, new="/n", eol="/n", timeout=15)
msg = 0
counter = 0
while(counter < 1):
    #ser.write("hello")
    #print("write")
    msg = swser.read()
    #if msg is not None:
     #   print("read")
    print("msg:",msg)
    counter += 1
