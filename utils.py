import struct

from constants import SOCKS_VERSION, ReplyCode, AddressTypeCode


def generate_general_socks_server_failure_reply():
    return generate_failed_reply(
        AddressTypeCode.IPv4, ReplyCode.GENERAL_SOCKS_SERVER_FAILURE
    )


def generate_connection_refused_reply():
    return generate_failed_reply(AddressTypeCode.IPv4, ReplyCode.CONNECTION_REFUSED)


def generate_network_unreachable_reply():
    return generate_failed_reply(AddressTypeCode.IPv4, ReplyCode.NETWORK_UNREACHABLE)


def generate_host_unreachable_reply():
    return generate_failed_reply(AddressTypeCode.IPv4, ReplyCode.HOST_UNREACHABLE)


def generate_address_type_not_supported_reply():
    return generate_failed_reply(
        AddressTypeCode.IPv4, ReplyCode.ADDRESS_TYPE_NOT_SUPPORTED
    )


def generate_failed_reply(address_type: AddressTypeCode, error_number: ReplyCode):
    return struct.pack(
        "!BBBBIH", SOCKS_VERSION, error_number.value, 0, address_type.value, 0, 0
    )
