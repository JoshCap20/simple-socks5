import unittest
from unittest.mock import MagicMock, patch
import struct
import socket
from src.handlers.tcp import TCPHandler
from src.exceptions import InvalidVersionError, InvalidRequestError
from src.constants import SOCKS_VERSION, AddressTypeCodes, MethodCodes
from src.models import DetailedAddress, Request

# Testing Data
## Initial Requests
REQ_INCORRECT_VERSION = b"\x04\x01"
REQ_CORRECT_VERSION_ONE_METHOD = b"\x05\x01"

CORRECT_VERSION_NO_AUTH_REQUIRED = [b"\x05\x01", b"\x00"]
CORRECT_VERSION_AUTH_REQUIRED = [b"\x05\x01", b"\x02"]
CORRECT_VERSION_AUTH_OR_NO_AUTH = [b"\x05\x02", b"\x00\x02"]

## Initial Responses
RESP_CORRECT_VERSION_NO_AUTH_REQUIRED = b"\x05\x00"
RESP_CORRECT_VERSION_AUTH_REQUIRED = b"\x05\x02"
RESP_CORRECT_VERSION_NO_ACCEPTABLE_METHODS = b"\x05\xFF"
RESP_LOGIN_SUCCESS = b"\x01\x00"
RESP_LOGIN_FAILURE = b"\x01\x01"


class TestTCPRequestHandlerIPv4(unittest.TestCase):
    def setUp(self):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.handler = TCPHandler(self.connection)

    def tearDown(self):
        self.connection.close()

    @patch("socket.socket.recv")
    def test_handle_handshake__incorrect_version(self, mock_recv):
        mock_recv.side_effect = [REQ_INCORRECT_VERSION]
        with self.assertRaises(InvalidVersionError):
            self.handler.handle_request()

    @patch("socket.socket.recv")
    @patch("socket.socket.sendall")
    def test_handle_handshake__no_authentication_required(
        self, mock_sendall, mock_recv
    ):
        mock_recv.side_effect = CORRECT_VERSION_NO_AUTH_REQUIRED
        result = self.handler.handle_request()
        mock_sendall.assert_called_with(RESP_CORRECT_VERSION_NO_AUTH_REQUIRED)

    @patch("socket.socket.recv")
    @patch("socket.socket.sendall")
    def test_handle_handshake__correct_version__authentication_required_success(
        self, mock_sendall, mock_recv
    ):
        username = "myusername"
        password = "mypassword"
        mock_recv.side_effect = [
            *CORRECT_VERSION_AUTH_REQUIRED,
            b"\x01",
            chr(len(username)).encode(),
            username.encode(),
            chr(len(password)).encode(),
            password.encode(),
        ]
        result = self.handler.handle_request()
        mock_sendall.assert_called_with(RESP_LOGIN_SUCCESS)

    @patch("socket.socket.recv")
    @patch("socket.socket.sendall")
    def test_handle_handshake__correct_version__authentication_required_subnegotiation_failure(
        self, mock_sendall, mock_recv
    ):
        username = "myusername"
        password = "mypassword"
        mock_recv.side_effect = [
            *CORRECT_VERSION_AUTH_REQUIRED,
            b"\x00",
            chr(len(username)).encode(),
            username.encode(),
            chr(len(password)).encode(),
            password.encode(),
        ]
        result = self.handler.handle_request()
        mock_sendall.assert_called_with(RESP_LOGIN_FAILURE)

    @patch("socket.socket.recv")
    @patch("socket.socket.sendall")
    def test_handle_handshake__correct_version__authentication_required_incorrect_password(
        self, mock_sendall, mock_recv
    ):
        username = "myusername"
        password = "eh"
        mock_recv.side_effect = [
            *CORRECT_VERSION_AUTH_REQUIRED,
            b"\x00",
            chr(len(username)).encode(),
            username.encode(),
            chr(len(password)).encode(),
            password.encode(),
        ]
        result = self.handler.handle_request()
        mock_sendall.assert_called_with(RESP_LOGIN_FAILURE)

    def test_authenticate_with_username_password_method(self):
        methods = b"\x02"
        result = self.handler._negotiate_authentication_method(methods)
        self.assertEqual(result, MethodCodes.USERNAME_PASSWORD)

    def test_authenticate_with_no_authentication_required(self):
        methods = b"\x00"
        result = self.handler._negotiate_authentication_method(methods)
        self.assertEqual(result, MethodCodes.NO_AUTHENTICATION_REQUIRED)

    def test_authenticate_with_invalid_methods(self):
        methods = b"\xFF"
        result = self.handler._negotiate_authentication_method(methods)
        self.assertEqual(result, MethodCodes.NO_ACCEPTABLE_METHODS)

    @patch("socket.socket.recv")
    @patch("socket.socket.sendall")
    def test_handle_username_password_auth__valid(self, mock_sendall, mock_recv):
        methods = b"\x02"
        mock_recv.side_effect = [
            b"\x01",
            b"\x08",
            b"myusername",
            b"\x08",
            b"mypassword",
        ]
        result = self.handler._handle_username_password_auth()
        mock_sendall.assert_called_with(RESP_LOGIN_SUCCESS)
        self.assertTrue(result)

    @patch("socket.socket.recv")
    @patch("socket.socket.sendall")
    def test_handle_username_password_auth__invalid(self, mock_sendall, mock_recv):
        mock_recv.side_effect = [
            b"\x01",
            bytes([len("myusername")]),
            b"myusername",
            bytes([len("eh")]),
            b"eh",
        ]
        result = self.handler._handle_username_password_auth()
        mock_sendall.assert_called_with(RESP_LOGIN_FAILURE)
        self.assertFalse(result)

    @patch("socket.socket.recv")
    @patch("src.handlers.base.socket.gethostbyaddr")
    def test_parse_request(self, mock_gethostbyaddr, mock_recv):
        mock_gethostbyaddr.return_value = ("example.com", [], ["93.184.216.34"])
        # VER=05, CMD=01 (CONNECT), RSV=00, ATYP=01 (IPv4), ADDR, PORT
        mock_recv.side_effect = [
            struct.pack("!BBBB", 0x05, 0x01, 0x00, 0x01),
            socket.inet_aton("93.184.216.34"),
            struct.pack("!H", 80),
        ]
        result = self.handler.parse_request()
        self.assertIsInstance(result, Request)
        self.assertEqual(result.version, 5)
        self.assertEqual(result.command, 1)
        self.assertEqual(result.address.ip, "93.184.216.34")
        self.assertEqual(result.address.port, 80)
        self.assertEqual(result.address.address_type, AddressTypeCodes.IPv4)

    @patch("socket.socket.recv")
    @patch("src.handlers.base.socket.gethostbyaddr")
    def test_parse_address_ipv4(self, mock_gethostbyaddr, mock_recv):
        mock_gethostbyaddr.return_value = ("example.com", [], ["1.2.3.4"])
        mock_recv.side_effect = [
            socket.inet_aton("1.2.3.4"),
            struct.pack("!H", 443),
        ]
        result = self.handler._parse_address(AddressTypeCodes.IPv4.value)
        self.assertEqual(result.ip, "1.2.3.4")
        self.assertEqual(result.port, 443)
        self.assertEqual(result.name, "example.com")
        self.assertEqual(result.address_type, AddressTypeCodes.IPv4)

    @patch("socket.socket.recv")
    @patch("src.handlers.base.socket.gethostbyname")
    def test_parse_address_domain_name(self, mock_gethostbyname, mock_recv):
        mock_gethostbyname.return_value = "93.184.216.34"
        domain = "example.com"
        mock_recv.side_effect = [
            bytes([len(domain)]),
            domain.encode(),
            struct.pack("!H", 80),
        ]
        result = self.handler._parse_address(AddressTypeCodes.DOMAIN_NAME.value)
        self.assertEqual(result.ip, "93.184.216.34")
        self.assertEqual(result.port, 80)
        self.assertEqual(result.name, domain)
        # Domain names get resolved to IPv4
        self.assertEqual(result.address_type, AddressTypeCodes.IPv4)

    @patch("socket.socket.recv")
    @patch("src.handlers.base.socket.gethostbyaddr")
    def test_parse_address_ipv6(self, mock_gethostbyaddr, mock_recv):
        ipv6 = "2001:db8::1"
        mock_gethostbyaddr.return_value = ("ipv6host.example.com", [], [ipv6])
        mock_recv.side_effect = [
            socket.inet_pton(socket.AF_INET6, ipv6),
            struct.pack("!H", 8080),
        ]
        result = self.handler._parse_address(AddressTypeCodes.IPv6.value)
        self.assertEqual(result.ip, ipv6)
        self.assertEqual(result.port, 8080)
        self.assertEqual(result.name, "ipv6host.example.com")
        self.assertEqual(result.address_type, AddressTypeCodes.IPv6)

    def test_parse_address_invalid(self):
        with self.assertRaises(InvalidRequestError):
            self.handler._parse_address(0xFF)

    @patch("src.handlers.base.socket.gethostbyaddr")
    def test_gethostbyaddr_success(self, mock_gethostbyaddr):
        mock_gethostbyaddr.return_value = ("example.com", [], ["1.2.3.4"])
        result = self.handler._gethostbyaddr("1.2.3.4")
        self.assertEqual(result, "example.com")

    @patch("src.handlers.base.socket.gethostbyaddr")
    def test_gethostbyaddr_failure_returns_ip(self, mock_gethostbyaddr):
        mock_gethostbyaddr.side_effect = OSError("no reverse DNS")
        result = self.handler._gethostbyaddr("1.2.3.4")
        self.assertEqual(result, "1.2.3.4")


if __name__ == "__main__":
    unittest.main()
