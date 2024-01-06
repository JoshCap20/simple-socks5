import os
import select
import socket

from .logger import get_logger

verbose = os.environ.get("VERBOSE", "0") == "1"
logger = get_logger(__name__, verbose=verbose)


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

        try:
            while True:
                # Wait until client or remote is available for read
                readable_sockets, _, _ = select.select(
                    [client_socket, remote_socket], [], []
                )

                for sock in readable_sockets:
                    other_sock: socket.socket = (
                        remote_socket if sock is client_socket else client_socket
                    )
                    other_address: socket._RetAddress = (
                        remote_address if sock is client_socket else client_address
                    )

                    data: bytes = sock.recv(4096)
                    if not data:
                        logger.info(
                            f"Connection Closed: {sock.getpeername()} <-> {other_address}"
                        )
                        return
                    while data:
                        sent: int = other_sock.send(data)
                        logger.debug(
                            f"Data relayed: {sock.getpeername()} -> {other_address}, Size: {len(data)} bytes"
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
