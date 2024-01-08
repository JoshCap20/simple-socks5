from .argument_parser import parse_arguments


def main():
    """
    Entry point of the program.
    Parses command line arguments, starts the server, and handles server shutdown.
    """
    args = parse_arguments()

    # Import here to allow setting the logging level before logger is imported
    from .server import (
        ThreadingTCPServer,
        TCPProxyServer,
    )
    from .logger import get_logger

    logger = get_logger(__name__)

    with ThreadingTCPServer((args.host, args.port), TCPProxyServer) as tcp_server:
        logger.info(f"Proxy server started on {args.host}:{args.port}")

        try:
            tcp_server.serve_forever()
        except KeyboardInterrupt:
            logger.info("Server shutting down...")
        finally:
            tcp_server.server_close()
            tcp_server.shutdown()
            logger.info("Server terminated.")


if __name__ == "__main__":
    main()
