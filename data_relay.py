import select
import socket
from logger import logger


class DataRelay:
    @staticmethod
    def relay_data(client_socket: socket.socket, remote_socket: socket.socket) -> None:
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
                            f"Closing connection: {sock.getpeername()} <-> {other_address}"
                        )
                        return
                    while data:
                        sent: int = other_sock.send(data)
                        logger.info(
                            f"Data relayed: {sock.getpeername()} -> {other_address}, Size: {len(data)} bytes"
                        )
                        data = data[sent:]

        except BrokenPipeError as e:
            logger.error(f"Caught BrokenPipeError: {e}")
        except ConnectionResetError as e:
            logger.error(f"Caught ConnectionResetError: {e}")
        finally:
            for sock in [client_socket, remote_socket]:
                try:
                    sock.shutdown(socket.SHUT_RDWR)
                except Exception as e:
                    pass
                finally:
                    sock.close()
