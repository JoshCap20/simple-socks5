import os
import argparse


def parse_arguments():
    parser = argparse.ArgumentParser(description="SOCKS5 Proxy Server")
    parser.add_argument(
        "-H",
        "--host",
        type=str,
        default="localhost",
        help="Host address for the SOCKS server. Default: localhost.",
    )
    parser.add_argument(
        "-P",
        "--port",
        type=int,
        default=1080,
        help="Port number for the SOCKS server. Default: 1080.",
    )
    parser.add_argument(
        "-L",
        "--logging-level",
        type=int,
        choices=range(0, 6),
        default=1,
        help=(
            "Set the logging level. 0 = disabled, "
            "1 = debug, 2 = info, 3 = warning, 4 = error, 5 = critical. "
            "Default: 1 (debug)."
        ),
    )
    args = parser.parse_args()

    if args.logging_level is not None:
        os.environ["LOGGING_LEVEL"] = str(args.logging_level)
    else:
        os.environ["DISABLE_LOGGING"] = "1"

    return args
