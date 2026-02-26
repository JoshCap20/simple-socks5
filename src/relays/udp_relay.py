import socket

from .base import BaseRelay
from ..constants import RELAY_BUFFER_SIZE, UDP_RECV_TIMEOUT, UDP_FORWARD_TIMEOUT
from ..models import DetailedAddress, BaseAddress
from ..logger import get_logger
from ..handlers import UDPHandler
from ..utils import (
    generate_udp_socket,
    map_address_enum_to_socket_family,
    base_relay_template,
)

logger = get_logger(__name__)


class UDPRelay(BaseRelay):
    """
    Class responsible for relaying data between a client socket and a remote socket via UDP.
    """

    def __init__(self, client_connection: socket.socket, dst_address: DetailedAddress):
        super().__init__(client_connection, dst_address)
        self.generate_proxy_connection()

    def generate_proxy_connection(self) -> None:
        sock = generate_udp_socket(self.dst_address.address_type)
        try:
            sock.bind(("", 0))  # Bind to any available port
            sock.settimeout(UDP_RECV_TIMEOUT)
        except Exception:
            sock.close()
            raise
        self.proxy_connection = sock
        self.set_proxy_address()

    def listen_and_relay(self):
        try:
            while True:
                data, addr = self.proxy_connection.recvfrom(RELAY_BUFFER_SIZE)

                datagram = UDPHandler.parse_udp_datagram(data)

                if datagram.frag != 0:
                    logger.debug(
                        f"(UDP) Dropped fragmented datagram: {addr} -> "
                        f"{datagram.dst_addr}:{datagram.dst_port}, "
                        f"Size: {len(datagram.data)} bytes"
                    )
                    continue

                try:
                    self._forward_packet(datagram, addr)
                except (ValueError, KeyError) as e:
                    logger.debug(f"(UDP) Dropped unsupported datagram from {addr}: {e}")
                    continue

        except socket.timeout:
            logger.debug("UDP relay timed out waiting for data")
        except OSError as e:
            logger.error(f"UDP relay socket error: {e}")
        finally:
            try:
                self.proxy_connection.close()
            except OSError:
                pass

    def _forward_packet(self, datagram, client_addr: tuple) -> None:
        with socket.socket(
            map_address_enum_to_socket_family(datagram.address_type),
            socket.SOCK_DGRAM,
        ) as forward_socket:
            forward_socket.settimeout(UDP_FORWARD_TIMEOUT)
            forward_socket.sendto(
                datagram.data, (datagram.dst_addr, datagram.dst_port)
            )
            self._log_relay(
                BaseAddress(client_addr[0], client_addr[1]),
                BaseAddress(datagram.dst_addr, datagram.dst_port),
                len(datagram.data),
            )

            try:
                response, remote_addr = forward_socket.recvfrom(RELAY_BUFFER_SIZE)
                header = UDPHandler.build_udp_response_header(
                    remote_addr[0], remote_addr[1]
                )
                self.proxy_connection.sendto(header + response, client_addr)
                self._log_relay(
                    BaseAddress(datagram.dst_addr, datagram.dst_port),
                    BaseAddress(client_addr[0], client_addr[1]),
                    len(response),
                )
            except socket.timeout:
                logger.debug(
                    f"UDP forward timeout waiting for response from "
                    f"{datagram.dst_addr}:{datagram.dst_port}"
                )

    def _log_relay(self, src_addr: BaseAddress, dst_addr: BaseAddress, data_len: int):
        logger.debug(
            base_relay_template.substitute(
                protocol="UDP",
                src_ip=src_addr.ip,
                src_port=src_addr.port,
                dst_ip=dst_addr.ip,
                dst_port=dst_addr.port,
                data_size=data_len,
            )
        )
