import pigpio
import logging
import time

class softwareSerial():
    def __init__(self, txd_pin, rxd_pin, baudrate, timeout=15, new="/n", eol="/n"):
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)

        self.txd = txd_pin
        self.rxd = rxd_pin
        self.baudrate = baudrate
        self.timeout = timeout
        self.new = new
        self.eol = eol

        self.logger.info("Initializing pigpio...")
        self.pigpio = pigpio.pi()

        if not self.pigpio.connected:
            self.logger.critical("Pigpio daemon not started! Start with: `sudo pigpiod`. Exiting...")
            exit()

        self.logger.info("Initializing pins...")

        self.pigpio.set_mode(self.txd, pigpio.OUTPUT)
        self.pigpio.set_mode(self.rxd, pigpio.INPUT)

        pigpio.exceptions = False
        self.pigpio.bb_serial_read_close(self.rxd)
        
        pigpio.exceptions = True
        
        self.pigpio.bb_serial_read_open(self.rxd, self.baudrate)

    def write(self, message):
        self.logger.debug("Clearing wave...")
        self.pigpio.wave_clear()
        self.logger.debug("Creating message and connection...")
        self.pigpio.wave_add_serial(self.txd, self.baudrate, str(f"{message}\n").encode())
        self.logger.debug("Creating wave...")
        wave = self.pigpio.wave_create()
        self.logger.debug("Sending data...")
        self.pigpio.wave_send_once(wave)
        while self.pigpio.wave_tx_busy():
            pass
        self.logger.debug("Deleting wave...")
        self.pigpio.wave_delete(wave)

    def read(self):
        try:
            
            start = time.perf_counter()
            while round((time.perf_counter() - start), 2) < self.timeout:
                final_string = ""
                (byte_count, data) = self.pigpio.bb_serial_read(self.rxd)
                if data:
                    #print("01:",type(data))
                    #print("02:",data,data[0])
                    try:
                        #pass
                        final_string += data.decode()
                        #print("1: ", final_string)
                    except UnicodeDecodeError:
                        final_string += "".join([chr(b) for b in data])
                        print("2: ", final_string)

                    #final_string = final_string + data
                    #print("3: ", final_string)
                    #print("final_string.find(self.new) :",final_string.find(self.new))
                    if final_string.find(self.new) != -1:
                        while int(byte_count) > 0:
                            (byte_count, data) = self.pigpio.bb_serial_read(self.rxd)
                            
                            try:
                                final_string += data.decode("utf-8")
                                print("4: ", final_string)
                            except AttributeError:                                
                                print("5: ", final_string)
                                pass

                            final_string = final_string + data
                            print("6: ", final_string)

                            if final_string.find(self.eol) != -1:
                                final_string = final_string.strip(self.new)
                                final_string = final_string.strip(self.eol)
                                print("7: ", final_string)
                                return final_string
                    #print("8: ", final_string)
                    return final_string
            self.logger.warning("Timeout reached!")
            print("9: ", final_string)
            return final_string
        except Exception as e:
            self.logger.error(f"Failed to get data, error: {e}")

if __name__ == "__main__":
    serial = softwareSerial(17, 27, 9600)

    while True:
        read = serial.read()
        
        if read != None:
            if read.find("ping") != -1:
                serial.write("pong")
