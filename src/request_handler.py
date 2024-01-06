import struct
import socket

from .constants import SOCKS_VERSION, AddressTypeCodes, MethodCodes, USERNAME, PASSWORD
from .exceptions import InvalidRequestError, InvalidVersionError
from .logger import get_logger
from .models import Address, Request
from .utils import map_address_type_to_enum

logger = get_logger(__name__)


class RequestHandler:
    connection: socket.socket
    client_authenticated: bool

    def __init__(self, connection: socket.socket):
        self.connection = connection
        self.client_authenticated = False

    def handle_handshake(self) -> bool:
        try:
            header = self.connection.recv(2)
            if len(header) < 2:
                return False

            version, nmethods = struct.unpack("!BB", header)

            if version != SOCKS_VERSION:
                return False

            methods = self.connection.recv(nmethods)

            # Authentication
            self.client_authenticated = self._authenticate(methods)
            return self.client_authenticated
        except socket.error as e:
            logger.exception(f"Socket error during handshake: {e}")
            return False

    def _authenticate(self, methods: bytes) -> bool:
        client_methods = {method for method in methods}

        supported_methods = {
            MethodCodes.NO_AUTHENTICATION_REQUIRED.value,
            MethodCodes.USERNAME_PASSWORD.value,
        }

        mutual_method = client_methods.intersection(supported_methods)

        if MethodCodes.USERNAME_PASSWORD.value in mutual_method:
            self.connection.sendall(
                struct.pack("!BB", SOCKS_VERSION, MethodCodes.USERNAME_PASSWORD.value)
            )
            return self._handle_username_password_auth()
        elif MethodCodes.NO_AUTHENTICATION_REQUIRED.value in mutual_method:
            self.connection.sendall(
                struct.pack(
                    "!BB", SOCKS_VERSION, MethodCodes.NO_AUTHENTICATION_REQUIRED.value
                )
            )
            return True
        else:
            # No acceptable methods
            self.connection.sendall(
                struct.pack(
                    "!BB", SOCKS_VERSION, MethodCodes.NO_ACCEPTABLE_METHODS.value
                )
            )
            return False

    def _handle_username_password_auth(self) -> bool:
        self.connection.settimeout(45.0)
        try:
            # Receive and verify the version
            version = self.connection.recv(1)
            if not version or version != b"\x01":
                logger.error(f"Incorrect subnegotiation version: {version}")
                self.connection.sendall(b"\x01\x01")
                return False

            # Receive username length and username
            username_len_byte = self.connection.recv(1)
            if not username_len_byte:
                logger.error("No username length byte received")
                self.connection.sendall(b"\x01\x01")
                return False
            username_len = ord(username_len_byte)
            username = (
                self.connection.recv(username_len).decode() if username_len else ""
            )

            # Receive password length and password
            password_len_byte = self.connection.recv(1)
            if not password_len_byte:
                logger.error("No password length byte received")
                self.connection.sendall(b"\x01\x01")
                return False
            password_len = ord(password_len_byte)
            password = (
                self.connection.recv(password_len).decode() if password_len else ""
            )

            # Validate credentials
            if username == USERNAME and password == PASSWORD:
                # Success
                logger.info(f"Authenticated user: {username}")
                self.connection.sendall(b"\x01\x00")  # version 1, status 0 (success)
                return True
            else:
                # Failure
                logger.warn(f"Invalid authentication request: {username}")
                self.connection.sendall(b"\x01\x01")  # version 1, status 1 (failure)
                return False
        except socket.timeout:
            logger.exception("Socket timed out waiting for data")
            return False
        except socket.error as e:
            logger.exception(
                f"Socket error during username/password authentication: {e}"
            )
            return False

    def parse_request(self) -> Request:
        try:
            header = self.connection.recv(4)
            if len(header) < 4:
                raise InvalidRequestError(header)

            version, cmd, _, address_type = struct.unpack("!BBBB", header)
            if version != SOCKS_VERSION:
                raise InvalidVersionError(version)

            address: Address = self._parse_address(address_type)

            return Request(version=version, command=cmd, address=address)

        except socket.error as e:
            logger.exception(f"Socket error during request parsing: {e}")
            raise socket.error(e)

    def _parse_address(self, address_type: int) -> Address:
        try:
            match address_type:
                case AddressTypeCodes.IPv4.value:
                    address: str = socket.inet_ntoa(self.connection.recv(4))
                    domain_name: str = self._gethostbyaddr(address)
                case AddressTypeCodes.DOMAIN_NAME.value:
                    domain_length = self.connection.recv(1)[0]
                    domain_name = self.connection.recv(domain_length)
                    address: str = socket.gethostbyname(domain_name)
                    address_type = AddressTypeCodes.IPv4.value
                case AddressTypeCodes.IPv6.value:
                    address: str = socket.inet_ntop(
                        socket.AF_INET6, self.connection.recv(16)
                    )
                    domain_name: str = self._gethostbyaddr(address)
                case _:
                    raise InvalidRequestError(address_type)

            port: int = struct.unpack("!H", self.connection.recv(2))[0]
            return Address(
                name=domain_name,
                ip=address,
                port=port,
                address_type=map_address_type_to_enum(address_type),
            )

        except socket.error as e:
            logger.exception(f"Socket error during address and port parsing: {e}")
            raise socket.error(e)

    def _gethostbyaddr(self, ip: str) -> str:
        try:
            return socket.gethostbyaddr(ip)[0]
        except OSError:
            return ip
        except Exception as e:
            logger.exception("Error setting hostname")
            return ip