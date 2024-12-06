"""

아두이노와의 통신. 


아두이노가 먼저 avail을 보낸다. 

avail이 라즈베리파이에 제대로 들어왔을 시, abcd프로토콜로 각도를 보낸다. 

아두이노에서 데이터가 제대로 들어왔는지 확인한 후, 틀리면 invalid라고 보낸다. 이때는

라즈베리파이에서 같은 데이터를 재전송해주는걸 반복한다. 

틀리지 않으면 아두이노에서 데이터를 받아들이고 block이라고 보낸다. 

이때부터는 다시 avail이 들어오기 전까지 라즈베리파이에서 데이터를 보내지 않는다. 
"""

import serial
import time

# Serial communication setup via GPIO pin
ser = serial.Serial(
        port='/dev/ttyAMA3',
        baudrate=115200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
        )
time.sleep(2)  # Waiting for serial initialization

try:
    while True:
        # Step 1: Waiting for the 'avail' signal from Arduino.
        if ser.in_waiting > 0:
            incoming_data = ser.readline().decode().strip()
            if incoming_data == 'avail':
                print("Received 'avail' from Arduino.")

                # Step 2: Send 'abcde' message to Arduino.
                
                # Enter a user input
                user_input = input("Enter a message to send to Arduino (Form: 'a 100 b 80 c 80 d 50 e 110 f' Or exit when entering 'exit'): ")
                
                # if enter 'exit', finish program
                if user_input.lower() == 'exit':
                    print("Termination of program")
                    break

                # Encode a user input
                ser.write(user_input.encode())
                print(f"'{user_input}' Message sent to Arduino.")
                
                while True:
                    if ser.in_waiting > 0:
                        incoming_data = ser.readline().decode().strip()
                        print("Received a 'invalid' message from Arduino.")

                        if incoming_data == 'invalid':
                            ser.write(user_input.encode())
                            print('old input', user_input.encode())
                            time.sleep(0.1)

                        else:
                            break

                    else:
                        time.sleep(0.1)
                        
                # Step 3: wait for 'block' message from Arduino
                while True:
                    if ser.in_waiting > 0:
                        block_data = ser.readline().decode().strip()
                        if block_data == 'block':
                            print("Received a 'block' message from Arduino.")
                            break
                # Step 4: Wait for 'avail' message
                print("Waiting for 'avail'...")

except KeyboardInterrupt:
    print("Termination of communication")
finally:
    ser.close()
