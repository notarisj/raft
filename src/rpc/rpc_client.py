# rpc_client.py
import ssl
import xmlrpc.client

from src.configuration_reader import IniConfig
from src.logger import MyLogger

logger = MyLogger()
raft_config = IniConfig('src/configurations/config.ini')


class RPCClient:
    """
    A simple RPC client that connects to a remote server and calls a method on it.

    Args:
        host (str): Hostname of the remote server
        port (int): Port number of the remote server

    Attributes:
        server_proxy (xmlrpc.client.ServerProxy): A proxy object that represents the remote server
    """
    def __init__(self, host="localhost", port=8000):
        """
        Initialize the RPC client.

        Args:
            host (str): Hostname of the remote server
            port (int): Port number of the remote server
        """
        url = f"https://{host}:{port}"  # Use HTTPS instead of HTTP
        context = ssl.create_default_context(cafile=raft_config.get_property('SSL', 'ssl_cert_file'))
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED
        self.server_proxy = xmlrpc.client.ServerProxy(url, allow_none=True, context=context)
        logger.info(f"RPC client initialized. Connected to {url}.")

    def call(self, method, *args):
        """
        Call a remote method on the server.

        Args:
            method (str): Name of the remote method to call
            *args: Variable length argument list for the remote method

        Returns:
            The return value of the remote method

        Raises:
            Exception: If an error occurs while calling the remote method
        """
        try:
            result = getattr(self.server_proxy, method)(*args)
            return result
        except Exception as e:
            logger.error(f"An error occurred while calling remote method '{method}': {str(e)}")
            # Handle the exception or re-raise it if needed.
            # You can also return a specific value to indicate the error condition.
