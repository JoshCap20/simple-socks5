import socket
from socketserver import ThreadingMixIn, TCPServer, StreamRequestHandler

from constants import CommandCodes
from request_handler import RequestHandler
from data_relay import DataRelay
from utils import (
    generate_general_socks_server_failure_reply,
    generate_command_not_supported_reply,
    generate_connection_refused_reply,
    generate_host_unreachable_reply,
    generate_succeeded_reply,
    generate_socket
)
from logger import logger
from models import Request, Address

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

        request: Request = request_handler.parse_request()
        
        reply: bytes | None = None
        
        logger.info(f"Connection Established with {request.address.name}, {request.address.ip}, {request.address.port}, {request.address.address_type}")
        
        try:
            match request.command:
                case CommandCodes.CONNECT.value:
                    # CONNECT
                    logger.info(f"CONNECT {request.address.name}:{request.address.port}")
                    reply = self.handle_connect(request.address)
                    
                case CommandCodes.BIND.value:
                    # TODO: BIND
                    reply = self.handle_bind(request.address)
                    
                case CommandCodes.UDP_ASSOCIATE.value:
                    # TODO: UDP ASSOCIATE
                    reply = self.handle_udp_associate(request.address)
                    
                case _:
                    # Invalid command
                    reply = generate_command_not_supported_reply()
                    
        except ConnectionRefusedError:
            logger.error(f"Connection refused: {request.address.name}, {request.address.ip}:{request.address.port}")
            reply = generate_connection_refused_reply()
        except socket.gaierror:
            logger.error(f"Host unreachable: {request.address.name}, {request.address.ip}:{request.address.port}")
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
        logger.info(f"CONNECT HANDLING: {address.ip}:{address.port}")
        remote: socket.socket = generate_socket(address)
        remote.connect((address.ip, address.port))
        bind_address: socket._RetAddress = remote.getsockname()
        logger.info(f"Connected to remote: {bind_address}")

        print(f"BIND1: {bind_address[0]}:{bind_address[1]}")
        print(f"ADDRESS1: {address.ip}:{address.port}")
        success_reply = generate_succeeded_reply(
            address.address_type, bind_address[0], bind_address[1]
        )
        self.connection.sendall(success_reply)
        logger.info(f"Sent success reply: {success_reply}")
        DataRelay.relay_data(self.connection, remote)
        
    def handle_bind(self, address: Address) -> bytes:
        logger.error("BIND command not supported")
        return generate_command_not_supported_reply()
    
    def handle_udp_associate(self, address: Address) -> bytes:
        logger.error("UDP ASSOCIATE command not supported")
        return generate_command_not_supported_reply()