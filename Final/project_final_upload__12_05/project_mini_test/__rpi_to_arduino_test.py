import serial
import time

ser=serial.Serial(port='/dev/ttyAMA3',
            baudrate=115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1) 

time.sleep(2)
ser.flushInput()
ser.flushOutput()
user_input=input("Enter a message to send to Arduino (Form: 'a100b80c80d50e110f'): ")

ser.write(user_input.encode())



   
# 아두이노가 응답 없는 경우 대기

    
while ser.in_waiting==0:
    time.sleep(0.01)
    
received=ser.readline().decode().strip()
print(received)



        
        