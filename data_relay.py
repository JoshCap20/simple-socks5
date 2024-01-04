import sys
import select
import socket


class DataRelay:
    @staticmethod
    def relay_data(client_socket: socket.socket, remote_socket: socket.socket) -> None:
        try:
            while True:
                # Wait until client or remote is available for read
                r, w, e = select.select([client_socket, remote_socket], [], [])

                if client_socket in r:
                    data = client_socket.recv(4096)
                    if remote_socket.send(data) <= 0:
                        break

                if remote_socket in r:
                    data = remote_socket.recv(4096)
                    if client_socket.send(data) <= 0:
                        break

        except BrokenPipeError as e:
            print(f"Caught BrokenPipeError: {e}", file=sys.stderr)
        except ConnectionResetError as e:
            print(f"Caught ConnectionResetError: {e}", file=sys.stderr)
        finally:
            client_socket.close()
            remote_socket.close()
