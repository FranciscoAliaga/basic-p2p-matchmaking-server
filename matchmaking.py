# python version 3.10.5

import os.path      
import cherrypy     # minimalistic server framework
import time         # time.time()
import random       # provides randomization
from collections import deque # queue support

TIMEOUT_TRIES = 20 # 20 timeout tries per request
TIMEOUT       = 10*60 # 10 minutes
START_TIME    = time.time()

# TODO: return proper HTTP ok codes

# Class for storing requests in a list in such a way that:
#   1. requests can be efficiently inserted, deleted and sampled uniformly at random
#   2. requests can be efficiently removed when timed out.
#   3. time out processing is only performed when the class recieves a request.
class HostRequests:

    # returns a request sampled uniformly at random.
    # should only be called if `not self.empty()`.
    def get_request(self):
        r = random.randint(0,len(self.requestPool)-1)
        return self.requestPool[r]

    # returns true if the requests list is empty
    def empty(self): return (len(self.requestPool)==0)

    # updates a request given a ip_adress (any string key) , a number >=0 and a time.
    def update_request(self, ip_adress : str, number : int, time : float):
        # safe to assume:
        # ip_adress is valid
        # number >= 0

        # check if ip_adress is inside
        if (ip_adress in self.requestMap):
            if (number>0):
                # then, update requestpool
                index = self.requestMap[ip_adress]
                self.requestPool[index] = (ip_adress,number,time) 
                self.requestQueue.append(ip_adress) # appends on the right
                return "REQUEST UPDATED"
            else:
                self.delete_request(ip_adress)
                return "REQUEST DELETED"
        # else, previous request not found.
        
        # is this request valid?
        if (number == 0): # no point in updating request
            return "REQUEST DELETED"

        ## create a new request
        # make room for another index at the end of the pool
        new_index = len(self.requestMap)
        self.requestPool.append((ip_adress,number,time)) # add request
        self.requestMap[ip_adress] = new_index           # add index to map
        self.requestQueue.append(ip_adress)              # add to queue
        return "REQUEST UPDATED"

    # deletes a request
    def delete_request(self, ip_adress : str):
        # safe to assume:
        # ip_adress is a valid ip_adress

        # does the request exist?
        if not (ip_adress in self.requestMap): return 

        # swap the request with the request at the last position
        index     = self.requestMap[ip_adress]
        end_index = len(self.requestPool)-1

        end_request = self.requestPool[end_index]
        end_ip      = end_request[0]

        self.requestPool[index] = end_request
        self.requestMap[end_ip] = index

        # pop last and the ip_adress from the map
        self.requestPool.pop()
        self.requestMap.pop(ip_adress)
        return

    def __init__(self,bad_request_error = cherrypy.HTTPError(400)):
        self.requestPool  : list  = [] # (ip,number,time) ; stores and retrieves requests
        self.requestMap   : dict  = {} # (key,value) = (ip,index) ; makes a map of request indexes
        self.requestQueue : deque = deque() # (ip,next) ; takes care of host request timeouts by checking on first ins
        self.bad_request_error = bad_request_error

    def process_timeouts(self):
        tries = TIMEOUT_TRIES
        while( len(self.requestQueue) > 0 and (tries > 0)):
            tries-=1
            ip    = self.requestQueue.popleft()
            if not (ip in self.requestMap): continue # deleted request, timeout not needed
            index   = self.requestMap[ip]
            request = self.requestPool[index]
            last_update = request[2]
            current_time = time.time()-START_TIME
            if last_update < current_time - TIMEOUT:
                # timeout!
                self.delete_request(ip)

Hosts = HostRequests()

class Matchmaking:

    @cherrypy.expose
    def host(self,number = None):
        if number==None: raise cherrypy.HTTPError(400)
        number = int(number)
        if (number<0): raise cherrypy.HTTPError(400) 

        host_ip   = cherrypy.request.remote.ip # does not pass through proxies
        curr_time = time.time() - START_TIME
        result    = Hosts.update_request(host_ip,number,curr_time)

        Hosts.process_timeouts()
        return result

    @cherrypy.expose
    def join(self):
        Hosts.process_timeouts()
        ok = not Hosts.empty()
        if ok:
            result = Hosts.get_request() 
            host_ip = result[0]
            Hosts.process_timeouts()
            return host_ip
        # else
        return "NO HOST AVAILABLE"

conf = os.path.join(
    os.path.dirname(__file__),'basic.conf'
)

if __name__ == '__main__':
    cherrypy.quickstart(Matchmaking (),config=conf)