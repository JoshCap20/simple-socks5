import os
import argparse


def parse_arguments():
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
    parser.add_argument(
        "-Q",
        "--quiet",
        action="store_false",
        dest="verbose",
        help="Disable verbose logging (verbose is enabled by default)",
    )
    args = parser.parse_args()

    os.environ["VERBOSE"] = "1" if args.verbose else "0"

    return args
