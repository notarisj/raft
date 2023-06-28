from src.kv_store.server.kv_server import KVServer

if __name__ == '__main__':
    kv_server = KVServer(_id=1, _replication_factor=2)
    kv_server.start()
