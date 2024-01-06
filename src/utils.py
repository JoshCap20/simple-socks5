import struct
import socket

from .constants import SOCKS_VERSION, ReplyCodes, AddressTypeCodes
from .models import Address

def generate_general_socks_server_failure_reply(
    address_type: AddressTypeCodes = AddressTypeCodes.IPv4,
) -> bytes:
    return generate_failed_reply(address_type, ReplyCodes.GENERAL_SOCKS_SERVER_FAILURE)


def generate_connection_refused_reply(
    address_type: AddressTypeCodes = AddressTypeCodes.IPv4,
) -> bytes:
    return generate_failed_reply(address_type, ReplyCodes.CONNECTION_REFUSED)


def generate_network_unreachable_reply(
    address_type: AddressTypeCodes = AddressTypeCodes.IPv4,
) -> bytes:
    return generate_failed_reply(address_type, ReplyCodes.NETWORK_UNREACHABLE)


def generate_host_unreachable_reply(
    address_type: AddressTypeCodes = AddressTypeCodes.IPv4,
) -> bytes:
    return generate_failed_reply(address_type, ReplyCodes.HOST_UNREACHABLE)


def generate_address_type_not_supported_reply(
    address_type: AddressTypeCodes = AddressTypeCodes.IPv4,
) -> bytes:
    return generate_failed_reply(address_type, ReplyCodes.ADDRESS_TYPE_NOT_SUPPORTED)


def generate_connection_not_allowed_by_ruleset_reply(
    address_type: AddressTypeCodes = AddressTypeCodes.IPv4,
) -> bytes:
    return generate_failed_reply(
        address_type, ReplyCodes.CONNECTION_NOT_ALLOWED_BY_RULESET
    )


def generate_ttl_expired_reply(
    address_type: AddressTypeCodes = AddressTypeCodes.IPv4,
) -> bytes:
    return generate_failed_reply(address_type, ReplyCodes.TTL_EXPIRED)


def generate_command_not_supported_reply(
    address_type: AddressTypeCodes = AddressTypeCodes.IPv4,
) -> bytes:
    return generate_failed_reply(address_type, ReplyCodes.COMMAND_NOT_SUPPORTED)


def generate_unassigned_reply() -> bytes:
    return generate_failed_reply(AddressTypeCodes.IPv4, ReplyCodes.UNASSIGNED)


def generate_failed_reply(
    address_type: AddressTypeCodes, error_number: ReplyCodes
) -> bytes:
    return struct.pack(
        "!BBBBIH", SOCKS_VERSION, error_number.value, 0, address_type.value, 0, 0
    )


def generate_succeeded_reply(
    address_type: AddressTypeCodes, ip: str, port: int
) -> bytes:
    addr_bytes: bytes = translate_address_to_bytes(address_type, ip)
    address_field: int = int.from_bytes(addr_bytes, byteorder="big")

    return struct.pack(
        "!BBBBIH",
        SOCKS_VERSION,
        ReplyCodes.SUCCEEDED.value,
        0,
        address_type.value,
        address_field,
        port,
    )

def translate_address_to_bytes(address_type: AddressTypeCodes, ip: str) -> bytes:
    if address_type == AddressTypeCodes.IPv4:
        return socket.inet_aton(ip)
    elif address_type == AddressTypeCodes.IPv6:
        return socket.inet_pton(socket.AF_INET6, ip)
    else:
        raise ValueError("Address type not suitable for byte translation")
    
def map_address_type_to_enum(address_type: int) -> AddressTypeCodes:
    if address_type == AddressTypeCodes.IPv4.value:
        return AddressTypeCodes.IPv4
    elif address_type == AddressTypeCodes.DOMAIN_NAME.value:
        return AddressTypeCodes.DOMAIN_NAME
    elif address_type == AddressTypeCodes.IPv6.value:
        return AddressTypeCodes.IPv6
    else:
        raise ValueError("Unknown address type")
    
def map_address_type_to_socket_family(address_type: AddressTypeCodes) -> int:
    if address_type == AddressTypeCodes.IPv4:
        return socket.AF_INET
    elif address_type == AddressTypeCodes.IPv6:
        return socket.AF_INET6
    else:
        raise ValueError("Unknown address type")
    
def generate_socket(address: Address) -> socket.socket:
    return socket.socket(map_address_type_to_socket_family(address.address_type), socket.SOCK_STREAM)