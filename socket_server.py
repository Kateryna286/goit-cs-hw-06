import socket
import urllib.parse
from datetime import datetime
from pymongo import MongoClient
import os


HOST = "127.0.0.1"
PORT = 5000

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB_NAME", "messages_db")
COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME", "messages")


def run_socket_server():
    # Підключення до MongoDB
    try:
        mongo_client = MongoClient(MONGO_URI)
        db = mongo_client[DB_NAME]
        collection = db[COLLECTION_NAME]
        print(f"Connected to MongoDB at {MONGO_URI}, db='{DB_NAME}', collection='{COLLECTION_NAME}'")
    except Exception as e:
        print("Error connecting to MongoDB:", e)
        collection = None

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

                # 5) Зберігаємо в MongoDB
                if collection is not None:
                    try:
                        result = collection.insert_one(doc)
                        print(f"Inserted into MongoDB with _id={result.inserted_id}")
                    except Exception as e:
                        print("Error inserting document into MongoDB:", e)
                else:
                    print("MongoDB collection is not available, skipping save")


if __name__ == "__main__":
    run_socket_server()
