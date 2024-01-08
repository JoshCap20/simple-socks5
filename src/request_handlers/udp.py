import socket
import struct

from .base import BaseRequestHandler
from ..logger import get_logger
from ..exceptions import InvalidRequestError
from ..models import UDPDatagram
from ..utils import map_address_int_to_enum

logger = get_logger(__name__)


class UDPRequestHandler(BaseRequestHandler):
    connection: socket.socket

    def __init__(self, connection: socket.socket):
        """
        Initializes a new instance of the UDPRequestHandler class.

        Args:
            connection (socket.socket): The client socket.
        """
        self.connection = connection

    @staticmethod
    def parse_udp_datagram(data: bytes) -> UDPDatagram:
        """
        Procedure for UDP-based clients per RFC 1928.

        +----+------+------+----------+----------+----------+
        |RSV | FRAG | ATYP | DST.ADDR | DST.PORT |   DATA   |
        +----+------+------+----------+----------+----------+
        | 2  |  1   |  1   | Variable |    2     | Variable |
        +----+------+------+----------+----------+----------+

        o  RSV - Reserved X'0000'
        o  FRAG - Current fragment number
        o  ATYP - address type of following addresses:
            o  IP V4 address: X'01'
            o  DOMAINNAME: X'03'
            o  IP V6 address: X'04'
        o  DST.ADDR - desired destination address
        o  DST.PORT - desired destination port
        o  DATA - user data
        """

        # Parse the SOCKS UDP request header
        rsv, frag, atyp = struct.unpack("!HBB", data[:4])

        if atyp == 1:  # IPv4
            dst_addr = socket.inet_ntoa(data[4:8])
            dst_port = struct.unpack("!H", data[8:10])[0]
            user_data = data[10:]
        elif atyp == 3:  # Domain name
            domain_length = data[4]
            dst_addr = data[5 : 5 + domain_length].decode()
            dst_port = struct.unpack("!H", data[5 + domain_length : 7 + domain_length])[
                0
            ]
            user_data = data[7 + domain_length :]
        elif atyp == 4:  # IPv6
            dst_addr = socket.inet_ntop(socket.AF_INET6, data[4:20])
            dst_port = struct.unpack("!H", data[20:22])[0]
            user_data = data[22:]
        else:
            raise InvalidRequestError(atyp)

        return UDPDatagram(
            frag=frag,
            address_type=map_address_int_to_enum(atyp),
            dst_addr=dst_addr,
            dst_port=dst_port,
            data=user_data,
        )
