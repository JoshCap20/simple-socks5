import socket
import struct
import unittest
from unittest.mock import MagicMock, patch

from src.constants import AddressTypeCodes
from src.models import DetailedAddress
from src.relays.udp_relay import UDPRelay


def build_udp_datagram(dst_addr: str, dst_port: int, data: bytes, frag: int = 0, atyp: int = 1) -> bytes:
    """Build a SOCKS5 UDP datagram per RFC 1928 section 7."""
    rsv = 0
    header = struct.pack("!HBB", rsv, frag, atyp)
    if atyp == 1:  # IPv4
        addr_bytes = socket.inet_aton(dst_addr)
    elif atyp == 4:  # IPv6
        addr_bytes = socket.inet_pton(socket.AF_INET6, dst_addr)
    else:
        addr_bytes = bytes([len(dst_addr)]) + dst_addr.encode()
    port_bytes = struct.pack("!H", dst_port)
    return header + addr_bytes + port_bytes + data


class TestUDPRelay(unittest.TestCase):
    @patch("src.relays.udp_relay.generate_udp_socket")
    def test_init_creates_and_binds_socket(self, mock_gen_socket):
        mock_sock = MagicMock()
        mock_sock.getsockname.return_value = ("0.0.0.0", 5000)
        mock_gen_socket.return_value = mock_sock

        client_conn = MagicMock()
        client_conn.getpeername.return_value = ("127.0.0.1", 1234)
        dst = DetailedAddress(
            name="test", ip="1.2.3.4", port=80,
            address_type=AddressTypeCodes.IPv4,
        )

        relay = UDPRelay(client_conn, dst)
        mock_sock.bind.assert_called_once_with(("", 0))
        self.assertEqual(relay.get_proxy_address().ip, "0.0.0.0")
        self.assertEqual(relay.get_proxy_address().port, 5000)

    @patch("src.relays.udp_relay.generate_udp_socket")
    def test_listen_and_relay_forwards_packet(self, mock_gen_socket):
        mock_proxy_sock = MagicMock()
        mock_proxy_sock.getsockname.return_value = ("0.0.0.0", 5000)
        mock_gen_socket.return_value = mock_proxy_sock

        client_conn = MagicMock()
        client_conn.getpeername.return_value = ("127.0.0.1", 1234)
        dst = DetailedAddress(
            name="test", ip="1.2.3.4", port=80,
            address_type=AddressTypeCodes.IPv4,
        )
        relay = UDPRelay(client_conn, dst)

        # Build a valid UDP datagram
        datagram = build_udp_datagram("10.0.0.1", 53, b"hello")
        client_addr = ("127.0.0.1", 1234)

        # First recvfrom returns the datagram, second raises timeout to exit loop
        mock_proxy_sock.recvfrom.side_effect = [
            (datagram, client_addr),
            socket.timeout("done"),
        ]

        # Mock the forward socket created inside listen_and_relay
        mock_fwd_sock = MagicMock()
        mock_fwd_sock.recvfrom.return_value = (b"response", ("10.0.0.1", 53))
        mock_fwd_sock.__enter__ = MagicMock(return_value=mock_fwd_sock)
        mock_fwd_sock.__exit__ = MagicMock(return_value=False)

        with patch("src.relays.udp_relay.socket.socket", return_value=mock_fwd_sock):
            relay.listen_and_relay()

        # Verify data was sent to correct destination
        mock_fwd_sock.sendto.assert_called_once_with(b"hello", ("10.0.0.1", 53))
        # Verify response was sent back to client
        mock_proxy_sock.sendto.assert_called_once()

    @patch("src.relays.udp_relay.generate_udp_socket")
    def test_listen_and_relay_drops_fragmented_datagrams(self, mock_gen_socket):
        mock_proxy_sock = MagicMock()
        mock_proxy_sock.getsockname.return_value = ("0.0.0.0", 5000)
        mock_gen_socket.return_value = mock_proxy_sock

        client_conn = MagicMock()
        client_conn.getpeername.return_value = ("127.0.0.1", 1234)
        dst = DetailedAddress(
            name="test", ip="1.2.3.4", port=80,
            address_type=AddressTypeCodes.IPv4,
        )
        relay = UDPRelay(client_conn, dst)

        # Build a fragmented datagram (frag != 0)
        frag_datagram = build_udp_datagram("10.0.0.1", 53, b"data", frag=1)
        client_addr = ("127.0.0.1", 1234)

        mock_proxy_sock.recvfrom.side_effect = [
            (frag_datagram, client_addr),
            socket.timeout("done"),
        ]

        with patch("src.relays.udp_relay.socket.socket") as mock_socket_cls:
            relay.listen_and_relay()
            # Should NOT have created any forward socket for fragmented datagram
            mock_socket_cls.assert_not_called()

    @patch("src.relays.udp_relay.generate_udp_socket")
    def test_listen_and_relay_handles_socket_error(self, mock_gen_socket):
        mock_proxy_sock = MagicMock()
        mock_proxy_sock.getsockname.return_value = ("0.0.0.0", 5000)
        mock_gen_socket.return_value = mock_proxy_sock

        client_conn = MagicMock()
        client_conn.getpeername.return_value = ("127.0.0.1", 1234)
        dst = DetailedAddress(
            name="test", ip="1.2.3.4", port=80,
            address_type=AddressTypeCodes.IPv4,
        )
        relay = UDPRelay(client_conn, dst)

        # recvfrom raises a socket error
        mock_proxy_sock.recvfrom.side_effect = OSError("network down")

        # Should not raise — error should be handled gracefully
        relay.listen_and_relay()


if __name__ == "__main__":
    unittest.main()
