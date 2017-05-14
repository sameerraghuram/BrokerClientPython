import json
import socket
import io
from gevent import monkey
monkey.patch_all()

# Our application port
BROKER_PORT = 12344
CLIENT_PORT = 12343
BUF_SIZE = 1024

def send_message_client(broker, message):

    print("Sending to {}".format(broker))

    send_sock = socket.create_connection((broker, BROKER_PORT))
    message_stream = io.BytesIO(json.dumps(message).encode())
    send_chunk = message_stream.read(BUF_SIZE)

    while(send_chunk):
        send_sock.send(send_chunk)
        send_chunk = message_stream.read(BUF_SIZE)



def send_message_server(subscriber, message):

    print("Sending to {}".format(subscriber))

    send_sock = socket.create_connection((subscriber, CLIENT_PORT))
    message_stream = io.BytesIO(json.dumps(message).encode())
    send_chunk = message_stream.read(BUF_SIZE)

    while(send_chunk):
        send_sock.send(send_chunk)
        send_chunk = message_stream.read(BUF_SIZE)

def recieve_message(sock):

    data = bytes('','utf-8')
    recv_blob = sock.recv(1024)
    #print("recvd")
    while(recv_blob):
        data += recv_blob
        recv_blob = sock.recv(1024)

    return json.loads(data.decode())