import socket
import threading
from queue import Queue

class Server:
    def __init__(self, host='127.0.0.1', port=55555):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen()
        self.clients = []
        self.nicknames = []
        self.message_buffer = Queue()  # Message buffer for synchronization

    def broadcast(self, message, exclude=None):
        if exclude is not None:
            for client in self.clients:
                if client != exclude:
                    try:
                        client.send(message)
                    except:
                        pass  # Handle error or removal of client
        else:
            for client in self.clients:
                try:
                    client.send(message)
                except:
                    pass  # Handle error or removal of client

        # Empty the buffer and send to the newly connected client if exclude is specified
        if exclude:
            while not self.message_buffer.empty():
                message = self.message_buffer.get()
                try:
                    exclude.send(message)
                except:
                    pass  # Handle error

    def handle(self, client):
        while True:
            try:
                message = client.recv(1024)
                self.broadcast(message)
                self.message_buffer.put(message)  # Add incoming messages to buffer
            except:
                index = self.clients.index(client)
                self.clients.remove(client)
                client.close()
                nickname = self.nicknames[index]
                self.nicknames.remove(nickname)
                self.broadcast(f'{nickname} left the chat!'.encode('ascii'))
                break

    def receive(self):
        while True:
            client, address = self.server.accept()
            print(f'Connected with {str(address)}')

            client.send('NICK'.encode('ascii'))
            nickname = client.recv(1024).decode('ascii')
            self.nicknames.append(nickname)
            self.clients.append(client)

            print(f'Nickname of the client is {nickname}!')
            self.broadcast(f'{nickname} joined the chat!'.encode('ascii'), exclude=client)
            client.send('Connected to the server!'.encode('ascii'))

            thread = threading.Thread(target=self.handle, args=(client,))
            thread.start()

if __name__ == "__main__":
    server = Server()
    server.receive()
