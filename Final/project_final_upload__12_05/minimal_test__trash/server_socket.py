import socket
import threading

def server_thread(host='127.0.0.1', port=12345):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"서버가 {host}:{port}에서 실행 중입니다...")

    try:
        while True:
            conn, addr = server_socket.accept()
            print(f"클라이언트 {addr} 연결됨.")
            handle_client(conn, addr)  # 클라이언트 연결 처리
    except Exception as e:
        print(f"서버 에러: {e}")
    finally:
        server_socket.close()
        print("서버 소켓이 닫혔습니다.")

def handle_client(conn, addr):
    try:
        while True:
            data = conn.recv(1024).decode()
            if not data or data.lower() == 'exit':
                print(f"클라이언트 {addr} 연결 종료.")
                break
            print(f"클라이언트 {addr}: {data}")
            conn.send(f"서버 응답: {data}".encode())
    except Exception as e:
        print(f"클라이언트 {addr} 처리 중 에러: {e}")
    finally:
        conn.close()
        print(f"클라이언트 {addr} 소켓이 닫혔습니다.")

# 데몬 스레드로 서버 시작
def start_server_in_thread():
    server_thread_instance = threading.Thread(target=server_thread, daemon=True)
    server_thread_instance.start()
    print("데몬 스레드에서 서버 시작됨.")

if __name__ == "__main__":
    start_server_in_thread()
    input("서버 실행 중. 종료하려면 Enter를 누르세요...\n")
