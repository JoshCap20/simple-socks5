import select
import socket
from logger import logger


class DataRelay:
    @staticmethod
    def relay_data(client_socket: socket.socket, remote_socket: socket.socket) -> None:
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
                    data: bytes = sock.recv(4096)
                    if not data:
                        logger.info("Connection closed by the remote host.")
                        return
                    while data:
                        sent = other_sock.send(data)
                        data = data[sent:]

        except BrokenPipeError as e:
            logger.error(f"Caught BrokenPipeError: {e}")
        except ConnectionResetError as e:
            logger.error(f"Caught ConnectionResetError: {e}")
        finally:
            client_socket.close()
            remote_socket.close()
