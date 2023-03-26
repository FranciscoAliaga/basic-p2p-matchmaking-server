# python version 3.10.5

from matchmaking import HostRequests

class bad_request(Exception):
    pass

H = HostRequests(bad_request)

##########################################

# TODO: unit testing