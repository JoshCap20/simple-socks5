import struct
import socket
from socketserver import ThreadingMixIn, TCPServer, StreamRequestHandler

from constants import SOCKS_VERSION, AddressTypeCodes
from request_handler import RequestHandler
from data_relay import DataRelay
from utils import (
    generate_general_socks_server_failure_reply,
    generate_command_not_supported_reply,
    generate_connection_refused_reply,
    generate_host_unreachable_reply,
    generate_succeeded_reply,
)
from logger import logger


class ThreadingTCPServer(ThreadingMixIn, TCPServer):
    """A threading version of TCP server."""

    pass


class SocksProxy(StreamRequestHandler):
    connection: socket.socket

    def handle(self):
        if not RequestHandler.handle_handshake(self.connection):
            return

        version, cmd, address_type = RequestHandler.parse_request(self.connection)
        if version != SOCKS_VERSION:
            return

        address, port = RequestHandler.parse_address_and_port(
            self.connection, address_type
        )

        reply: bytes | None = None

        try:
            if cmd == 1:
                # CONNECT
                remote: socket.socket = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM
                )
                remote.connect((address, port))
                bind_address: socket._RetAddress = remote.getsockname()

                success_reply = generate_succeeded_reply(
                    AddressTypeCodes.IPv4, bind_address[0], bind_address[1]
                )
                self.connection.sendall(success_reply)

                DataRelay.relay_data(self.connection, remote)
            elif cmd == 2:
                # TODO: Implement BIND
                reply = generate_command_not_supported_reply()
            elif cmd == 3:
                # TODO: Implement UDP ASSOCIATE
                reply = generate_command_not_supported_reply()
            else:
                # Invalid command
                reply = generate_command_not_supported_reply()

        except ConnectionRefusedError:
            logger.error("Connection refused")
            reply = generate_connection_refused_reply()
        except socket.gaierror:
            logger.error("Host unreachable")
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
