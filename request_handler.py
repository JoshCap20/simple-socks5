import struct
import socket

from constants import SOCKS_VERSION, AddressTypeCodes
from logger import logger


class RequestHandler:
    @staticmethod
    def handle_handshake(connection: socket.socket) -> bool:
        try:
            header = connection.recv(2)
            if len(header) < 2:
                return False

            version, nmethods = struct.unpack("!BB", header)
            if version != SOCKS_VERSION:
                return False

            methods = connection.recv(nmethods)
            return RequestHandler._authenticate(connection, methods)
        except socket.error as e:
            logger.error(f"Socket error during handshake: {e}")
            return False

    @staticmethod
    def _authenticate(connection: socket.socket, methods) -> bool:
        # TODO: Implement authentication
        connection.sendall(struct.pack("!BB", SOCKS_VERSION, 0))
        return True

    @staticmethod
    def parse_request(connection: socket.socket) -> tuple:
        try:
            header = connection.recv(4)
            if len(header) < 4:
                return None, None, None

            version, cmd, _, address_type = struct.unpack("!BBBB", header)
            return version, cmd, address_type
        except socket.error as e:
            logger.error(f"Socket error during request parsing: {e}")
            return None, None, None

    @staticmethod
    def parse_address_and_port(connection: socket.socket, address_type: int) -> tuple:
        try:
            if address_type == AddressTypeCodes.IPv4:
                address = socket.inet_ntoa(connection.recv(4))
            elif address_type == AddressTypeCodes.DOMAIN_NAME:
                domain_length = connection.recv(1)[0]
                address = connection.recv(domain_length)
                address = socket.gethostbyname(address)
            elif address_type == AddressTypeCodes.IPv6:
                address = socket.inet_ntop(socket.AF_INET6, connection.recv(16))
            else:
                return None, None

            port = struct.unpack("!H", connection.recv(2))[0]
            return address, port
        except socket.error as e:
            logger.error(f"Socket error during address and port parsing: {e}")
            return None, None

    @staticmethod
    def get_address_type(connection: socket.socket) -> AddressTypeCodes | None:
        _, _, address_type = RequestHandler.parse_request(connection)
        if address_type == 1:
            return AddressTypeCodes.IPv4
        elif address_type == 3:
            return AddressTypeCodes.DOMAIN_NAME
        elif address_type == 4:
            return AddressTypeCodes.IPv6
        else:
            return None
