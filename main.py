from http.server import HTTPServer, BaseHTTPRequestHandler
import mimetypes
import pathlib
import urllib.parse
import socket
from multiprocessing import Process


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path

        # 1) Статика (css, картинки)
        if path == "/style.css" or path == "/logo.png":
            self.send_static(path.lstrip("/"))
            return

        # 2) HTML-сторінки
        if path == "/" or path == "/index.html":
            self.send_html("index.html")
        elif path in ("/message", "/message.html"):
            self.send_html("message.html")
        else:
            # усе інше — помилка 404
            self.send_html("error.html", status_code=404)

    def do_POST(self):
        """Обробка POST-запитів з форм."""
    
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        # Декодуємо в строку
        data_str = body.decode()
        # Розкодовуємо URL-encoding
        data_parsed = urllib.parse.unquote_plus(data_str)

        # Перетворюємо у словник
        data_dict = {
            key: value
            for key, value in (pair.split("=", 1) for pair in data_parsed.split("&"))
        }

        print("=== Received form data (HTTP) ===")
        print("raw:", body)
        print("parsed string:", data_parsed)
        print("dict:", data_dict)

        # Відправляємо дані на socket-сервер
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock_conn:
                sock_conn.connect(("127.0.0.1", 5000))
                sock_conn.sendall(body)
                print("Data sent to socket server")
        except ConnectionRefusedError:
            print("Socket server is not available on 127.0.0.1:5000")

        # Після обробки — редірект на головну
        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()

    def send_html(self, filename: str, status_code: int = 200):
        try:
            self.send_response(status_code)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            with open(filename, "rb") as f:
                self.wfile.write(f.read())
        except FileNotFoundError:
            self.send_response(500)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"Internal Server Error: file not found")

    def send_static(self, filename: str):
        """Відправка css / png та інших статичних файлів."""
        file_path = pathlib.Path(filename)
        if not file_path.exists():
            self.send_html("error.html", status_code=404)
            return

        mime_type, _ = mimetypes.guess_type(str(file_path))
        if not mime_type:
            mime_type = "application/octet-stream"

        self.send_response(200)
        self.send_header("Content-Type", mime_type)
        self.end_headers()

        with open(file_path, "rb") as f:
            self.wfile.write(f.read())


def start_http_server():
    """Запуск HTTP-сервера (в окремому процесі)."""
    server_address = ("", 3000) 
    httpd = HTTPServer(server_address, HttpHandler)
    print("HTTP server is running on http://localhost:3001")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("HTTP server stopped")
    finally:
        httpd.server_close()


def start_socket_server():
    """Запуск socket-сервера (інший процес)."""
    from socket_server import run_socket_server
    run_socket_server()


def main():
    http_process = Process(target=start_http_server)
    socket_process = Process(target=start_socket_server)

    http_process.start()
    socket_process.start()

    print("Both HTTP and socket servers started in separate processes.")

    try:
        http_process.join()
        socket_process.join()
    except KeyboardInterrupt:
        print("\nStopping servers...")
        http_process.terminate()
        socket_process.terminate()
        http_process.join()
        socket_process.join()
        print("Servers stopped.")


if __name__ == "__main__":
    main()
