import socket
import unittest
from unittest.mock import MagicMock, patch

from src.exceptions import InvalidVersionError, InvalidRequestError
from src.server import TCPProxyServer


class TestHandleParseRequestErrors(unittest.TestCase):
    """Verify parse_request() exceptions produce SOCKS5 error replies."""

    def _make_handler(self):
        """Create a TCPProxyServer without actually binding a socket."""
        handler = object.__new__(TCPProxyServer)
        handler.connection = MagicMock(spec=socket.socket)
        handler.connection.getpeername.return_value = ("127.0.0.1", 9999)
        handler.request = handler.connection
        handler.server = MagicMock()
        return handler

    @patch("src.server.TCPHandler")
    def test_invalid_version_sends_general_failure(self, mock_tcp_handler_cls):
        handler = self._make_handler()
        mock_instance = mock_tcp_handler_cls.return_value
        mock_instance.handle_request.return_value = True
        mock_instance.parse_request.side_effect = InvalidVersionError(4)

        handler.handle()

        handler.connection.sendall.assert_called_once()
        reply = handler.connection.sendall.call_args[0][0]
        # VER=05, REP=01 (general failure), RSV=00, ATYP=01 (IPv4), zeroed addr+port
        self.assertEqual(reply, b"\x05\x01\x00\x01\x00\x00\x00\x00\x00\x00")

    @patch("src.server.TCPHandler")
    def test_invalid_request_sends_general_failure(self, mock_tcp_handler_cls):
        handler = self._make_handler()
        mock_instance = mock_tcp_handler_cls.return_value
        mock_instance.handle_request.return_value = True
        mock_instance.parse_request.side_effect = InvalidRequestError(0xFF)

        handler.handle()

        handler.connection.sendall.assert_called_once()
        reply = handler.connection.sendall.call_args[0][0]
        self.assertEqual(reply, b"\x05\x01\x00\x01\x00\x00\x00\x00\x00\x00")

    @patch("src.server.TCPHandler")
    def test_connection_error_sends_general_failure(self, mock_tcp_handler_cls):
        handler = self._make_handler()
        mock_instance = mock_tcp_handler_cls.return_value
        mock_instance.handle_request.return_value = True
        mock_instance.parse_request.side_effect = ConnectionError("closed")

        handler.handle()

        handler.connection.sendall.assert_called_once()
        reply = handler.connection.sendall.call_args[0][0]
        self.assertEqual(reply, b"\x05\x01\x00\x01\x00\x00\x00\x00\x00\x00")

    @patch("src.server.TCPHandler")
    def test_socket_error_sends_general_failure(self, mock_tcp_handler_cls):
        handler = self._make_handler()
        mock_instance = mock_tcp_handler_cls.return_value
        mock_instance.handle_request.return_value = True
        mock_instance.parse_request.side_effect = socket.error("reset")

        handler.handle()

        handler.connection.sendall.assert_called_once()
        reply = handler.connection.sendall.call_args[0][0]
        self.assertEqual(reply, b"\x05\x01\x00\x01\x00\x00\x00\x00\x00\x00")


class TestSendErrorReply(unittest.TestCase):
    """Verify _send_error_reply swallows all OSError subclasses."""

    def _make_handler(self):
        handler = object.__new__(TCPProxyServer)
        handler.connection = MagicMock(spec=socket.socket)
        return handler

    def test_swallows_broken_pipe(self):
        handler = self._make_handler()
        handler.connection.sendall.side_effect = BrokenPipeError
        handler._send_error_reply(b"\x05\x01\x00\x01\x00\x00\x00\x00\x00\x00")

    def test_swallows_connection_reset(self):
        handler = self._make_handler()
        handler.connection.sendall.side_effect = ConnectionResetError
        handler._send_error_reply(b"\x05\x01\x00\x01\x00\x00\x00\x00\x00\x00")

    def test_swallows_generic_oserror(self):
        handler = self._make_handler()
        handler.connection.sendall.side_effect = OSError("transport endpoint closed")
        handler._send_error_reply(b"\x05\x01\x00\x01\x00\x00\x00\x00\x00\x00")


if __name__ == "__main__":
    unittest.main()
