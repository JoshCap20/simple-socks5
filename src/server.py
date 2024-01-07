import socket
from socketserver import StreamRequestHandler

from .constants import CommandCodes
from .request_handlers import TCPRequestHandler
from .relays import TCPRelay
from .utils import (
    generate_general_socks_server_failure_reply,
    generate_command_not_supported_reply,
    generate_connection_refused_reply,
    generate_host_unreachable_reply,
    generate_succeeded_reply,
    generate_socket,
)
from .logger import get_logger
from .models import Request, Address
from socketserver import ThreadingMixIn, TCPServer

logger = get_logger(__name__)


class ThreadingTCPServer(ThreadingMixIn, TCPServer):
    """
    A threading version of a TCP server.

    https://docs.python.org/3/library/socketserver.html#socketserver.ThreadingMixIn
    """

    pass


class TCPProxyServer(StreamRequestHandler):
    """
    For each connection, a new instance of this class is created.

    https://docs.python.org/3/library/socketserver.html#socketserver.StreamRequestHandler
    """

    connection: socket.socket
    server: ThreadingTCPServer

    def handle(self):
        """
        This function must do all the work required to service a request.

        Available:
            connection: The new socket.socket object to be used to communicate with the client.
            client_address: Client address returned by BaseServer.get_request().
            server: BaseServer object used for handling the request.
        """
        request_handler = TCPRequestHandler(self.connection)

        if not request_handler.handle_request():
            logger.error("Handshake failed")
            self.server.shutdown_request(self.request)
            return

        conn_request: Request = request_handler.parse_request()

        reply: bytes | None = None

        logger.info(
            f"Connection Established: {conn_request.address.name}, {conn_request.address.ip}, {conn_request.address.port}, {conn_request.address.address_type}"
        )

        try:
            match conn_request.command:
                case CommandCodes.CONNECT.value:
                    # CONNECT
                    reply = self.handle_connect(conn_request.address)

                case CommandCodes.BIND.value:
                    # TODO: BIND
                    reply = self.handle_bind(conn_request.address)

                case CommandCodes.UDP_ASSOCIATE.value:
                    # TODO: UDP ASSOCIATE
                    print(conn_request)
                    reply = self.handle_udp_associate(conn_request.address)

                case _:
                    # Invalid command
                    reply = generate_command_not_supported_reply()

        except ConnectionRefusedError:
            logger.error(
                f"Connection refused: {conn_request.address.name}, {conn_request.address.ip}:{conn_request.address.port}"
            )
            reply = generate_connection_refused_reply()
        except socket.gaierror:
            logger.error(
                f"Host unreachable: {conn_request.address.name}, {conn_request.address.ip}:{conn_request.address.port}"
            )
            reply = generate_host_unreachable_reply()
        except Exception as e:
            logger.error(f"Exception: {e}")
            reply = generate_general_socks_server_failure_reply()

        finally:
            if reply is not None:
                try:
                    self.connection.sendall(reply)
                except BrokenPipeError as e:
                    logger.error(f"Error sending reply: {e}")
            self.server.shutdown_request(self.request)

    def handle_connect(self, address: Address) -> None:
        """
        Handles CONNECT command.
        """
        remote: socket.socket = generate_socket(address)
        remote.connect((address.ip, address.port))
        bind_address: socket._RetAddress = remote.getsockname()

        success_reply = generate_succeeded_reply(
            address.address_type, bind_address[0], bind_address[1]
        )
        self.connection.sendall(success_reply)

        TCPRelay.relay_data(self.connection, remote, address, bind_address)

    def handle_bind(self, address: Address) -> bytes:
        """
        Handles BIND command.
        """
        logger.error("BIND command not supported")
        return generate_command_not_supported_reply()

    def handle_udp_associate(self, address: Address) -> bytes:
        """
        Handles UDP ASSOCIATE command.
        """
        logger.error("UDP ASSOCIATE command not supported")
        return generate_command_not_supported_reply()

    def finish(self):
        """
        Called after handle() to perform any clean-up actions required.
        """
        self.connection.close()
