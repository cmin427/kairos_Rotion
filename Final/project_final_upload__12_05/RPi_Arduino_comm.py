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
