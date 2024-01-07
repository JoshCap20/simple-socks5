import select
import socket


from .base import BaseRelay
from ..models import Address
from ..logger import get_logger
from ..utils import generate_tcp_socket

logger = get_logger(__name__)


class TCPRelay(BaseRelay):
    """
    Class responsible for relaying data between a client socket and a remote socket via TCP.
    """

    def __init__(self, client_connection: socket.socket, dst_address: Address):
        """
        Initializes a new instance of the TCPRelay class.

        Args:
            connection (socket.socket): The client socket.
            dst_address (Address): The address to connect to.
        """
        super().__init__(client_connection, dst_address)
        self.generate_proxy_connection()

    def generate_proxy_connection(self) -> None:
        """
        Generates a new proxy connection.
        """
        self.proxy_connection = generate_tcp_socket(self.dst_address.address_type)
        self.proxy_connection.connect((self.dst_address.ip, self.dst_address.port))
        self.set_proxy_address()

    def listen_and_relay(self) -> None:
        """
        Relays data between the client socket and the remote socket.
        """

        try:
            while True:
                # Wait until client or remote is available for read
                readable_sockets, _, _ = select.select(
                    [self.client_connection, self.proxy_connection], [], []
                )

                for sock in readable_sockets:
                    # Determine which socket is available for read
                    other_sock = (
                        self.proxy_connection
                        if sock is self.client_connection
                        else self.client_connection
                    )

                    # Metadata for logging
                    other_info: Address = (
                        self.get_dst_address()
                        if sock is self.client_connection
                        else self.get_client_address()
                    )
                    sock_info: Address = (
                        self.get_client_address()
                        if sock is self.client_connection
                        else self.get_dst_address()
                    )

                    # Receive data from socket
                    data: bytes = sock.recv(4096)

                    if not data:
                        # No data received, connection closed
                        logger.info(f"Connection closed: {sock_info} <-> {other_info}")
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
            for sock in [self.client_connection, self.proxy_connection]:
                sock.close()
