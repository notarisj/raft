"""
Server is the kv raft_node. It gets requests, process them and send back the result.
Also communicate with Raft nodes with sockets and users.
"""

"""
Make inheritance for the 3 types of requests.
"""