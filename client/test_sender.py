from client import Connection

_printer = lambda x: print(x)

if __name__ == '__main__':
    # Connect to the broker
    conn = Connection('newavalon.cs.rit.edu')

    # Create a queue
    conn.create_queue('q1')

    # Subscribe to the queue
    conn.subscribe('q1', _printer)




