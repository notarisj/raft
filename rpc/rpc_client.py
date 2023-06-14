# rpc_client.py

import xmlrpc.client

from logger import MyLogger

logger = MyLogger()


class RPCClient:
    """
    A class representing an RPC client.

    Attributes:
        server_proxy (xmlrpc.client.ServerProxy): The XML-RPC server proxy.

    Methods:
        __init__(self, url="http://localhost:8000"): Initializes the RPCClient instance.
        call(self, method, *args): Calls a remote method on the server.
    """

    def __init__(self, url="http://localhost:8000"):
        """
        Initializes the RPCClient instance.

        Args:
            url (str): The URL of the RPC server. Defaults to "http://localhost:8000".
        """
        self.server_proxy = xmlrpc.client.ServerProxy(url)
        logger.info(f"RPC client initialized. Connected to {url}.")

    def call(self, method, *args):
        """
        Calls a remote method on the server.

        Args:
            method (str): The name of the method to call.
            *args: Variable length arguments to be passed to the method.

        Returns:
            The result of the method call.
        """
        try:
            logger.info(f"Calling remote method '{method}' with arguments: {args}")
            result = getattr(self.server_proxy, method)(*args)
            logger.info("Remote method call completed.")
            return result
        except Exception as e:
            logger.error(f"An error occurred while calling remote method '{method}': {str(e)}")
            # Handle the exception or re-raise it if needed.
            # You can also return a specific value to indicate the error condition.
