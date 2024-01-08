import struct

from .addresses import map_address_to_bytes
from ..constants import SOCKS_VERSION, ReplyCodes, AddressTypeCodes, MethodCodes


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
    if address_type == AddressTypeCodes.DOMAIN_NAME:
        raise ValueError("Address type not suitable for failed reply")
    return struct.pack(
        "!BBBBIH", SOCKS_VERSION, error_number.value, 0, address_type.value, 0, 0
    )


def generate_succeeded_reply(
    address_type: AddressTypeCodes, ip: str, port: int
) -> bytes:
    addr_bytes: bytes = map_address_to_bytes(address_type, ip)
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


def generate_connection_method_response(method: MethodCodes) -> bytes:
    return struct.pack("!BB", SOCKS_VERSION, method.value)
