import pytest
import socket
import threading
import time

def client_simulation(port, nickname, messages_to_send, received_messages, ready_event, finished_event):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.settimeout(5)
    client_socket.connect(('localhost', port))
    client_socket.send(nickname.encode('ascii'))
    response = client_socket.recv(1024).decode('ascii')
    print(f"{nickname} received initial response: {response}")

    ready_event.set()
    finished_event.wait()

    try:
        for msg in messages_to_send:
            full_message = f'{nickname}: {msg}'
            client_socket.send(full_message.encode('ascii'))
            print(f"{nickname} sent: {msg}")

        while True:
            try:
                message = client_socket.recv(1024).decode('ascii')
                if message:
                    received_messages.append(message)
                    print(f"{nickname} received: {message}")
                else:
                    break
            except socket.timeout:
                print(f"{nickname} receive timed out")
                break
    finally:
        client_socket.close()

@pytest.fixture
def setup_server():
    from server import Server
    server = Server()
    server_thread = threading.Thread(target=server.receive, daemon=True)
    server_thread.start()
    yield server
    server.stop()
    server_thread.join(timeout=5)
    if server_thread.is_alive():
        print("Warning: Server thread did not terminate properly.")
def test_message_exchange(setup_server):
    port = 55555
    received_messages_client1 = []
    received_messages_client2 = []
    ready_event_client1 = threading.Event()
    ready_event_client2 = threading.Event()
    finished_event = threading.Event()

    client1_thread = threading.Thread(target=client_simulation, args=(port, 'Client1', ['Hello from Client1'], received_messages_client1, ready_event_client1, finished_event))
    client2_thread = threading.Thread(target=client_simulation, args=(port, 'Client2', ['Hello from Client2'], received_messages_client2, ready_event_client2, finished_event))

    client1_thread.start()
    client2_thread.start()

    ready_event_client1.wait()
    ready_event_client2.wait()
    finished_event.set()

    client1_thread.join()
    client2_thread.join()

    split_messages_client1 = [msg.split('!') for msg in received_messages_client1]
    split_messages_client2 = [msg.split('!') for msg in received_messages_client2]

    assert any('Client1: Hello from Client1' in msg for msg in split_messages_client2)
    assert any('Client2: Hello from Client2' in msg for msg in split_messages_client1)
if __name__ == "__main__":
    pytest.main(['-s', 'testP2P.py'])
