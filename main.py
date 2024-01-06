from argument_parser import parse_arguments

def main():
    args = parse_arguments()
    
    from server import ThreadingTCPServer, SocksProxy
    from logger import get_logger
    logger = get_logger(__name__)

    with ThreadingTCPServer((args.host, args.port), SocksProxy) as server:
        logger.info(f"Server started on {args.host}:{args.port}")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            logger.info("Server shutting down...")
            server.server_close()
            server.shutdown()
        finally:
            logger.info("Server terminated.")

if __name__ == "__main__":
    main()