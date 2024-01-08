import argparse

__version__ = "0.2.1"


def parse_arguments() -> argparse.Namespace:
    """
    Parses command line arguments for the SOCKS5 Proxy Server.

    This parser configures the server's host, port, logging level, and the option to use Tor.
    """
    parser = argparse.ArgumentParser(
        description="SOCKS5 Proxy Server. A flexible and configurable proxy server.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Server Configuration
    server_group = parser.add_argument_group("Server Configuration")
    server_group.add_argument(
        "-H",
        "--host",
        type=str,
        default="localhost",
        help="Host address for the SOCKS server.",
    )
    server_group.add_argument(
        "-P", "--port", type=int, default=1080, help="Port number for the SOCKS server."
    )

    # Logging Configuration
    logging_group = parser.add_argument_group("Logging Configuration")
    logging_group.add_argument(
        "-L",
        "--logging-level",
        type=str,
        choices=["disabled", "debug", "info", "warning", "error", "critical"],
        default="debug",
        help="Set the logging level.",
    )

    # # Tor Configuration
    # tor_group = parser.add_argument_group("Tor Configuration")
    # tor_group.add_argument(
    #     "-UT",
    #     "--use-tor",
    #     action="store_true",
    #     help="Use Tor to make requests to the destination server.",
    # )

    # Version Information
    parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {__version__}"
    )

    args = parser.parse_args()
    return args
