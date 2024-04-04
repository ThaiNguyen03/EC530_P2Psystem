
import socket
import threading
import pymongo
import datetime
import uuid

db_client = pymongo.MongoClient("mongodb://localhost:27017")
db = db_client["chat_db"]
collection = db["messages"]
nickname = input("Choose a nickname: ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 55555))


def receive():
    while True:
        try:
            message = client.recv(1024).decode('ascii')
            if message == 'NICK':
                client.send(nickname.encode('ascii'))
            else:
                print(message)
        except:
            print("An error occurred!")
            client.close()
            break


def write():
    while True:
        message = f'{nickname}: {input("")}'
        client.send(message.encode('ascii'))
        message_id = str(uuid.uuid4())
        message_data = {
            "message_id": message_id,
            "sender": nickname,
            "time": datetime.datetime.now(),
            "message": message

        }
        collection.insert_one(message_data)


receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
