import socket
import threading
from queue import Queue

class Server:
    def __init__(self, host='127.0.0.1', port=55555):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.server.bind((self.host, self.port))
        self.server.listen()
        self.clients = []
        self.nicknames = []
        self.message_buffer = Queue()

    def broadcast(self, message, exclude=None):
        if exclude is not None:
            for client in self.clients:
                if client != exclude:
                    try:
                        client.send(message)
                    except:
                        client.close()
                        self.clients.remove(client)
        else:
            for client in self.clients:
                try:
                    client.send(message)
                except:
                    client.close()
                    self.clients.remove(client)


        if exclude:
            while not self.message_buffer.empty():
                message = self.message_buffer.get()
                try:
                    exclude.send(message)
                except:
                    pass

    def disconnect_client(self, client):
        if client in self.clients:
            index = self.clients.index(client)
            nickname = self.nicknames[index]
            self.clients.remove(client)
            self.nicknames.remove(nickname)
            client.close()
            self.broadcast(f'{nickname} left the chat!'.encode('ascii'))
            print(f'{nickname} disconnected.')

    def handle(self, client):
        while True:
            try:
                message = client.recv(1024)
                self.broadcast(message)
                self.message_buffer.put(message)
            except:
                self.disconnect_client(client)
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
    def stop(self):
        for client in self.clients:
            client.shutdown(socket.SHUT_RDWR)
            client.close()
        self.server.shutdown(socket.SHUT_RDWR)
        self.server.close()
        print("Server stopped")

if __name__ == "__main__":
    server = Server()
    server.receive()
