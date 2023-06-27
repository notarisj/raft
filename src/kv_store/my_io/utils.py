import sys
import struct
from typing import Optional

from src.logger import MyLogger

logger = MyLogger()


def send_message(message, conn):
    """
    Sends a message over the established connection.

    Args:
        message (str): The message to be sent.
        conn: The connection to the server.

    Returns:
        None
    """
    message_size = len(message)
    sys.stdout.flush()
    header = struct.pack('!I', message_size)
    try:
        conn.sendall(header)
        conn.sendall(message.encode())
    except (BrokenPipeError, AttributeError):
        logger.info("Error sending message. Please ensure you are connected to the server.")
        raise ConnectionError


def receive_message(conn) -> Optional[str]:
    """
    Receives a message from the connection.

    Returns:
        message (str): The received message as a string.
    """
    sys.stdout.flush()
    header = conn.recv(4)
    if not header:
        return None
    message_size = struct.unpack('!I', header)[0]
    message_chunks = []
    remaining_size = message_size
    try:
        while remaining_size > 0:
            chunk_size = min(remaining_size, 4096)
            chunk = conn.recv(chunk_size)
            if not chunk:
                logger.info("Disconnected from the server.")
                break
            message_chunks.append(chunk)
            remaining_size -= len(chunk)
        message = b''.join(message_chunks).decode()
        # logger.log_info("[+] Message received successfully")
        return message
    except (ConnectionResetError, AttributeError):
        logger.info("Connection lost. Disconnected from the server.")
        return None


def send_request_opened_connection(request, conn) -> str:
    """
    Sends a request to a specified raft_node address and receives the response.

    Args:
        request (str): The request to be sent.
        conn: The connection to the server.

    Returns:
        The response received from the KV-server.
    """
    send_message(request, conn)
    return receive_message(conn)
