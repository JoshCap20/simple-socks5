import socket

from .base import BaseRelay
from ..models import DetailedAddress, BaseAddress
from ..logger import get_logger
from ..handlers import UDPHandler
from ..utils import (
    generate_udp_socket,
    map_address_enum_to_socket_family,
    base_relay_template,
)

logger = get_logger(__name__)


class UDPRelay(BaseRelay):
    """
    Class responsible for relaying data between a client socket and a remote socket via UDP.
    """

    def __init__(self, client_connection: socket.socket, dst_address: DetailedAddress):
        """
        Initializes a new instance of the UDPRelay class.

        Args:
            client_connection (socket.socket): The client socket.
            dst_address (DetailedAddress): The destination address.
        """
        super().__init__(client_connection, dst_address)
        self.generate_proxy_connection()

    def generate_proxy_connection(self) -> None:
        """
        Generates a new proxy connection.
        """
        self.proxy_connection = generate_udp_socket(self.dst_address.address_type)
        self.proxy_connection.bind(("", 0))  # Bind to any available port
        self.set_proxy_address()

    def listen_and_relay(self):
        """
        Listens for incoming UDP packets and relays them to the actual destination.
        """
        # TODO: Refactor this later to make code cleaner
        while True:
            # Receive data from the client
            data, addr = self.proxy_connection.recvfrom(4096)
            if not data:
                break

            # Extract the UDP datagram
            datagram = UDPHandler.parse_udp_datagram(data)

            if datagram.frag != 0:
                # Per RFC 1928, "an implementation that does not support fragmentation MUST drop any datagram whose FRAG field is other than X'00'."
                logger.debug(
                    f"(UDP) Dropped datagram: {addr} -> {datagram.dst_addr}:{datagram.dst_port}, Size: {len(datagram.data)} bytes"
                )
                continue

            # Forward the data to the actual destination
            with socket.socket(
                map_address_enum_to_socket_family(datagram.address_type),
                socket.SOCK_DGRAM,
            ) as forward_socket:
                forward_socket.sendto(
                    datagram.data, (datagram.dst_addr, datagram.dst_port)
                )
                self._log_relay(
                    BaseAddress(addr[0], addr[1]),
                    BaseAddress(datagram.dst_addr, datagram.dst_port),
                    len(datagram.data),
                )

                response, _ = forward_socket.recvfrom(4096)
                self.proxy_connection.sendto(response, addr)
                self._log_relay(
                    BaseAddress(datagram.dst_addr, datagram.dst_port),
                    BaseAddress(addr[0], addr[1]),
                    len(response),
                )

    def _log_relay(self, src_addr: BaseAddress, dst_addr: BaseAddress, data_len: int):
        """
        Logs the relay of data between the client and the destination.

        Args:
            src_addr (BaseAddress): The source socket information.
            dst_addr (BaseAddress): The destination socket information.
            data_len (int): The length of the data sent.
        """
        logger.debug(
            base_relay_template.substitute(
                protocol="UDP",
                src_ip=src_addr.ip,
                src_port=src_addr.port,
                dst_ip=dst_addr.ip,
                dst_port=dst_addr.port,
                data_size=data_len,
            )
        )
