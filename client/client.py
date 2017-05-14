import sockutils
import consts

# Our application port
BROKER_PORT = 12344
CLIENT_PORT = 12343
BUF_SIZE = 2048
BROKER = 'newavalon.cs.rit.edu'

import json
import socket
import io
import threading
from concurrent.futures import ThreadPoolExecutor

def logger(log):
    print("[{}] {}".format(__name__, log))

def get_ip():
    return socket.gethostbyname(socket.getfqdn())

class Connection():
    '''
    Used to create a connection with the exchange.
    Further, the client can create a message queue, which
    it shall consume/publish to.
    '''

    def __init__(self, broker):
        '''
        Initializes the client listener.

        :param broker: address of the broker (domain name or ip-address)
        :type broker: String
        :return: An instance of a connection to the message broker
        :rtype: Connection
        '''
        self.server = None
        self.clients = {}
        self.listener_on = True

        self.broker = broker

        self._callbacks = {}        # Queues -> callback

        # Our application port
        self.BROKER_PORT = 12344
        self.CLIENT_PORT = 12343

        # Create a listerner
        self.listener = self.create_listener(('0.0.0.0',self.CLIENT_PORT))

        thread = threading.Thread(target=self.accept_connections, args=[self.listener])
        thread.start()



    def create_listener(self,address):
        '''
        Creates a server socket on the specified address.

        :param address: (address,port)
        :type address: Tuple
        :return: server socket
        :rtype: Socket
        '''
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        listener.bind(address)
        listener.listen(12)
        return listener

    def accept_connections(self,listener):
        '''
        Accepts a connection and creates another thread to handle it.

        :param listener:    Our listening serversocket
        :type listener:     Socket
        :return:            None
        :rtype:             None
        '''

        with ThreadPoolExecutor(max_workers=4) as executor:
            while(self.listener_on):
                client_socket,client_address = listener.accept()
                executor.submit(self.handle_connections, client_socket)


    def send_message_client(self, message):

        print("Sending to {}".format(self.broker))

        send_sock = socket.create_connection((self.broker, BROKER_PORT))
        message_stream = io.BytesIO(message.encode())
        send_chunk = message_stream.read(BUF_SIZE)

        while(send_chunk):
            send_sock.send(send_chunk)
            send_chunk = message_stream.read(BUF_SIZE)


    def handle_connections(self, client_socket):
        """
        Dispatches the request to a handler function as determined by
        the dispatch dictionary.

        :param client_socket: Incoming Socket Connection
        :type client_socket: Socket

        """
        print("[CLIENT] Receiving message..")
        message = sockutils.recieve_message(client_socket)
        print("[MESSAGE] {}".format(message))
        header = message[consts.MSG_HEADER_LABEL]
        request = header[consts.MSG_HEADER_REQUEST_LABEL]

        if request == consts.REQ_ADD_MESSGAE:
            self.handle_message(message)



    def create_queue(self, queue_name = None, exchange_name = None, acknowledge=False):
        '''
        Returns a dictionary in the form of a JSON object that
        contains the message required by the broker to create
        a queue.

        :return: JSON request
        :rtype: JSON
        '''

        # If exchange name is not specified. We shall use the default.
        if not exchange_name:
            exchange_name = 'default'

        # Message dictionary
        msg = {
            consts.MSG_HEADER_LABEL: {
                consts.MSG_HEADER_REQUEST_LABEL: consts.REQ_CREATE_QUEUE,
                consts.MSG_HEADER_CLIENT_LABEL: get_ip()
            },
            consts.INFO_NAME_EXCHANGE: exchange_name,
            consts.INFO_NAME_QUEUE: queue_name,
        }

        self.send_message_client(json.dumps(msg))


    def create_exchange(self, exchange_name, exchange_type=consts.TYPE_EXCHANGE_DIRECT):
        '''
        Returns a dictionary in the form of a JSON object that
        contains the message required by the broker to create
        an exchange.

        :return: JSON request
        :rtype: JSON
        '''
        client_ip = get_ip()

        # Message dictionary
        msg = {
            consts.MSG_HEADER_LABEL: {
                consts.MSG_HEADER_REQUEST_LABEL: consts.REQ_CREATE_EXCHAGE,
                consts.MSG_HEADER_CLIENT_LABEL: client_ip
            },
            consts.INFO_NAME_EXCHANGE: exchange_name,
            consts.INFO_TYPE_EXCHANGE: exchange_type
        }

        self.send_message_client(json.dumps(msg))


    def subscribe(self, queue_name, callback, exchange_name='default'):
        '''
        Returns a dictionary in the form of a JSON object that
        contains the message required by the broker to add
        a subscriber to a message_queue
        :return: JSON request
        :rtype: JSON
        '''
        client_ip = get_ip()


        # Message dictionary
        msg = {
            consts.MSG_HEADER_LABEL: {
                consts.MSG_HEADER_REQUEST_LABEL: consts.REQ_ADD_SUBSCRIBER,
                consts.MSG_HEADER_CLIENT_LABEL: client_ip
            },
            consts.INFO_NAME_EXCHANGE: exchange_name,
            consts.INFO_NAME_QUEUE: queue_name,
            consts.INFO_NAME_SUBSCRIBER: client_ip
        }

        self._callbacks[queue_name] = callback

        self.send_message_client(json.dumps(msg))


    def publish(self, queue_name, message, exchange_name='default'):
        '''
        Returns a dictionary in the form of a JSON object that
        contains the message required by the broker to create
        an exchange.

        :return: JSON request
        :rtype: JSON
        '''
        client_ip = get_ip()

        # Message dictionary
        msg = {
            consts.MSG_HEADER_LABEL: {
                consts.MSG_HEADER_REQUEST_LABEL: consts.REQ_ADD_MESSGAE,
                consts.MSG_HEADER_CLIENT_LABEL: client_ip
            },
            consts.INFO_NAME_EXCHANGE: exchange_name,
            consts.INFO_NAME_QUEUE: queue_name,
            consts.INFO_NAME_MESSAGE: message
        }

        self.send_message_client(json.dumps(msg))


    def handle_message(self, message):

        queue_name = message[consts.INFO_NAME_QUEUE]
        self._callbacks[queue_name](message)