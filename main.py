import sys
import signal

from server import SocksProxy
from constants import HOST_NAME, PORT_NUMBER
from server import ThreadingTCPServer


def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    with ThreadingTCPServer((HOST_NAME, PORT_NUMBER), SocksProxy) as server:
        print(f"SOCKS server started on {HOST_NAME}:{PORT_NUMBER}")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            print("Server shutting down.")


def signal_handler(signum, frame):
    print("Signal received, shutting down the server.")
    sys.exit(0)


if __name__ == "__main__":
    main()
