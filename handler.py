import sys
import select
import socket
import struct
from socketserver import StreamRequestHandler

from constants import SOCKS_VERSION, ReplyCode
from utils import generate_failed_reply


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
        version, cmd, _, address_type = struct.unpack("!BBBB", self.connection.recv(4))

        if version != SOCKS_VERSION:
            # Incorrect SOCKS version
            return

        if address_type == 1:  # IPv4
            address = socket.inet_ntoa(self.connection.recv(4))
        elif address_type == 3:  # Domain name
            domain_length = self.connection.recv(1)[0]
            address = self.connection.recv(domain_length)
            address = socket.gethostbyname(address)
        port = struct.unpack("!H", self.connection.recv(2))[0]

        try:
            if cmd == 1:
                remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                remote.connect((address, port))
                bind_address = remote.getsockname()
            else:
                # Unsupported command
                self.server.close_request(self.request)

            addr = struct.unpack("!I", socket.inet_aton(bind_address[0]))[0]
            port = bind_address[1]
            reply = struct.pack("!BBBBIH", SOCKS_VERSION, 0, 0, 1, addr, port)

        except Exception as e:
            # General SOCKS server failure
            reply = generate_failed_reply(address_type, ReplyCode.GENERAL_SOCKS_SERVER_FAILURE)

        self.connection.sendall(reply)

        # establish data exchange
        if reply[1] == 0 and cmd == 1:
            self.relay_data(self.connection, remote)

        self.server.close_request(self.request)

    def authenticate(self, methods: bytes) -> bool:
        # Implement authentication logic
        # No authentication required:
        self.connection.sendall(struct.pack("!BB", SOCKS_VERSION, 0))
        return True

    def relay_data(
        self, client_socket: socket.socket, remote_socket: socket.socket
    ) -> None:
        try:
            while True:
                # wait until client or remote is available for read
                r, w, e = select.select([client_socket, remote_socket], [], [])

                if client_socket in r:
                    data = client_socket.recv(4096)
                    if remote_socket.send(data) <= 0:
                        break

                if remote_socket in r:
                    data = remote_socket.recv(4096)
                    if client_socket.send(data) <= 0:
                        break

        except BrokenPipeError as e:
            print(f"Caught BrokenPipeError: {e}", file=sys.stderr)
        except ConnectionResetError as e:
            print(f"Caught ConnectionResetError: {e}", file=sys.stderr)
        finally:
            client_socket.close()
            remote_socket.close()
