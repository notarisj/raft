from src.kv_store.server.kv_server import KVServer

if __name__ == '__main__':
    kv_server = KVServer(_replication_factor=2, _kv_server_host='localhost', _kv_server_port=9003,
                         _raft_server_host='localhost', _raft_server_port=9010,
                         _id=3, _server_list_file='/home/giannis-pc/Desktop/raft/src/kv_store/resources/serverFile.txt')
    kv_server.start()
