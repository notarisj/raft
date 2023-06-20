from kv_store.server.kv_server import KVServer

if __name__ == '__main__':
    kv_server = KVServer(_kv_server_host='localhost', _kv_server_port=9002,
                         _raft_server_host='localhost', _raft_server_port=9010,
                         _id=2, _server_list_file='/home/giannis-pc/Desktop/raft/kv_store/resources/serverFile.txt')
    kv_server.start()
