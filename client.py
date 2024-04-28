import socket
import threading
import pymongo
import datetime
import uuid
import sys

try:
    mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = mongo_client["chat_db"]
    collection = db["messages"]
    print("Connected to MongoDB!")
except pymongo.errors.ConnectionFailure as e:
    print(f"Could not connect to MongoDB: {e}")
    sys.exit(1)

nickname = input("Choose a nickname: ")
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('127.0.0.1', 55555))
client_socket.settimeout(1.0)

running = threading.Event()
running.set()

def receive():
    while running.is_set():
        try:
            message = client_socket.recv(1024).decode('ascii')
            if message == 'NICK':
                client_socket.send(nickname.encode('ascii'))
            else:
                print(message)
        except socket.timeout:
            continue
        except Exception as e:
            print("An error occurred!", e)
            break

def write():
    while running.is_set():
        try:
            message = input()
            if message.lower() == 'exit*':
                print("Exiting chat...")
                running.clear()
                break
            full_message = f'{nickname}: {message}'
            client_socket.send(full_message.encode('ascii'))
            message_id = str(uuid.uuid4())
            message_data = {
                "message_id": message_id,
                "sender": nickname,
                "time": datetime.datetime.now(),
                "message": full_message
            }
            collection.insert_one(message_data)
        except Exception as e:
            print("Failed to send message", e)
            running.clear()
            break

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()

write_thread.join()
receive_thread.join()

client_socket.close()
#mongo_client.close()
sys.exit(0)
