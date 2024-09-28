import socket
from socketserver import StreamRequestHandler, ThreadingMixIn, TCPServer

from .constants import CommandCodes
from .handlers import TCPHandler
from .relays import TCPRelay, UDPRelay
from .utils import (
    generate_general_socks_server_failure_reply,
    generate_command_not_supported_reply,
    generate_connection_refused_reply,
    generate_host_unreachable_reply,
    generate_succeeded_reply,
    connection_established_template,
)
from .logger import get_logger
from .models import Request, DetailedAddress

logger = get_logger(__name__)


class ThreadingTCPServer(ThreadingMixIn, TCPServer):
    """
    A threading version of a TCP server.

    https://docs.python.org/3/library/socketserver.html#socketserver.ThreadingMixIn
    """

    daemon_threads = True


class TCPProxyServer(StreamRequestHandler):
    """
    For each connection, a new instance of this class is created.

    https://docs.python.org/3/library/socketserver.html#socketserver.StreamRequestHandler
    """

    client_address: DetailedAddress
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
        request_handler = TCPHandler(self.connection)

        if not request_handler.handle_request():
            logger.error("Handshake failed")
            self.server.shutdown_request(self.request)
            return

        dst_request: Request = request_handler.parse_request()

        self.client_address: DetailedAddress = DetailedAddress(
            *self.connection.getpeername(),
            name="Client",
            address_type=dst_request.address.address_type,
        )
        self._log_connection(dst_request.address)

        reply: bytes | None = None

        try:
            match dst_request.command:
                case CommandCodes.CONNECT.value:
                    # CONNECT
                    reply = self.handle_connect(dst_request.address)

                case CommandCodes.BIND.value:
                    # TODO: BIND
                    reply = self.handle_bind(dst_request.address)

                case CommandCodes.UDP_ASSOCIATE.value:
                    # UDP ASSOCIATE
                    reply = self.handle_udp_associate(dst_request.address)

                case _:
                    # Invalid command
                    reply = generate_command_not_supported_reply()

        except ConnectionRefusedError:
            logger.error(f"Connection refused: {dst_request.address}")
            reply = generate_connection_refused_reply()
        except socket.gaierror:
            logger.error(f"Host unreachable: {dst_request.address}")
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

    def handle_connect(self, dst_address: DetailedAddress) -> None:
        """
        Handles CONNECT command.
        """
        # Allocate port for TCP relay
        tcp_relay = TCPRelay(self.connection, dst_address)

        # Send reply with bind address and port
        success_reply = generate_succeeded_reply(
            dst_address.address_type, *tcp_relay.get_proxy_address()
        )
        self.connection.sendall(success_reply)

        # Start TCP relay
        tcp_relay.listen_and_relay()

    def handle_udp_associate(self, dst_address: DetailedAddress) -> None:
        """
        Handles UDP ASSOCIATE command.
        """
        # Allocate port for UDP relay
        udp_relay = UDPRelay(self.connection, dst_address)

        # Send reply with allocated port and server IP
        success_reply = generate_succeeded_reply(
            dst_address.address_type, *udp_relay.get_proxy_address()
        )
        self.connection.sendall(success_reply)

        # Start UDP relay
        udp_relay.listen_and_relay()

    def handle_bind(self, address: DetailedAddress) -> bytes:
        """
        Handles BIND command.
        """
        logger.error("BIND command not supported")
        return generate_command_not_supported_reply()

    def finish(self):
        """
        Called after handle() to perform any clean-up actions required.

        Ensures proper closure of each socket.
        """
        try:
            self.connection.shutdown(socket.SHUT_RDWR)
        except socket.error:
            pass  # Handle already closed socket
        finally:
            self.connection.close()

    def _log_connection(self, dst_address: DetailedAddress) -> None:
        """
        Logs connection.
        """
        logger.info(
            connection_established_template.substitute(
                src_domain_name=self.client_address.name,
                src_ip=self.client_address.ip,
                src_port=self.client_address.port,
                dst_domain_name=dst_address.name,
                dst_ip=dst_address.ip,
                dst_port=dst_address.port,
            )
        )
