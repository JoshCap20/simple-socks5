import select
import socket
from logger import logger


class DataRelay:
    @staticmethod
    def relay_data(client_socket: socket.socket, remote_socket: socket.socket) -> None:
        try:
            while True:
                # Wait until client or remote is available for read
                a, b, c = select.select([client_socket, remote_socket], [], [])

                if client_socket in a:
                    data = client_socket.recv(4096)
                    if remote_socket.send(data) <= 0:
                        break

                if remote_socket in a:
                    data = remote_socket.recv(4096)
                    if client_socket.send(data) <= 0:
                        break

        except BrokenPipeError as e:
            logger.error(f"Caught BrokenPipeError: {e}")
        except ConnectionResetError as e:
            logger.error(f"Caught ConnectionResetError: {e}")
        finally:
            client_socket.close()
            remote_socket.close()
