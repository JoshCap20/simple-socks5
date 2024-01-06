import argparse

from logger import get_logger
from server import ThreadingTCPServer, SocksProxy

logger = get_logger(__name__)

def main(host: str, port: int):

    with ThreadingTCPServer((host, port), SocksProxy) as server:
        logger.info(f"Server started on {host}:{port}")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            logger.info("Server shutting down...")
            server.server_close()
            server.shutdown()
        finally:
            logger.info("Server terminated.")
            


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SOCKS5 Proxy Server")
    parser.add_argument(
        "-H",
        "--host",
        type=str,
        default="localhost",
        help="Host address for the SOCKS server",
    )
    parser.add_argument(
        "-P", "--port", type=int, default=9999, help="Port number for the SOCKS server"
    )
    
    args = parser.parse_args()

    main(args.host, args.port)
