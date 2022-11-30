import xmlrpc.client
import sys
import json
import pandas as pd
import clockSync.client as client 

client.initiateSlaveClient()

global path
path = None
proxy = None

print(f"\n{'*'*60}\n\nWelcome to INOX Cinema\n\n{'*'*60}")

locs = {1: 'Mumbai', 2: 'Delhi', 3: 'Bangalore'}
if sys.argv.__len__()>1:
    path = sys.argv[1]
else:
    path = locs[int(input('\nChoose Location -\n1: Mumbai\n2: Delhi\n3: Bangalore\n\n->  '))]

try:
    proxy = xmlrpc.client.ServerProxy("http://localhost/"+str(path.lower()))
    print(proxy.serverDetails(path))
except:
    print('\nServers not available. Try again later.\n\nThank you!\n')
    proxy = None
    print(f'\n{"*"*20}\tTHANK YOU!!\t{"*"*20}\n')



class Request:
    def __init__(self, timestamp, queue_name, access_duration=None):
        self.timestamp = timestamp
        self.owner_id = queue_name
        self.access_duration = access_duration

    def __repr__(self):
        return "(timestamp: %s, queue: %s, access_duration: %s)" % (self.timestamp, self.owner_id, self.access_duration)

    # used by PriorityQueue for comparing elements
    def __lt__(self, other):
        return self.timestamp < other.timestamp

def create_request(n,city):
    # increment timestamp before creating a request
    proxy.increment_clock()
    # push request to own queue
    request = Request(proxy.clock, proxy.node_id,n)
    # proxy.requests_put(request)
    response = json.loads(proxy.enter_critical_section(request,city))
    print(f'\n{"*"*80}\n{response["status"]}\n{"*"*80}')


while proxy:
    choice = int(input("\nPress -\n1. To select and book seat \n2. Show available seats\n3. Change Location\n4. Exit\n\n->  "))
    if(choice==1):
        seats = pd.DataFrame(json.loads(proxy.showAvailableSeats(path.lower())))
        print('\n',seats.to_string(index=False))
        n = int(input(f"\nWhich seat from 1-{seats.shape[0]} would you want to book: "))
        create_request(n,path)
        # msg = proxy.bookTicket(n,path)
        # print(msg)
    elif(choice==2):
        print(f'\nINOX Cinema, {path} - Seating Arrangement:')
        seats = pd.DataFrame(json.loads(proxy.showAvailableSeats(path.lower())))
        print('\n',seats.to_string(index=False))
    elif(choice==3):
        path = locs[int(input('\nChoose Location -\n1: Mumbai\n2: Delhi\n3: Bangalore\n\n->  '))]
        proxy = xmlrpc.client.ServerProxy("http://localhost/"+str(path))
        print(proxy.serverDetails(path))
    elif(choice==4):
        print(f'\n{"*"*20}\tTHANK YOU!!\t{"*"*20}\n')
        break

