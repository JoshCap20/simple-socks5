import select
import socket
import struct
from socketserver import StreamRequestHandler

from constants import SOCKS_VERSION, ReplyCode
from utils import send_socks_response, parse_socks_request


class SocksProxy(StreamRequestHandler):
    connection: socket.socket

    def handle(self) -> None:
        # Initial greeting and version agreement
        version, nmethods = struct.unpack("!BB", self.connection.recv(2))
        if version != SOCKS_VERSION:
            # Unsupported SOCKS protocol version
            return

        methods = self.connection.recv(nmethods)
        if not self.authenticate(methods):
            # Authentication failed
            return

        # Request handling
        version, cmd, address_type, dest_address, dest_port = parse_socks_request(self.connection)
        if version != SOCKS_VERSION:
            # Incorrect SOCKS version
            return

        try:
            if cmd == 1:
                self.handle_connect(dest_address, dest_port)
            else:
                # Unsupported command
                self.send_reply(ReplyCode.COMMAND_NOT_SUPPORTED)
        except Exception as e:
            # General SOCKS server failure
            self.send_reply(ReplyCode.GENERAL_SOCKS_SERVER_FAILURE)

    def authenticate(self, methods: bytes) -> bool:
        # Implement authentication logic
        # No authentication required:
        self.connection.sendall(struct.pack("!BB", SOCKS_VERSION, 0))
        return True

    def handle_connect(self, dest_address: str, dest_port: int) -> None:
        # Establish a connection to the destination
        try:
            remote_socket = socket.create_connection((dest_address, dest_port))
            local_address, local_port = remote_socket.getsockname()
            self.send_reply(ReplyCode.SUCCEEDED, local_address, local_port)

            # Start relaying data
            self.relay_data(self.connection, remote_socket)
        except socket.error:
            self.send_reply(ReplyCode.CONNECTION_REFUSED)

    def relay_data(
        self, client_socket: socket.socket, remote_socket: socket.socket
    ) -> None:
        while True:
            # Wait until either socket has data to read
            r, w, e = select.select([client_socket, remote_socket], [], [])

            if client_socket in r:
                data = client_socket.recv(4096)
                if len(data) == 0:  # No more data to read
                    break
                remote_socket.sendall(data)

            if remote_socket in r:
                data = remote_socket.recv(4096)
                if len(data) == 0:  # No more data to read
                    break
                client_socket.sendall(data)

    def send_reply(
        self, reply_code: ReplyCode, address: str = "0.0.0.0", port: int = 0
    ) -> None:
        # Send a SOCKS reply to the client
        send_socks_response(self.connection, reply_code, address, port)
