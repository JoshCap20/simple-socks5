import socket

from ..logger import get_logger
from ..models import Address
from ..request_handlers import UDPRequestHandler

logger = get_logger(__name__)


class UDPRelay:
    udp_socket: socket.socket
    request_handler: UDPRequestHandler
    address: Address

    def __init__(self, address: Address):
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind(("", 0))  # Bind to any available port
        self.request_handler = UDPRequestHandler(self.udp_socket)
        self.relay_port = self.udp_socket.getsockname()[1]  # Get the allocated port
        self.address = address

    def listen_and_relay(self):
        # TODO: Refactor this later to make code cleaner
        while True:
            (
                data,
                addr,
                frag,
                atyp,
                dst_addr,
                dst_port,
                user_data,
            ) = self.request_handler.handle_request()

            # Forward the data to the actual destination
            forward_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            forward_socket.sendto(user_data, (dst_addr, dst_port))

            logger.debug(
                f"Data relayed: {addr} -> {dst_addr}:{dst_port}, Size: {len(user_data)} bytes"
            )

            # Receive response and send back to client
            response, _ = forward_socket.recvfrom(4096)

            # Send response back to client
            self.udp_socket.sendto(response, addr)

            logger.debug(
                f"Data relayed: {dst_addr}:{dst_port} -> {addr}, Size: {len(response)} bytes"
            )

            forward_socket.close()

    def get_allocated_port(self) -> int:
        return self.relay_port
