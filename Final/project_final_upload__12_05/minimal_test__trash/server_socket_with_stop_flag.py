import socket
import threading

class SocketServer:
    def __init__(self):
        # 한 고객의 주문 목록 리스트가 요소가됨, 리스트의 리스트
        self.customers_order_list = []
        self.is_running = True  # 서버 실행 상태 플래그
        self.socket_thread_init()

    def socket_thread_init(self):
        self.host = '127.0.0.1'
        self.port = 12345

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)  # 클라이언트 1개만 허용

        print(f"서버가 {self.host}:{self.port}에서 대기 중입니다...")

        # 스레드 시작
        self.server_thread = threading.Thread(target=self.accept_client)
        self.server_thread.daemon = True  # 데몬 스레드로 실행
        self.server_thread.start()

    def accept_client(self):
        try:
            self.conn, self.addr = self.server_socket.accept()
            print(f"클라이언트 {self.addr}와 연결되었습니다.")
            self.thread_listening_to_client()
        except Exception as e:
            print(f"클라이언트 연결 처리 중 에러: {e}")
        finally:
            self.close_sockets()

    def thread_listening_to_client(self):
        while self.is_running:  # 실행 상태 플래그 확인
            try:
                data = self.conn.recv(1024).decode()  # 1024 바이트까지 수신
                if not data or data.lower() == 'exit':
                    print("클라이언트와 연결 종료.")
                    break
                print(f"클라이언트: {data}")

                # 클라이언트로 메시지 전송
                response = input("서버: ")  # 서버에서 보낼 메시지 입력
                self.conn.send(response.encode())
            except Exception as e:
                print(f"데이터 처리 중 에러: {e}")
                break
        self.conn.close()

    def stop_server(self):
        """서버 종료 메서드"""
        print("서버 종료 중...")
        self.is_running = False  # 실행 상태 플래그 변경
        if self.conn:
            try:
                self.conn.close()  # 클라이언트 소켓 닫기
            except Exception as e:
                print(f"클라이언트 소켓 닫기 중 에러: {e}")
        if self.server_socket:
            try:
                self.server_socket.close()  # 서버 소켓 닫기
            except Exception as e:
                print(f"서버 소켓 닫기 중 에러: {e}")

    def close_sockets(self):
        """소켓 정리 메서드"""
        if self.conn:
            self.conn.close()
        if self.server_socket:
            self.server_socket.close()
        print("모든 소켓이 닫혔습니다.")


server = SocketServer()
server.stop_server()

