import struct
import socket
from socketserver import ThreadingMixIn, TCPServer, StreamRequestHandler

from constants import SOCKS_VERSION, AddressTypeCodes, CommandCodes
from request_handler import RequestHandler
from data_relay import DataRelay
from utils import (
    generate_general_socks_server_failure_reply,
    generate_command_not_supported_reply,
    generate_connection_refused_reply,
    generate_host_unreachable_reply,
    generate_succeeded_reply,
    generate_socket,
    map_address_type_to_enum
)
from logger import logger


class ThreadingTCPServer(ThreadingMixIn, TCPServer):
    """A threading version of TCP server."""

    pass


class SocksProxy(StreamRequestHandler):
    connection: socket.socket

    def handle(self):
        request_handler = RequestHandler(self.connection)
        
        if not request_handler.handle_handshake():
            logger.error("Handshake failed")
            return
        
        if not request_handler.client_authenticated:
            logger.error("Client not authenticated")
            return

        version, cmd, address_type = request_handler.parse_request()
        if version != SOCKS_VERSION:
            return

        address, port = request_handler.parse_address_and_port(
            address_type
        )

        reply: bytes | None = None
        
        logger.info(f"Connection Established: {address}:{port}")
        
        try:
            match cmd:
                case CommandCodes.CONNECT.value:
                    # CONNECT
                    logger.info(f"CONNECT {address}:{port}")
                    reply = self.handle_connect(address, port, map_address_type_to_enum(address_type))
                    
                case CommandCodes.BIND.value:
                    # TODO: BIND
                    reply = self.handle_bind(address, port)
                    
                case CommandCodes.UDP_ASSOCIATE.value:
                    # TODO: UDP ASSOCIATE
                    reply = self.handle_udp_associate(address, port)
                    
                case _:
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

    def handle_connect(self, address: str, port: int, address_type: AddressTypeCodes) -> None:
        logger.info(f"CONNECT HANDLING: {address}:{port}")
        remote: socket.socket = generate_socket(address_type)
        remote.connect((address, port))
        bind_address: socket._RetAddress = remote.getsockname()
        logger.info(f"Connected to remote: {bind_address}")

        success_reply = generate_succeeded_reply(
            address_type, bind_address[0], bind_address[1]
        )
        self.connection.sendall(success_reply)
        logger.info(f"Sent success reply: {success_reply}")
        DataRelay.relay_data(self.connection, remote)
        
    def handle_bind(self, address: str, port: int) -> bytes:
        logger.error("BIND command not supported")
        return generate_command_not_supported_reply()
    
    def handle_udp_associate(self, address: str, port: int) -> bytes:
        logger.error("UDP ASSOCIATE command not supported")
        return generate_command_not_supported_reply()