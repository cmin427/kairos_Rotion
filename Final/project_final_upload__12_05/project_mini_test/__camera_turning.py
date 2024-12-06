import RPi.GPIO as GPIO #RPi.GPIO 라이브러리를 GPIO로 사용


from time import sleep 


class hallCamera:
    def __init__(self):
        self.servoPin          = 12   # 서보 핀
        self.SERVO_MAX_DUTY    = 12.5   # 서보의 최대(180도) 위치의 주기
        self.SERVO_MIN_DUTY    = 1.5    # 서보의 최소(0도) 위치의 주기

        GPIO.setmode(GPIO.BOARD)        # GPIO 설정
        GPIO.setup(self.servoPin, GPIO.OUT)  # 서보핀 출력으로 설정

        self.servo = GPIO.PWM(self.servoPin, 50)  # 서보핀을 PWM 모드 50Hz로 사용하기 (50Hz > 20ms)
        self.servo.start(0)  # 서보 PWM 시작 duty = 0, duty가 0이면 서보는 동작하지 않는다.

    def __setServoPos(self,degree):
            # 각도는 180도를 넘을 수 없다.
            if degree > 180:
                degree = 180

            if degree<0:
                degree=0

            # 각도(degree)를 duty로 변경한다.
            duty = self.SERVO_MIN_DUTY+(degree*(self.SERVO_MAX_DUTY-self.SERVO_MIN_DUTY)/180.0)
            # duty 값 출력
            # print("Degree: {} to {}(Duty)".format(degree, duty))

            GPIO.setup(self.servoPin, GPIO.OUT)
            # 변경된 duty값을 서보 pwm에 적용
            self.servo.ChangeDutyCycle(duty)
            sleep(0.3)
    def set_cam_direction(self,cam_direction):
        if cam_direction=="LEFT":
            self.__setServoPose(0)
            sleep(2)
        elif cam_direction=="RIGHT":
            self.__setServoPos(180)
            sleep(2)
        else:
            raise(ValueError("카메라 방향으로 잘못된 입력받음"))
           
           
hall=hallCamera() 
while True:
    hall.set_cam_direction("LEFT")
    hall.set_cam_direction("RIGHT")