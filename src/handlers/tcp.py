import struct
import socket

from .base import BaseHandler
from ..constants import SOCKS_VERSION, MethodCodes, USERNAME, PASSWORD
from ..exceptions import InvalidVersionError
from ..logger import get_logger
from ..utils import generate_connection_method_response

logger = get_logger(__name__)


class TCPHandler(BaseHandler):
    connection: socket.socket

    def __init__(self, connection: socket.socket):
        """
        Initializes a new instance of the TCPRequestHandler class.

        Args:
            connection (socket.socket): The client socket.
        """
        self.connection = connection

    def handle_request(self) -> bool:
        """
        Procedure for TCP-based clients per RFC 1928.

        Handles authentication negotation.

        Client request:
            +----+----------+----------+
            |VER | NMETHODS | METHODS  |
            +----+----------+----------+
            | 1  |    1     | 1 to 255 |
            +----+----------+----------+
        Server response:
            +----+--------+
            |VER | METHOD |
            +----+--------+
            | 1  |   1    |
            +----+--------+

        Methods:
            o  X'00' NO AUTHENTICATION REQUIRED
            o  X'01' GSSAPI
            o  X'02' USERNAME/PASSWORD
            o  X'03' to X'7F' IANA ASSIGNED
            o  X'80' to X'FE' RESERVED FOR PRIVATE METHODS
            o  X'FF' NO ACCEPTABLE METHODS

        Returns:
            bool: True if the handshake was successful, False otherwise.
        """
        try:
            # Parses client VER, NMETHODS, METHODS
            header = self.connection.recv(2)
            if len(header) < 2:
                return False

            version, nmethods = struct.unpack("!BB", header)

            if version != SOCKS_VERSION:
                raise InvalidVersionError(version)

            methods = self.connection.recv(nmethods)

            # Handles negotiation for authentication method
            negotiated_authentication: MethodCodes = (
                self._negotiate_authentication_method(methods)
            )

            # Handles server response
            self.connection.sendall(
                generate_connection_method_response(negotiated_authentication)
            )

            # Handles authentication
            if negotiated_authentication == MethodCodes.NO_AUTHENTICATION_REQUIRED:
                return True
            elif negotiated_authentication == MethodCodes.USERNAME_PASSWORD:
                return self._handle_username_password_auth()
            elif negotiated_authentication == MethodCodes.GSSAPI:
                # Not implemented yet
                return self._handle_gssapi_auth()
            else:
                logger.warn("No acceptable authentication methods")
                return False

        except socket.error as e:
            logger.exception(f"Socket error during handshake: {e}")
            return False

    def _negotiate_authentication_method(self, methods: bytes) -> MethodCodes:
        """
        Finds the a mutually supported authentication method.
        USERNAME/PASSWORD is the preferred method.

        Args:
            methods (bytes): The methods sent by the client.

        Returns:
            MethodCodes: The negotiated authentication method.
        """
        client_methods = {method for method in methods}

        supported_methods = {
            MethodCodes.NO_AUTHENTICATION_REQUIRED.value,
            MethodCodes.USERNAME_PASSWORD.value,
        }

        mutual_method = client_methods.intersection(supported_methods)

        if MethodCodes.USERNAME_PASSWORD.value in mutual_method:
            return MethodCodes.USERNAME_PASSWORD
        # TODO: Implement GSS-API authentication
        elif MethodCodes.NO_AUTHENTICATION_REQUIRED.value in mutual_method:
            return MethodCodes.NO_AUTHENTICATION_REQUIRED
        else:
            # No acceptable methods
            return MethodCodes.NO_ACCEPTABLE_METHODS

    def _handle_username_password_auth(self) -> bool:
        """
        Handles USERNAME/PASSWORD authentication method.

        Client request:
            +----+------+----------+------+----------+
            |VER | ULEN |  UNAME   | PLEN |  PASSWD  |
            +----+------+----------+------+----------+
            | 1  |  1   | 1 to 255 |  1   | 1 to 255 |
            +----+------+----------+------+----------+
        Server response:
            +----+--------+
            |VER | STATUS |
            +----+--------+
            | 1  |   1    |
            +----+--------+

        Fields
            o VER - subnegotiation protocol version (1 byte): X'01'
            o ULEN - username length (1 byte)
            o UNAME - username
            o PLEN - password length (1 byte)
            o PASSWD - password
            o STATUS - status code (1 byte): X'00' for success, X'01' for failure
                - Connection must be closed if status is not X'00'
        """
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

    def _handle_gssapi_auth(self) -> bool:
        """
        GSS-API method implementation per RFC 1961.
        """
        logger.warn("GSS-API authentication method not implemented")
        return False
