from src.kv_store.client.external_client import ExternalClient

# Example usage
if __name__ == '__main__':
    server_ip = 'localhost'
    server_port = 9001
    client = ExternalClient(server_ip, server_port)
    client.connect()
    client.start_interaction()
