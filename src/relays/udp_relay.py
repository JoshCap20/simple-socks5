import socket
import struct

from .base import BaseRelay
from ..models import Address
from ..logger import get_logger
from ..request_handlers import UDPRequestHandler
from ..utils import generate_udp_socket, map_address_int_to_socket_family

logger = get_logger(__name__)


class UDPRelay(BaseRelay):
    """
    Class responsible for relaying data between a client socket and a remote socket via UDP.
    """

    def __init__(self, client_connection: socket.socket, dst_address: Address):
        """
        Initializes a new instance of the UDPRelay class.

        Args:
            client_connection (socket.socket): The client socket.
            dst_address (Address): The destination address.
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

            # Extract the address type from the data
            rsv, frag, atyp = struct.unpack("!HBB", data[:4])

            # Extract the destination address and port from the data
            dst_addr, dst_port, user_data = self.extract_destination_info(data, atyp)

            # Forward the data to the actual destination
            with socket.socket(
                map_address_int_to_socket_family(atyp), socket.SOCK_DGRAM
            ) as forward_socket:
                forward_socket.sendto(user_data, (dst_addr, dst_port))
                logger.debug(
                    f"Data relayed: {addr} -> {dst_addr}:{dst_port}, Size: {len(user_data)} bytes"
                )

                response, _ = forward_socket.recvfrom(4096)
                self.proxy_connection.sendto(response, addr)
                logger.debug(
                    f"Data relayed: {dst_addr}:{dst_port} -> {addr}, Size: {len(response)} bytes"
                )

    def extract_destination_info(self, data, atyp):
        """
        Extracts destination address, port, and user data from UDP packet.
        """
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
            raise ValueError("Invalid ATYP value in UDP packet")

        return dst_addr, dst_port, user_data
