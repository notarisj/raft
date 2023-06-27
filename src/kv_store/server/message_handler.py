import json


def format_msg_for_search(message, _sender) -> str:
    data = json.loads(message)
    data['sender'] = _sender
    return json.dumps(data)


def format_top_lvl_key_msg(message, _sender) -> str:
    data = json.loads(message)
    data['sender'] = _sender
    data['command'] = message
    return json.dumps(data)


# def format_to_send_over_raft(message, _sender, _command_type, _rep_ids) -> str:
#     data = json.loads(message)
#     data['sender'] = _sender
#     data['command'] = _command_type + " " + get_msg_command_value(message)
#     data['rep_ids'] = _rep_ids
#     return json.dumps(data)


def is_client_request(request) -> bool:
    try:
        msg = json.loads(request)
        return msg['sender'] == 'CLIENT'
    except json.JSONDecodeError as e:
        raise e


def is_raft_request(request) -> bool:
    try:
        msg = json.loads(request)
        return msg['sender'] == 'RAFT'
    except json.JSONDecodeError as e:
        raise e


def is_kv_server_request(request) -> bool:
    try:
        msg = json.loads(request)
        return msg['sender'] == 'KV_SERVER'
    except json.JSONDecodeError as e:
        raise e


# def get_msg_command_type(request) -> str:
#     try:
#         msg = json.loads(request)['commands']
#         results = msg.split(" ", 1)
#         return results[0]
#     except json.JSONDecodeError as e:
#         raise e


# def get_msg_command_value(request) -> str:
#     try:
#         msg = json.loads(request)['commands']
#         results = msg.split(" ", 1)
#         return results[1]
#     except json.JSONDecodeError as e:
#         raise e


def get_msg_command(request) -> str:
    try:
        msg = json.loads(request)
        return msg['commands']
    except json.JSONDecodeError as e:
        raise e


def get_key(_request) -> str:
    msg = json.loads(_request)['commands']
    results = msg.split(" ", 3)
    key = results[1].replace(":", "").replace("\"", "")
    return key


def get_requests_list(request) -> list:
    try:
        msg = json.loads(request)
        return msg['requests']
    except json.JSONDecodeError as e:
        raise e


def check_id_exist(request, _id) -> bool:
    try:
        msg = json.loads(request)
        replication_nodes = msg.get("rep_ids", [])
        return _id in replication_nodes
    except json.JSONDecodeError as e:
        raise e
