import select
import socket
from functools import lru_cache

from .logger import get_logger

logger = get_logger(__name__)


class DataRelay:
    """
    Class responsible for relaying data between a client socket and a remote socket.
    """

    @staticmethod
    def relay_data(client_socket: socket.socket, remote_socket: socket.socket) -> None:
        """
        Relays data between the client socket and the remote socket.

        Args:
            client_socket (socket.socket): The client socket.
            remote_socket (socket.socket): The remote socket.

        Returns:
            None
        """
        client_address: socket._RetAddress = client_socket.getpeername()
        remote_address: socket._RetAddress = remote_socket.getpeername()

        client_info = DataRelay.resolve_address_info(*client_address)
        remote_info = DataRelay.resolve_address_info(*remote_address)

        try:
            while True:
                # Wait until client or remote is available for read
                readable_sockets, _, _ = select.select(
                    [client_socket, remote_socket], [], []
                )

                for sock in readable_sockets:
                    other_sock = (
                        remote_socket if sock is client_socket else client_socket
                    )
                    other_info = remote_info if sock is client_socket else client_info
                    sock_info = client_info if sock is client_socket else remote_info

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
            for sock in [client_socket, remote_socket]:
                try:
                    sock.shutdown(socket.SHUT_RDWR)
                except Exception as e:
                    pass
                finally:
                    sock.close()

    @staticmethod
    @lru_cache(maxsize=1024)
    def resolve_address_info(ip: str, port: int) -> dict:
        """
        Resolves the domain name, IP, and port from a given address.
        Supports both IPv4 and IPv6 addresses.
        """
        try:
            domain_name = socket.gethostbyaddr(ip)[0]
        except socket.herror:
            domain_name = "Unknown"

        return {"domain": domain_name, "ip": ip, "port": port}
