import unittest
from unittest.mock import MagicMock, patch
import struct
import socket
from src.request_handlers.tcp import TCPRequestHandler
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
        self.handler = TCPRequestHandler(self.connection)

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
            b"\x08",
            b"myusername",
            b"\x08",
            b"eh",
        ]
        result = self.handler._handle_username_password_auth()
        mock_sendall.assert_called_with(RESP_LOGIN_FAILURE)
        self.assertFalse(result)

    def test_parse_request(self):
        # TODO: Implement test case for _parse_request method
        pass

    def test_parse_address_ipv4(self):
        # TODO: Implement test case for _parse_address method with IPv4 address type
        pass

    def test_parse_address_domain_name(self):
        # TODO: Implement test case for _parse_address method with domain name address type
        pass

    def test_parse_address_ipv6(self):
        # TODO: Implement test case for _parse_address method with IPv6 address type
        pass

    def test_parse_address_invalid(self):
        # TODO: Implement test case for _parse_address method with invalid address type
        pass

    def test_gethostbyaddr(self):
        # TODO: Implement test case for _gethostbyaddr method
        pass


if __name__ == "__main__":
    unittest.main()
