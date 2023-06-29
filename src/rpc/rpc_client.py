# rpc_client.py
import ssl
import xmlrpc.client

from src.configurations import IniConfig
from src.logger import MyLogger

logger = MyLogger()
raft_config = IniConfig('src/raft_node/deploy/config.ini')


class RPCClient:
    def __init__(self, host="localhost", port=8000):
        url = f"https://{host}:{port}"  # Use HTTPS instead of HTTP
        context = ssl.create_default_context(cafile=raft_config.get_property('SSL', 'ssl_cert_file'))
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED
        self.server_proxy = xmlrpc.client.ServerProxy(url, allow_none=True, context=context)
        logger.info(f"RPC client initialized. Connected to {url}.")

    def call(self, method, *args):
        try:
            logger.info(f"Calling remote method '{method}' with arguments: {args}")
            result = getattr(self.server_proxy, method)(*args)
            logger.info("Remote method call completed.")
            return result
        except Exception as e:
            logger.error(f"An error occurred while calling remote method '{method}': {str(e)}")
            # Handle the exception or re-raise it if needed.
            # You can also return a specific value to indicate the error condition.
