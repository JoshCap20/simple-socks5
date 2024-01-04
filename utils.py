import socket
import struct

from constants import SOCKS_VERSION, ReplyCode, AddressTypeCode


def parse_socks_request(connection: socket.socket) -> tuple:
    # Unpack the version, command, and address type
    version, cmd, _, address_type = struct.unpack("!BBBB", connection.recv(4))

    # Resolve the address based on the address type
    if address_type == AddressTypeCode.IPv4.value:
        address = socket.inet_ntoa(connection.recv(4))
    elif address_type == AddressTypeCode.DOMAIN_NAME.value:
        domain_length = connection.recv(1)[0]
        address = connection.recv(domain_length)
    elif address_type == AddressTypeCode.IPv6.value:
        address = socket.inet_ntop(socket.AF_INET6, connection.recv(16))
    else:
        raise Exception("Address type not supported")

    # Unpack the port number
    port = struct.unpack("!H", connection.recv(2))[0]

    return version, cmd, address_type, address, port


def send_socks_response(
    connection: socket.socket,
    reply_code: ReplyCode,
    address: str = "0.0.0.0",
    port: int = 0,
) -> None:
    if isinstance(address, str):
        # Convert string IP to bytes
        address = socket.inet_aton(address)
    port = port.to_bytes(2, "big")  # Convert port to 2 bytes

    response = (
        struct.pack("!BBB", SOCKS_VERSION, reply_code.value, 0x00) + address + port
    )
    connection.sendall(response)


def resolve_address(connection: socket.socket, address_type: int) -> tuple:
    if address_type == AddressTypeCode.IPv4.value:
        address = socket.inet_ntoa(connection.recv(4))
    elif address_type == AddressTypeCode.DOMAIN_NAME.value:
        domain_length = connection.recv(1)[0]
        address = connection.recv(domain_length)
    elif address_type == AddressTypeCode.IPv6.value:
        address = socket.inet_ntop(socket.AF_INET6, connection.recv(16))
    else:
        raise Exception("Address type not supported")

    port = struct.unpack("!H", connection.recv(2))[0]
    return address, port
