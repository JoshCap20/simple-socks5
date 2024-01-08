import socket

from .addresses import (
    map_address_enum_to_socket_family,
    map_address_family_to_enum,
    resolve_address_info,
)
from ..constants import AddressTypeCodes
from ..models import DetailedAddress


def generate_tcp_socket(address_type: AddressTypeCodes) -> socket.socket:
    return socket.socket(
        map_address_enum_to_socket_family(address_type), socket.SOCK_STREAM
    )


def generate_udp_socket(address_type: AddressTypeCodes) -> socket.socket:
    return socket.socket(
        map_address_enum_to_socket_family(address_type), socket.SOCK_DGRAM
    )


def generate_address_from_socket(socket: socket.socket) -> DetailedAddress:
    address = socket.getsockname()
    return DetailedAddress(
        **resolve_address_info(address[0], address[1]),
        address_type=map_address_family_to_enum(socket.family),
    )
