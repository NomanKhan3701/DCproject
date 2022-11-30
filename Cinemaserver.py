from xmlrpc.server import SimpleXMLRPCServer,SimpleXMLRPCRequestHandler
import xmlrpc.client
import sys,os
import queue
import threading
from time import sleep
import pika
import pandas as pd
import json
import datetime
import clockSync.berkeley as berkeley


# set as False to hide logs
DEBUG = True

''' constants '''
DEBUG_FLAG = '[DEBUG]'                          # flag used in logs
BROADCAST = 'broadcast'                         # id of exchange common to all nodes (used as broadcast)
MSG_REQUEST = 'REQUEST'                         # Lamport request message prefix
MSG_RELEASE = 'RELEASE'                         # Lamport release message prefix
MSG_PERMISSION = 'PERMISSION'                   # Lamport granted permission message prefix
MSG_NETWORK_SIZE_REQUEST = 'NETWORK_SIZE'       # network size request message prefix
MSG_NETWORK_SIZE_ACK = 'NETWORK_SIZE_ACK'       # network size response message prefix
STATUS = ''

''' global variables '''
requests = queue.PriorityQueue()                # thread-safe requests queue, automatically ordered by timestamps
clock = 0                                       # logical clock used by Lamport Algorithm
network_size = 1                                # number of nodes in the system
received_permissions = 0                        # global counter: number of received permissions for the actual request
node_id = ''

global port
port = None

class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/delhi','/mumbai','/bangalore')


class Request:
    def __init__(self, timestamp, queue_name, access_duration=None):
        self.timestamp = timestamp
        self.owner_id = queue_name
        self.access_duration = access_duration

    def __repr__(self):
        return "(timestamp: %s, queue: %s, access_duration: %s)" % (self.timestamp, self.owner_id, self.access_duration)

    # used by PriorityQueue for comparing elements
    def __lt__(self, other):
        return self.timestamp < other["timestamp"]

def bookTicket(n,city):
    seconds = 5
    seats = pd.DataFrame(json.loads(showAvailableSeats(city.lower())))
    if not 0<n<=seats.shape[0]:
        return {'status':f"Seat number {n} does not exist. Please retry with a valid seat number." , 'seats':seats.to_json(orient='records')}
    elif(seats.Status[n-1]==0):
        seats.Status[n-1] = 1
        seats.Timestamp[n-1] = datetime.datetime.now()
        print(seats.to_string(index=False))
        database_proxy.update_database(seats.to_json(orient='records'),city.lower())
        for i in range(1, seconds + 1):
            sleep(1)
            print('work done: ' + str(int(100*(i/seconds))) + '%')
        return {'status':"Congratulations! You have booked seat number "+ str(n) +" at " + str(cinemaName)+", "+ str(city) , 'seats': seats.to_json(orient='records')}
    else:
        return {'status':"Sorry the seat you selected has already been booked, select another seat." , 'seats':seats.to_json(orient='records')}

def showAvailableSeats(city):
    return database_proxy.request_database(city.lower())

# increment global variable clock
def increment_clock():
    global clock
    clock += 1
    if DEBUG:
        print(DEBUG_FLAG, "[CLOCK] incremented clock to", clock)


# return True if, and only if, all the necessary permissions for the last request have been received
def node_has_permissions():
    return received_permissions == (network_size-1)


# put a request in node's request queue
def requests_put(request):
    requests.put_nowait(request)
    if DEBUG:
        print(DEBUG_FLAG, '[PUT]', request)
        print(requests.queue)


# get the first request from node's request queue
def requests_get():
    req = requests.get()  # equivalent to get(False)
    if DEBUG:
        print(DEBUG_FLAG, '[GET]', req)
        print(requests.queue)
    return req

def enter_critical_section(request,city):
    global received_permissions
    global seats
    received_permissions = 0
    # request = requests_get()
    seats = showAvailableSeats(city.lower())
    temp = bookTicket(request["access_duration"],city)
    return json.dumps(temp)

def serverDetails(city):
    return f"\n{'*'*60}\n\nWelcome to INOX Cinema, "+ str(city)+". Served by port "+ str(port)+f"\n\n{'*'*60}"


if __name__ == '__main__':
    berkeley.initiateClockServer()
    cinemaName = "INOX Cinema"
    seats = None
    database_proxy = xmlrpc.client.ServerProxy("http://localhost:9999")

    if sys.argv.__len__()>1:
        port = int(sys.argv[1])

    server = SimpleXMLRPCServer(("localhost", port),requestHandler=RequestHandler,allow_none=True)
    print("Welcome to "+str(cinemaName) + " " + str(port) + " - " + str(os.getpid()))
    server.register_instance(node_id, "node_id")
    server.register_instance(clock, "clock")
    server.register_instance(seats,"seats")
    server.register_instance(MSG_REQUEST, "MSG_REQUEST")
    server.register_function(enter_critical_section, "enter_critical_section")
    server.register_function(increment_clock, "increment_clock")
    server.register_function(requests_put, "requests_put")
    server.register_function(bookTicket, "bookTicket")
    server.register_function(serverDetails, "serverDetails")
    server.register_function(showAvailableSeats, "showAvailableSeats")
    server.serve_forever()

