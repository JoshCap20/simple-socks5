import struct
import socket

from constants import SOCKS_VERSION


class RequestHandler:
    @staticmethod
    def handle_handshake(connection: socket.socket) -> bool:
        version, nmethods = struct.unpack("!BB", connection.recv(2))
        if version != SOCKS_VERSION:
            return False

        methods = connection.recv(nmethods)
        return RequestHandler._authenticate(connection, methods)

    @staticmethod
    def _authenticate(connection: socket.socket, methods) -> bool:
        # TODO: Implement authentication
        connection.sendall(struct.pack("!BB", SOCKS_VERSION, 0))
        return True

    @staticmethod
    def parse_request(connection: socket.socket) -> tuple:
        version, cmd, _, address_type = struct.unpack("!BBBB", connection.recv(4))
        return version, cmd, address_type

    @staticmethod
    def parse_address_and_port(
        connection: socket.socket, address_type: int
    ) -> socket.socket:
        if address_type == 1:  # IPv4
            address = socket.inet_ntoa(connection.recv(4))
        elif address_type == 3:  # Domain name
            domain_length = connection.recv(1)[0]
            address = connection.recv(domain_length)
            address = socket.gethostbyname(address)
        port = struct.unpack("!H", connection.recv(2))[0]
        return address, port
