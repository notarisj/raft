from .command_handler import *
from .kv_server import KVServer
from .message_helper import *
from .query_handler import RequestHandler

__all__ = ['KVServer', 'RequestHandler']

"""
Server is the kv raft_node. It gets requests, process them and send back the result.
Also communicate with Raft nodes with sockets and users.
"""

"""
Make inheritance for the 3 types of requests.
"""
