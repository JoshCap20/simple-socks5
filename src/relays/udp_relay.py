import socket
import struct

from ..models import Address


class UDPRelay:
    udp_socket: socket.socket
    address: Address

    def __init__(self, address: Address):
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind(("", 0))  # Bind to any available port
        self.relay_port = self.udp_socket.getsockname()[1]  # Get the allocated port
        self.address = address

    def listen_and_relay(self):
        while True:
            data, addr = self.udp_socket.recvfrom(4096)
            if not data:
                break

            # Parse the SOCKS UDP request header
            rsv, frag, atyp = struct.unpack("!HBB", data[:4])

            # Forward the data to the actual destination

            # Receive response and send back to client

    def get_allocated_port(self) -> int:
        return self.relay_port
