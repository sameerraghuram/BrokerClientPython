from client import Connection

_printer = lambda x: print(x)

if __name__ == '__main__':

    # Creates a connection to the broker
    conn = Connection('newavalon.cs.rit.edu')

    # Create a queue with id "sample_queue" in the
    # "default" exchange.
    conn.create_queue('sample_queue')

    # Subscribe to incoming messages on the queue
    # Supply the _printer function defined earlier as a callback
    # which is used to print incoming messages.
    conn.subscribe("sample_queue", _printer)

    # Publish a message to the queue
    conn.publish('sample_queue', "Hello World")

    flag = True

    while(flag):
        # Continue the chat
        cmd = input("Enter a message you want to be sent.. ")
        if cmd == 'q':
            flag = False
        else:
            conn.publish('sample_queue', cmd)

