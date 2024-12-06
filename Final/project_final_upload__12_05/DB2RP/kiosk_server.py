import socket
import json
import sys
import sqlite3
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import threading
import os

# 서버 IP 주소와 포트 설정 (서버가 실행되는 Raspberry Pi의 IP 주소를 입력)
server_ip = '172.30.1.57'
server_port = 9999
# 소켓 생성 및 연결
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # 클라이언트 한개만 붙는 소켓이라고 최적화
server_socket.bind((server_ip,server_port))
server_socket.listen() # 클라이언트 1개만 허용
print(f"서버가 {server_ip}:{server_port}에서 대기 중입니다...")

conn, addr = server_socket.accept()
print(f"클라이언트 {addr}와 연결되었습니다.")




ID_file="pass_id.txt"

if not os.path.exists(ID_file):
    with open(ID_file, 'x') as f:
        f.write("")
else:
    with open(ID_file,"w") as f:
        f.write("")

def thread_IDfile_reading(kiosk): #데몬으로 설정하기 
    while True:
        with open(ID_file,"r") as f:
            txt_received=f.read()
        
        if txt_received !="": # 228 등 
            goods_id=int(txt_received)
            kiosk.current_buying_item_id =goods_id    
            kiosk.selected_item(goods_id)
            with open(ID_file,"w") as f:
                f.write("")
            


def find_index_by_id(db, n):
    for index, row in enumerate(db):
        if row[0] == n:  # 첫 번째 값이 id
            return index
    return -1  # id=n인 행이 없을 경우 -1 반환

def copy_4th_to_5th_column(db):
    for row in db:
        if len(row) > 5:  # 4번째와 5번째 인덱스가 있는지 확인
            row[6] = row[5]  # 4번째 인덱스 값을 5번째 인덱스로 복사
    return db

def reset_4th_and_5th_columns(db):
    for row in db:
        row[5] = 0    # 4번째 인덱스를 0으로 설정
        row[6] = 0    # 5번째 인덱스를 0으로 설정
    return db

class Kiosk(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("Kiosk.ui", self)  # Qt Designer로 만든 UI 파일 로드
        
        # 항목별 이미지 경로, 기본 이미지 설정
        self.default_path = "Design_Pictures/QR.png"
        self.item_images = {
            228: "Design_Pictures/1_립스틱.png",
            719: "Design_Pictures/2_립밤.jpg",
            1002: "Design_Pictures/3_향수.jpg"
        }

        # 데이터베이스 초기화 및 항목 로드
        self.db_in_python = [] # 파이썬 안에 있는 DB
        self.db_send_to_Changryong = [] # 창룡이한테 보내는 DB
        self.current_buying_item_id = None # DB에 저장된 id를 저장하는 변수

        self.init_db()
        self.first_load_items_from_db()
        self.re_load_items_from_db()

        '''
        UI 요소 연결
        '''
        # 여러개의 Page들을 찾아서 설정
        self.stacked_widget = self.findChild(QStackedWidget, "stackedWidget")

        # Page 1
        self.page1.mousePressEvent = lambda event: self.show_page(1)
        
        # Page 2
        self.reset_button = self.findChild(QPushButton, "reset_button") # 초기화 버튼
        self.quantity_display = self.findChild(QLabel, "quantity_display") # 수량
        self.image_display = self.findChild(QLabel, "image_display") # QR을 인식시키면 나오는 그림
        
        self.up_button = self.findChild(QToolButton, "up_button") # 수량 증가 버튼
        self.down_button = self.findChild(QToolButton, "down_button") # 수량 감소 버튼
        self.add_item_button = self.findChild(QPushButton, "add_item_button") # 항목 추가 구매 버튼
        self.move_order_button = self.findChild(QPushButton, "move_order_button") # 결제 페이지로 이동 하는 버튼 추가

        # 버튼 클릭 시 호출할 함수 연결
        self.reset_button.clicked.connect(self.reset)
        self.go_page2_button.clicked.connect(self.reset)  # Page 3로 이동하도록 설정
        self.up_button.clicked.connect(self.increment_number) # 수량 증가
        self.down_button.clicked.connect(self.decrement_number) # 수량 감소
        self.add_item_button.clicked.connect(self.save_selection) # 변수 저장
        self.move_order_button.clicked.connect(self.save_and_move_order)  # 결제 페이지로 이동

        # self.update_quantity_display(id) # 사고자 하는 항목의 수량이 몇개인지 표현

        # Page 3
        self.go_page2_button = self.findChild(QPushButton, "go_page2_button") # 이전 페이지로 이동
        self.complete_pay_button = self.findChild(QPushButton, "complete_pay_button") # 결제완료 버튼을 누르면 현재값들을 저장하고 다음 page로 이동

        # 버튼 클릭 시 호출할 함수 연결
        self.go_page2_button.clicked.connect(lambda: self.show_page(1))  # Page 3로 이동하도록 설정
        self.complete_pay_button.clicked.connect(self.complete_pay)
        
        # QLabel을 연결해 물품명과 수량을 각각 표시
        self.item_labels = []
        self.quantity_labels = []
        self.price_labels = []

        # 3개 항목에 대한 QLabel 설정
        for i in range(3):
            self.item_labels.append(self.findChild(QLabel, f"item_label_{i + 1}"))
            self.quantity_labels.append(self.findChild(QLabel, f"quantity_label_{i + 1}"))
            self.price_labels.append(self.findChild(QLabel, f"price_label_{i + 1}"))

        # 합계 레이블 추가
        self.total_label = self.findChild(QLabel, "total_label") # 총합을 표시할 QLabel
        
        # 초기 물품 및 수량 표시 업데이트
        # self.update_saved_list(id) # 영수증에 현재 사고하는 항목에 대한 정보들을 업데이트
        
        # Page 4
        self.waiting_new_customer_button = self.findChild(QPushButton, "new_customer_button") # 초기화 버튼
        # 함수
        self.waiting_new_customer_button.clicked.connect(self.waiting_new_customer)

    '''
    함수 설정
    '''
    def init_db(self):
        """SQLite 데이터베이스 초기화"""
        self.conn = sqlite3.connect("rotion")  # 데이터베이스 경로 수정
        self.cursor = self.conn.cursor()

    def first_load_items_from_db(self):
        """DB에서 항목 정보를 불러와서 item_quantities에 저장"""
        self.cursor.execute("SELECT id, name, quantity, price, location FROM cosmetic")
        
        for row in self.cursor.fetchall():
            # 기존 row에 구매수량 0을 추가하여 새로운 튜플로 생성
            row_with_purchase_quantity = row + (0, 0)  # (id, name, quantity, price, location, 구매수량, 진짜 구매수량)
            row_with_purchase_quantity = list(row_with_purchase_quantity)
            self.db_in_python.append(row_with_purchase_quantity)
    
    def re_load_items_from_db(self):
        # 기존 데이터를 지우고 다시 로드할 준비
        self.db_in_python.clear()

        # 데이터베이스에서 데이터 로드
        self.cursor.execute("SELECT id, name, quantity, price, location FROM cosmetic")
        
        for row in self.cursor.fetchall():
            # 기존 row에 구매수량 0을 추가하여 새로운 튜플로 생성
            row_with_purchase_quantity = row + (0, 0)  # (id, name, quantity, price, location, 구매수량, 진짜 구매수량)
            row_with_purchase_quantity = list(row_with_purchase_quantity)
            self.db_in_python.append(row_with_purchase_quantity)
            print(self.db_in_python)
        
    def save_to_db(self):
        """현재 db_in_python 정보를 DB에 저장"""
        for (id, name, stock, price, customer_buy, real_customer_buy, location) in self.db_in_python:
            updated_quantity = stock - real_customer_buy
            self.cursor.execute(
                "UPDATE cosmetic SET quantity = ? WHERE id = ?",
                (updated_quantity, id)
            )
        self.conn.commit()
        reset_4th_and_5th_columns(self.db_in_python)
    
    def closeEvent(self, event):
        """앱 종료 시 DB에 저장하고 연결 종료"""
        self.save_to_db()
        self.conn.close()
        event.accept()

    def show_page(self, page_index):
        """페이지 전환 메서드"""
        self.stacked_widget.setCurrentIndex(page_index)

    def keyPressEvent(self, event):
        """키보드로 물품을 선택하고 이미지를 업데이트 -> QR 인식 시켜서 해보기""" 
        if event.key() == Qt.Key_1:
            self.current_buying_item_id = 228
            self.selected_item(228)
            
        elif event.key() == Qt.Key_2:
            self.current_buying_item_id = 719
            self.selected_item(719)
            
        elif event.key() == Qt.Key_3:
            self.current_buying_item_id = 1002
            self.selected_item(1002)

    def sendDataToChangryong(self, db_send_to_Changryong):
        # 데이터 직렬화 (JSON 문자열로 변환)
        try:
            serialized_data = json.dumps(db_send_to_Changryong)
            print("Serialized data to send:", serialized_data)
        except Exception as e:
            print("JSON 직렬화 오류:", e)
            return

        
        try:
           
            
            # 데이터 전송
            conn.sendall(serialized_data.encode())
            print("데이터를 전송했습니다:", serialized_data)
 
        except ConnectionResetError as ex:
            print("현재 연결은 원격 호스트에 의해 강제로 끊겼습니다. 서버 소켓을 해제하고 시스템 종료.")
            conn.close()
            sys.exit(1)
                
    
    def reset(self, index):
        """초기 상태로 모든 값을 초기화"""

        # 항목별 수량 초기화
        for i in range(len(self.db_in_python)):
            self.db_in_python[i][5] = 0
            
        copy_4th_to_5th_column(self.db_in_python)
        
        # 이미지를 기본 상태로 초기화
        self.display_image(self.default_path)

        # 수량 표시 초기화
        self.update_quantity_display(index)

        copy_4th_to_5th_column(self.db_in_python)
        
        # 저장된 리스트 초기화
        self.update_saved_list()
    
    def selected_item(self, id):
        """항목을 선택하고 이미지 및 수량을 업데이트"""
        index_id = find_index_by_id(self.db_in_python, id)
        self.current_quantity = self.db_in_python[index_id][6]
        self.display_image(self.item_images[id])
        self.update_quantity_display(index_id)

    def display_image(self, image_path):
        """항목 이미지를 QLabel에 표시"""
        pixmap = QPixmap(image_path)
        self.image_display.setPixmap(pixmap)
        self.image_display.setScaledContents(True)
    
    def increment_number(self):
        """현재 선택된 항목의 수량을 1 증가"""
        index = find_index_by_id(self.db_in_python, self.current_buying_item_id)
        self.db_in_python[index][5] += 1
        self.update_quantity_display(index)

    def decrement_number(self):
        """현재 선택된 항목의 수량을 1 감소하며, 0 미만으로 내려가지 않음"""
        index = find_index_by_id(self.db_in_python, self.current_buying_item_id)
        
        if self.db_in_python[index][5] > 0:
            self.db_in_python[index][5] -= 1
        self.update_quantity_display(index)

    def save_selection(self, id):
        """선택한 물품과 수량을 저장하고 초기화"""
        # self.save_to_db()  # 변경된 수량 DB에 저장
        copy_4th_to_5th_column(self.db_in_python)
        print('select_4to5', self.db_in_python)
        self.display_image(self.default_path)
        self.quantity_display.setText(str(0)) # PyQT에서 보여지는 숫자를 0으로 만들기

    def save_and_move_order(self):
        """결제 페이지로 이동 시 현재 상태 저장"""
        # self.save_to_db()  # 변경된 수량 DB에 저장
        copy_4th_to_5th_column(self.db_in_python)
        print('move_odre', self.db_in_python)
        self.display_image(self.default_path)
        self.update_saved_list()
        self.show_page(2)

    def update_quantity_display(self, index):
        """수량을 QLabel에 표시"""
        self.quantity_display.setText(str(self.db_in_python[index][5]))

    def complete_pay(self):
        print("Starting complete_pay function.")
        print("Initial db_send_to_Changryong:", self.db_send_to_Changryong)
        
        self.save_to_db()  # 변경된 수량 DB에 저장
        
        # sendDataToChangryong 함수 호출
        if self.db_send_to_Changryong:
            self.sendDataToChangryong(self.db_send_to_Changryong)
        else:
            print("Error: db_send_to_Changryong is empty or None.")
        
        print('db_send_to_Ch:', self.db_send_to_Changryong)
        print('pre_complete_pay:', self.db_in_python)
        
        # 기존 데이터를 지우고 다시 로드할 준비
        self.db_in_python.clear()
        print('clear_complete_pay:', self.db_in_python)
        
        # Page 4로 이동하도록 설정
        self.show_page(3)
        
    
    def update_saved_list(self):
        """세 번째 페이지에 물품명, 수량, 금액을 각각의 QLabel로 표시"""
        items = [row[1] for row in self.db_in_python]
        quantities = [row[6] for row in self.db_in_python]
        prices = [row[3] for row in self.db_in_python]
        locations = [row[4] for row in self.db_in_python]
        
        # 수량이 0보다 큰 항목 필터링
        non_zero_items = [(item, qty, price, location) for item, qty, price, location in zip(items, quantities, prices, locations) if qty > 0]
        
        print('non_zero', non_zero_items)
        total_sum = 0
        
        # db_send_to_Changryong 리스트 초기화
        self.db_send_to_Changryong = []
        
        for idx in range(len(self.db_in_python)):  # Here, we use idx instead of id
            if idx < len(non_zero_items):
                item_name, item_quantity, item_price, item_location = non_zero_items[idx]
                
                # (item, qty) 추가
                self.db_send_to_Changryong.append((item_quantity, item_location))
                
                # 계산 및 QLabel 업데이트
                sub_total_price = item_quantity * item_price  # 현재 사고자 하는 수량 * 가격
                
                self.item_labels[idx].setText(item_name)
                self.quantity_labels[idx].setText(str(item_quantity))
                self.price_labels[idx].setText(str(sub_total_price))
                
                total_sum += sub_total_price
                
                self.item_labels[idx].show()
                self.quantity_labels[idx].show()
                self.price_labels[idx].show()
            else:
                self.item_labels[idx].hide()
                self.quantity_labels[idx].hide()
                self.price_labels[idx].hide()

        # db_send_to_Changryong 확인용 출력
        print(f"db_send_to_Changryong 리스트: {self.db_send_to_Changryong}")

        # 총합 업데이트
        self.total_label.setText(f"{total_sum:,}")
        self.total_label.show()

    
    def waiting_new_customer(self, index):
        # reset_4th_and_5th_columns(self.db_in_python)
        print('new_customer', self.db_in_python)
        self.show_page(0)
        self.re_load_items_from_db()
        print('reload', self.db_in_python)
        self.quantity_display.setText(str(0))
        
    def show_page(self, page_index):
        """페이지 전환 메서드"""
        self.stacked_widget.setCurrentIndex(page_index)

if __name__ == "__main__":
    
    
    app = QApplication(sys.argv)
    window = Kiosk()
    th_id=threading.Thread(target=thread_IDfile_reading,args=(window,))
    th_id.daemon=True
    
    window.show()
    th_id.start()
    
    sys.exit(app.exec_())
