import sys
import struct
import socket
from socketserver import ThreadingMixIn, TCPServer, StreamRequestHandler

from constants import SOCKS_VERSION
from request_handler import RequestHandler
from data_relay import DataRelay
from utils import generate_general_socks_server_failure_reply


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

        try:
            if cmd == 1:
                remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                remote.connect((address, port))
                bind_address = remote.getsockname()
            elif cmd == 2:
                # TODO: Implement BIND
                self.server.close_request(self.request)
            elif cmd == 3:
                # TODO: Implement UDP ASSOCIATE
                self.server.close_request(self.request)
            else:
                self.server.close_request(self.request)

            addr = struct.unpack("!I", socket.inet_aton(bind_address[0]))[0]
            port = bind_address[1]
            reply = struct.pack("!BBBBIH", SOCKS_VERSION, 0, 0, 1, addr, port)

        except Exception as e:
            print(e, file=sys.stderr)
            reply = generate_general_socks_server_failure_reply()

        self.connection.sendall(reply)

        if reply[1] == 0 and cmd == 1:
            DataRelay.relay_data(self.connection, remote)

        self.server.close_request(self.request)
