import time


class WareDragon:
    def __init__(self):
        
        self.stop_flag=False
        
        self.kiosk=SocketManagerToKiosk()
     
        
        
        
        
        
    
    def wait_for_stop_flag(self): # q 누르면 각 파츠가 정지할 수 있게끔 main 마지막에서 호출하는 함수 
        while not self.stop_flag:
            user_input = input("종료하려면 'q'를 입력하세요: ").strip().lower()
            if user_input == 'q':
                print("종료 신호 감지. 창룡 모든 파트 정지.")
                self.kiosk.stop_flag = True
                self.agv.stop_flag=True
                self.robotArm.stop_flag=True
                self.camera.stop_flag=True
                
                break
            
    
    def main_process(self):
        kiosk=self.kiosk
        while True:
            self.kiosk.cnt+=1
            kiosk.cnt+=1
            print(self.kiosk.cnt)
            time.sleep(1)
            
class SocketManagerToKiosk:
    def __init__(self):
        self.cnt=0

wd=WareDragon()
wd.main_process()