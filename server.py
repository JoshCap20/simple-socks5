from socketserver import ThreadingMixIn, TCPServer


class ThreadingTCPServer(ThreadingMixIn, TCPServer):
    """A threading version of TCP server."""

    pass
