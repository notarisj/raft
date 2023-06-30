from .command_handler import search_top_lvl_key, search
from .kv_server import KVServer
from .message_helper import get_key, check_id_exist
from .query_handler import RequestHandler
from .raft_json import RaftJSON, RaftJSONEncoder
from .server_json import ServerJSON, ServerJSONEncoder

__all__ = ['KVServer', 'RequestHandler', 'ServerJSON', 'ServerJSONEncoder', 'search_top_lvl_key', 'search', 'get_key',
           'check_id_exist', 'RaftJSON', 'RaftJSONEncoder']

"""
Server is the kv raft_node. It gets requests, process them and send back the result.
Also communicate with Raft nodes with sockets and users.
"""

"""
Make inheritance for the 3 types of requests.
"""
