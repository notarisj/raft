# rpc_client.py

import xmlrpc.client

from logger import MyLogger

logger = MyLogger()


class RPCClient:

    def __init__(self, host="localhost", port=8000):
        url = f"http://{host}:{port}"
        self.server_proxy = xmlrpc.client.ServerProxy(url, allow_none=True)
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
