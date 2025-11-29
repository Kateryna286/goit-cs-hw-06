import socket
import urllib.parse
from datetime import datetime


HOST = "127.0.0.1"
PORT = 5000


def run_socket_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(1)
        print(f"Socket server is running on {HOST}:{PORT}")

        while True:
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")
                data = conn.recv(1024)
                if not data:
                    continue

                print(f"Raw bytes from client: {data!r}")

                # 1) декодуємо байти в строку
                data_str = data.decode()
                # 2) розкодовуємо URL-encoding
                data_parsed = urllib.parse.unquote_plus(data_str)
                # 3) перетворюємо у словник
                data_dict = {
                    key: value
                    for key, value in (
                        pair.split("=", 1) for pair in data_parsed.split("&")
                    )
                }

                # 4) формуємо документ з датою
                doc = {
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                    "username": data_dict.get("username"),
                    "message": data_dict.get("message"),
                }

                print("=== Parsed message (socket server) ===")
                print(doc)


if __name__ == "__main__":
    run_socket_server()
