import struct
import socket

from constants import SOCKS_VERSION, AddressTypeCodes, MethodCodes, USERNAME, PASSWORD
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
    def _authenticate(connection: socket.socket, methods: bytes) -> bool:
        client_methods = {method for method in methods}

        supported_methods = {
            MethodCodes.NO_AUTHENTICATION_REQUIRED.value,
            MethodCodes.USERNAME_PASSWORD.value,
        }

        mutual_method = client_methods.intersection(supported_methods)

        if MethodCodes.USERNAME_PASSWORD.value in mutual_method:
            connection.sendall(
                struct.pack(
                    "!BB", SOCKS_VERSION, MethodCodes.USERNAME_PASSWORD.value
                )
            )
            return RequestHandler._handle_username_password_auth(connection)
        elif MethodCodes.NO_AUTHENTICATION_REQUIRED.value in mutual_method:
            connection.sendall(
                struct.pack(
                    "!BB", SOCKS_VERSION, MethodCodes.NO_AUTHENTICATION_REQUIRED.value
                )
            )
            return True
        else:
            # No acceptable methods
            connection.sendall(
                struct.pack(
                    "!BB", SOCKS_VERSION, MethodCodes.NO_ACCEPTABLE_METHODS.value
                )
            )
            return False
        
    @staticmethod
    def _handle_username_password_auth(connection: socket.socket) -> bool:
        connection.settimeout(45.0)
        try:
            # Receive and verify the version
            version = connection.recv(1)
            if not version or version != b"\x01":
                logger.error(f"Incorrect subnegotiation version: {version}")
                return False

            # Receive username length and username
            username_len_byte = connection.recv(1)
            if not username_len_byte:
                logger.error("No username length byte received")
                return False
            username_len = ord(username_len_byte)
            username = connection.recv(username_len).decode() if username_len else ""

            # Receive password length and password
            password_len_byte = connection.recv(1)
            if not password_len_byte:
                logger.error("No password length byte received")
                return False
            password_len = ord(password_len_byte)
            password = connection.recv(password_len).decode() if password_len else ""

            # Validate credentials
            if username == USERNAME and password == PASSWORD:
                # Success
                logger.info(f"Authenticated user: {username}")
                connection.sendall(b"\x01\x00")  # version 1, status 0 (success)
                return True
            else:
                # Failure
                logger.error(f"Invalid authentication request: {username}")
                connection.sendall(b"\x01\x01")  # version 1, status 1 (failure)
                return False
        except socket.timeout:
            logger.error("Socket timed out waiting for data")
            return False
        except socket.error as e:
            logger.error(f"Socket error during username/password authentication: {e}")
            return False


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
            if address_type == AddressTypeCodes.IPv4.value:
                address = socket.inet_ntoa(connection.recv(4))
            elif address_type == AddressTypeCodes.DOMAIN_NAME.value:
                domain_length = connection.recv(1)[0]
                address = connection.recv(domain_length)
                address = socket.gethostbyname(address)
            elif address_type == AddressTypeCodes.IPv6.value:
                address = socket.inet_ntop(socket.AF_INET6, connection.recv(16))
            else:
                return None, None

            port = struct.unpack("!H", connection.recv(2))[0]
            return address, port
        except socket.error as e:
            logger.error(f"Socket error during address and port parsing: {e}")
            return None, None

    @staticmethod
    def get_address_type(address_type: int) -> AddressTypeCodes | None:
        if address_type == 1:
            return AddressTypeCodes.IPv4
        elif address_type == 3:
            return AddressTypeCodes.DOMAIN_NAME
        elif address_type == 4:
            return AddressTypeCodes.IPv6
        else:
            return None
