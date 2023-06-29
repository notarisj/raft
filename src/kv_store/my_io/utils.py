# import socket
# import ssl
# import sys
# import struct
# from typing import Optional, Any
#
# from src.logger import MyLogger
#
# logger = MyLogger()
#
#
# def send_message(message: str, conn: Any) -> None:
#     """
#     Sends a message over the established connection.
#
#     Args:
#         message (str): The message to be sent.
#         conn: The connection to the server.
#
#     Returns:
#         None
#     """
#     message_size = len(message)
#     sys.stdout.flush()
#     header = struct.pack('!I', message_size)
#     try:
#         conn.sendall(header)
#         conn.sendall(message.encode())
#     except (BrokenPipeError, AttributeError):
#         logger.info("Error sending message. Please ensure you are connected to the server.")
#         raise ConnectionError
#
#
# def receive_message(conn: Any) -> Optional[str]:
#     """
#     Receives a message from the connection.
#
#     Returns:
#         message (str): The received message as a string.
#     """
#     sys.stdout.flush()
#     header = conn.recv(4)
#     if not header:
#         return None
#     message_size = struct.unpack('!I', header)[0]
#     message_chunks = []
#     remaining_size = message_size
#     try:
#         while remaining_size > 0:
#             chunk_size = min(remaining_size, 4096)
#             chunk = conn.recv(chunk_size)
#             if not chunk:
#                 logger.info("Disconnected from the server.")
#                 break
#             message_chunks.append(chunk)
#             remaining_size -= len(chunk)
#         message = b''.join(message_chunks).decode()
#         return message
#     except (ConnectionResetError, AttributeError):
#         logger.info("Connection lost. Disconnected from the server.")
#         return None
#
#
# def connect_to_server(host, port, certificate_path):
#     try:
#         client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#
#         # Create an SSL context
#         context = ssl.create_default_context(cafile=certificate_path)
#         context.check_hostname = True
#         context.verify_mode = ssl.CERT_REQUIRED
#
#         # Wrap the client socket with SSL
#         client_socket = context.wrap_socket(client_socket, server_hostname=host)
#
#         client_socket.connect((host, port))
#         print(f"Connected to {host}:{port}")
#         return client_socket
#     except ConnectionRefusedError:
#         print(f"Failed to connect to {host}:{port}. Please ensure the server is running.")
#         return None
#
# def send_request_opened_connection(request, conn) -> str:
#     """
#     Sends a request to a specified raft_node address and receives the response.
#
#     Args:
#         request (str): The request to be sent.
#         conn: The connection to the server.
#
#     Returns:
#         The response received from the KV-server.
#     """
#     send_message(request, conn)
#     return receive_message(conn)
