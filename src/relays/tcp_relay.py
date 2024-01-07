import select
import socket
from functools import lru_cache

from ..models import Address
from ..logger import get_logger
from ..utils import generate_socket

logger = get_logger(__name__)


class TCPRelay:
    """
    Class responsible for relaying data between a client socket and a remote socket.
    """

    connection: socket.socket
    tcp_socket: socket.socket
    address: Address
    bind_address: tuple[str, int]

    def __init__(self, connection: socket.socket, address: Address):
        """
        Initializes a new instance of the TCPRelay class.

        Args:
            address (Address): The address to connect to.
        """
        self.connection = connection
        self.address = address
        self.tcp_socket = generate_socket(address)
        self.tcp_socket.connect((address.ip, address.port))
        self.bind_address = self.tcp_socket.getsockname()

    def listen_and_relay(self) -> None:
        """
        Relays data between the client socket and the remote socket.
        """
        # Metadata for logging
        client_info: dict[str, str | int] = TCPRelay.resolve_address_info(
            ip=self.bind_address[0], port=self.bind_address[1]
        )

        remote_info: dict[str, str | int] = {
            "domain": self.address.name,
            "ip": self.tcp_socket.getpeername()[0],
            "port": self.address.port,
        }

        try:
            while True:
                # Wait until client or remote is available for read
                readable_sockets, _, _ = select.select(
                    [self.connection, self.tcp_socket], [], []
                )

                for sock in readable_sockets:
                    # Determine which socket is available for read
                    other_sock = (
                        self.tcp_socket if sock is self.connection else self.connection
                    )

                    # Metadata for logging
                    other_info = remote_info if sock is self.connection else client_info
                    sock_info = client_info if sock is self.connection else remote_info

                    # Receive data from socket
                    data: bytes = sock.recv(4096)

                    if not data:
                        # No data received, connection closed
                        logger.info(
                            f"Connection closed: {client_info} <-> {remote_info}"
                        )
                        return

                    while data:
                        # Send data loop to other socket
                        sent: int = other_sock.send(data)
                        logger.debug(
                            f"Data relayed: {sock_info} -> {other_info}, Size: {len(data)} bytes"
                        )
                        data = data[sent:]

        except BrokenPipeError as e:
            logger.exception(f"Broken Pipe: {e}")
        except ConnectionResetError as e:
            logger.exception(f"Connection Reset: {e}")
        finally:
            for sock in [self.connection, self.tcp_socket]:
                try:
                    sock.shutdown(socket.SHUT_RDWR)
                except Exception as e:
                    pass
                finally:
                    sock.close()

    @staticmethod
    @lru_cache(maxsize=1024)
    def resolve_address_info(ip: str, port: int) -> dict[str, str | int]:
        """
        Resolves the domain name, IP, and port from a given address.
        Supports both IPv4 and IPv6 addresses.
        """
        try:
            domain_name = socket.gethostbyaddr(ip)[0]
        except socket.herror:
            domain_name = "Unknown"

        return {"domain": domain_name, "ip": ip, "port": port}

    def get_allocated_address(self) -> tuple[str, int]:
        """
        Returns the allocated address and port.
        """
        return self.bind_address
