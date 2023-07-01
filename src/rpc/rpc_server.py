# rpc_server.py
import ssl
from xmlrpc.server import SimpleXMLRPCServer

from src.configuration_reader import IniConfig
from src.logger import MyLogger

logger = MyLogger()
raft_config = IniConfig('src/configurations/config.ini')


class RPCServer:
    """
    A simple XML-RPC server that can register functions and run forever.

    Usage:
        server = RPCServer(host="localhost", port=8000)
        server.register_function(function1, name="function1")
        server.register_function(function2, name="function2")
        threading.Thread(target=server).start()

    Args:
        host (str): Hostname of the server
        port (int): Port number of the server

    Attributes:
        server (xmlrpc.server.SimpleXMLRPCServer): An XML-RPC server object
    """

    def __init__(self, host="localhost", port=8000):
        """
        Initialize the RPC server.

        Args:
            host (str): Hostname of the server
            port (int): Port number of the server
        """
        self.server = SimpleXMLRPCServer((host, port), logRequests=False, allow_none=True)
        self.server.socket = ssl.wrap_socket(self.server.socket,
                                             certfile=raft_config.get_property('SSL', 'ssl_cert_file'),
                                             keyfile=raft_config.get_property('SSL', 'ssl_key_file'),
                                             server_side=True)
        logger.info(f"RPC server initialized. Listening on {host}:{port}...")

    def register_function(self, function, name=None):
        """
        Register a function with the server.

        Args:
            function: The function to register
            name (str): The name to register the function with
        """
        self.server.register_function(function, name)
        logger.info(f"Function '{function.__name__}' registered.")

    def stop(self):
        """
        Stop the RPC server.
        """
        logger.info("Stopping RPC server...")
        self.server.shutdown()
        logger.info("RPC server stopped.")

    def run(self):
        """
        Run the RPC server forever.

        Note:
            This method blocks the current thread.
            It should be called in a separate thread.
        """
        logger.info("RPC server is running.")
        self.server.serve_forever()
