from collections import namedtuple
from socket import socket

from ..models import Address, BindAddress
from ..utils import generate_address_from_socket, generate_tcp_socket


class BaseRelay:
    client_connection: socket
    proxy_connection: socket

    client_address: Address
    dst_address: Address
    proxy_address: BindAddress

    def __init__(self, connection: socket, dst_address: Address):
        self.client_connection = connection
        self.dst_address = dst_address
        self.set_client_address()

    def listen_and_relay(self):
        raise NotImplementedError

    def set_client_address(self) -> None:
        """
        Sets the client address from client socket.
        """
        self.client_address = generate_address_from_socket(self.client_connection)

    def set_proxy_address(self) -> None:
        """
        Sets the proxy address from proxy socket.
        """
        self.proxy_address = BindAddress(*self.proxy_connection.getsockname())

    def get_proxy_address(self) -> BindAddress:
        """
        Returns the proxy address.
        """
        if self.proxy_address is None:
            raise ValueError("Bind address is None")
        return self.proxy_address

    def get_proxy_ip(self) -> str:
        """
        Returns the proxy IP.
        """
        if self.proxy_address is None:
            raise ValueError("Bind address is None")
        return self.proxy_address.ip

    def get_proxy_port(self) -> int:
        """
        Returns the proxy port.
        """
        if self.proxy_address is None:
            raise ValueError("Bind address is None")
        return self.proxy_address.port

    def get_dst_address(self) -> Address:
        """
        Returns the destination address.
        """
        return self.dst_address

    def get_dst_ip(self) -> str:
        """
        Returns the destination IP.
        """
        return self.dst_address.ip

    def get_dst_port(self) -> int:
        """
        Returns the destination port.
        """
        return self.dst_address.port

    def get_client_address(self) -> Address:
        """
        Returns the client address.
        """
        return self.client_address

    def get_client_ip(self) -> str:
        """
        Returns the client IP.
        """
        return self.client_address.ip

    def get_client_port(self) -> int:
        """
        Returns the client port.
        """
        return self.client_address.port
