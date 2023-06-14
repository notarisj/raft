# rpc_server.py

from xmlrpc.server import SimpleXMLRPCServer
from logger import MyLogger

logger = MyLogger()


class RPCServer:
    """
    A class representing an RPC server.

    Attributes:
        server (SimpleXMLRPCServer): The underlying XML-RPC server.

    Methods:
        __init__(self, host="localhost", port=8000): Initializes the RPCServer instance.
        register_function(self, function, name=None): Registers a function with the server.
        run(self): Starts the RPC server and begins listening for incoming requests.
    """

    def __init__(self, host="localhost", port=8000):
        """
        Initializes the RPCServer instance.

        Args:
            host (str): The hostname or IP address to bind the server to. Defaults to "localhost".
            port (int): The port number to bind the server to. Defaults to 8000.
        """
        self.server = SimpleXMLRPCServer((host, port))
        logger.info(f"RPC server initialized. Listening on {host}:{port}...")

    def register_function(self, function, name=None):
        """
        Registers a function with the server.

        Args:
            function (callable): The function to be registered.
            name (str): The name under which the function should be registered. Defaults to None.
        """
        self.server.register_function(function, name)
        logger.info(f"Function '{function.__name__}' registered.")

    def run(self):
        """Starts the RPC server and begins listening for incoming requests."""
        logger.info("RPC server is running.")
        self.server.serve_forever()
        logger.info("RPC server stopped.")