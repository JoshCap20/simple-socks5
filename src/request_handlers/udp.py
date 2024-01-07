import socket

from .base import BaseRequestHandler
from ..logger import get_logger

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

    def handle_request(self):
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
        pass
