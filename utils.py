import struct

from constants import SOCKS_VERSION, ReplyCodes, AddressTypeCodes


def generate_general_socks_server_failure_reply():
    return generate_failed_reply(
        AddressTypeCodes.IPv4, ReplyCodes.GENERAL_SOCKS_SERVER_FAILURE
    )


def generate_connection_refused_reply():
    return generate_failed_reply(AddressTypeCodes.IPv4, ReplyCodes.CONNECTION_REFUSED)


def generate_network_unreachable_reply():
    return generate_failed_reply(AddressTypeCodes.IPv4, ReplyCodes.NETWORK_UNREACHABLE)


def generate_host_unreachable_reply():
    return generate_failed_reply(AddressTypeCodes.IPv4, ReplyCodes.HOST_UNREACHABLE)


def generate_address_type_not_supported_reply():
    return generate_failed_reply(
        AddressTypeCodes.IPv4, ReplyCodes.ADDRESS_TYPE_NOT_SUPPORTED
    )


def generate_failed_reply(address_type: AddressTypeCodes, error_number: ReplyCodes):
    return struct.pack(
        "!BBBBIH", SOCKS_VERSION, error_number.value, 0, address_type.value, 0, 0
    )
