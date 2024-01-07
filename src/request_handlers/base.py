import struct
import socket

from ..constants import SOCKS_VERSION, AddressTypeCodes
from ..exceptions import InvalidRequestError, InvalidVersionError
from ..logger import get_logger
from ..models import Address, Request
from ..utils import map_address_type_to_enum

logger = get_logger(__name__)


class BaseRequestHandler:
    connection: socket.socket

    def __init__(self, connection: socket.socket):
        """
        Initializes a new instance of the BaseRequestHandler class.

        Args:
            connection (socket.socket): The client socket.
        """
        self.connection = connection

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
        o  DST.PORT -desired destination port in network octet order


        Args:
            connection (socket.socket): The client socket.
        """
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
                    address: str = self._gethostbyname(domain_name)
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

    def _gethostbyname(self, name: str) -> str:
        try:
            return socket.gethostbyname(name)
        except OSError:
            return name
        except Exception as e:
            logger.exception("Error setting hostname")
            return name
