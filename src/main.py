from .argument_parser import parse_arguments


def main():
    """
    Entry point of the program.
    Parses command line arguments, starts the server, and handles server shutdown.
    """
    args = parse_arguments()

    from .server import ThreadingTCPServer, SocksProxy
    from .logger import get_logger

    logger = get_logger(__name__)

    with ThreadingTCPServer((args.host, args.port), SocksProxy) as server:
        logger.info(f"Server started on {args.host}:{args.port}")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            logger.info("Server shutting down...")
        finally:
            server.server_close()
            server.shutdown()
            logger.info("Server terminated.")


if __name__ == "__main__":
    main()
