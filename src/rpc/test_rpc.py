import threading
import unittest

from rpc_server import RPCServer
from rpc_client import RPCClient


# Server-side code
def add_numbers(x, y):
    return x + y


class RPCServerClientTest(unittest.TestCase):
    def setUp(self):
        # Server setup
        self.server = RPCServer()
        self.server.register_function(add_numbers)

        # Start the server in a separate thread
        self.server_thread = threading.Thread(target=self.server.run)
        self.server_thread.start()

        # Client setup
        self.client = RPCClient()

    def tearDown(self):
        # Stop the server
        self.server.server.shutdown()

        # Wait for the server thread to finish
        self.server_thread.join()

    def test_addition(self):
        result = self.client.call("add_numbers", 5, 3)
        self.assertEqual(result, 8)


if __name__ == "__main__":
    unittest.main()
