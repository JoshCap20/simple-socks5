import struct
import socket
import threading

from ..constants import SOCKS_VERSION, AddressTypeCodes, DNS_REVERSE_LOOKUP_TIMEOUT
from ..exceptions import InvalidRequestError, InvalidVersionError
from ..logger import get_logger
from ..models import DetailedAddress, Request
from ..utils import map_address_int_to_enum

logger = get_logger(__name__)


class BaseHandler:
    connection: socket.socket

    def __init__(self, connection: socket.socket):
        """
        Initializes a new instance of the BaseRequestHandler class.

        Args:
            connection (socket.socket): The client socket.
        """
        self.connection = connection

    def _recv_exact(self, n: int) -> bytes:
        """Receive exactly n bytes from the connection, handling partial reads."""
        buf = bytearray(n)
        pos = 0
        while pos < n:
            chunk = self.connection.recv(n - pos)
            if not chunk:
                raise ConnectionError("Connection closed during recv")
            buf[pos:pos + len(chunk)] = chunk
            pos += len(chunk)
        return bytes(buf)

    def handle_request(self) -> bool:
        """
        Implemented in TCP and UDP request handlers.
        """
        raise NotImplementedError

    def parse_request(self) -> Request:
        """
        Handles requests of the form:

        +----+-----+-------+------+----------+----------+
        |VER | CMD |  RSV  | ATYP | DST.ADDR | DST.PORT |
        +----+-----+-------+------+----------+----------+
        | 1  |  1  | X'00' |  1   | Variable |    2     |
        +----+-----+-------+------+----------+----------+

        o  VER - protocol version: X'05'
        o  CMD
            o  CONNECT X'01'
            o  BIND X'02'
            o  UDP ASSOCIATE X'03'
        o  RSV - RESERVED
        o  ATYP - address type of following address
            o  IP V4 address: X'01'
            o  DOMAINNAME: X'03'
            o  IP V6 address: X'04'
        o  DST.ADDR - desired destination address
        o  DST.PORT - desired destination port in network octet order


        Args:
            connection (socket.socket): The client socket.
        """
        try:
            header = self._recv_exact(4)

            version, cmd, rsv, address_type = struct.unpack("!BBBB", header)
            if version != SOCKS_VERSION:
                raise InvalidVersionError(version)
            if rsv != 0x00:
                raise InvalidRequestError(rsv)

            address: DetailedAddress = self._parse_address(address_type)

            return Request(version=version, command=cmd, address=address)

        except socket.error as e:
            logger.exception(f"Socket error during request parsing: {e}")
            raise

    def _parse_address(self, address_type: int) -> DetailedAddress:
        try:
            if address_type == AddressTypeCodes.IPv4.value:
                address: str = socket.inet_ntoa(self._recv_exact(4))
                domain_name: str = self._gethostbyaddr(address)
            elif address_type == AddressTypeCodes.DOMAIN_NAME.value:
                domain_length = self._recv_exact(1)[0]
                domain_name = self._recv_exact(domain_length).decode()
                address: str = self._gethostbyname(domain_name)
                address_type = AddressTypeCodes.IPv4.value
            elif address_type == AddressTypeCodes.IPv6.value:
                address: str = socket.inet_ntop(
                    socket.AF_INET6, self._recv_exact(16)
                )
                domain_name: str = self._gethostbyaddr(address)
            else:
                raise InvalidRequestError(address_type)

            port: int = struct.unpack("!H", self._recv_exact(2))[0]
            return DetailedAddress(
                name=str(domain_name),
                ip=address,
                port=port,
                address_type=map_address_int_to_enum(address_type),
            )

        except socket.error as e:
            logger.exception(f"Socket error during address and port parsing: {e}")
            raise

    def _gethostbyaddr(self, ip: str) -> str:
        result = [None]
        error = [None]

        def lookup():
            try:
                result[0] = socket.gethostbyaddr(ip)[0]
            except Exception as e:
                error[0] = e

        t = threading.Thread(target=lookup, daemon=True)
        t.start()
        t.join(timeout=DNS_REVERSE_LOOKUP_TIMEOUT)

        if t.is_alive():
            logger.debug(f"Reverse DNS lookup timed out for {ip}")
            return ip
        if error[0] is not None:
            if not isinstance(error[0], OSError):
                logger.exception("Error setting hostname")
            return ip
        return result[0] if result[0] is not None else ip

    def _gethostbyname(self, name: str) -> str:
        result = [None]
        error = [None]

        def lookup():
            try:
                result[0] = socket.gethostbyname(name)
            except Exception as e:
                error[0] = e

        t = threading.Thread(target=lookup, daemon=True)
        t.start()
        t.join(timeout=DNS_REVERSE_LOOKUP_TIMEOUT)

        if t.is_alive():
            logger.debug(f"DNS lookup timed out for {name}")
            return name
        if error[0] is not None:
            if not isinstance(error[0], OSError):
                logger.exception("Error setting hostname")
            return name
        return result[0] if result[0] is not None else name
