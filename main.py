import sys
import signal
import argparse

from logger import logger
from server import ThreadingTCPServer, SocksProxy


def main(host: str, port: int):
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    with ThreadingTCPServer((host, port), SocksProxy) as server:
        logger.info(f"Server started on {host}:{port}")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            logger.info("Server shutting down.")


def signal_handler(signum, frame):
    logger.info(f"Caught signal {signum}")
    sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SOCKS5 Proxy Server")
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Host address for the SOCKS server",
    )
    parser.add_argument(
        "--port", type=int, default=9999, help="Port number for the SOCKS server"
    )
    args = parser.parse_args()

    main(args.host, args.port)
