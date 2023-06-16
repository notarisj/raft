# rpc_server.py

from xmlrpc.server import SimpleXMLRPCServer
from logger import MyLogger

logger = MyLogger()


class RPCServer:

    def __init__(self, host="localhost", port=8000):
        self.server = SimpleXMLRPCServer((host, port))
        logger.info(f"RPC server initialized. Listening on {host}:{port}...")

    def register_function(self, function, name=None):
        self.server.register_function(function, name)
        logger.info(f"Function '{function.__name__}' registered.")

    def run(self):
        logger.info("RPC server is running.")
        self.server.serve_forever()
        logger.info("RPC server stopped.")