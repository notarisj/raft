# rpc_server.py
import ssl
from xmlrpc.server import SimpleXMLRPCServer

from src.configurations import IniConfig
from src.logger import MyLogger

logger = MyLogger()
raft_config = IniConfig('/Users/notaris/git/raft/src/raft_node/deploy/config.ini')


class RPCServer:

    def __init__(self, host="localhost", port=8000):
        self.server = SimpleXMLRPCServer((host, port), logRequests=False, allow_none=True)
        self.server.socket = ssl.wrap_socket(self.server.socket,
                                             certfile=raft_config.get_property('SSL', 'ssl_cert_file'),
                                             keyfile=raft_config.get_property('SSL', 'ssl_key_file'),
                                             server_side=True)
        logger.info(f"RPC server initialized. Listening on {host}:{port}...")

    def register_function(self, function, name=None):
        self.server.register_function(function, name)
        logger.info(f"Function '{function.__name__}' registered.")

    def stop(self):
        logger.info("Stopping RPC server...")
        self.server.shutdown()
        logger.info("RPC server stopped.")

    def run(self):
        logger.info("RPC server is running.")
        self.server.serve_forever()
