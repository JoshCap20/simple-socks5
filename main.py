from server import SocksProxy
from constants import HOST_NAME, PORT_NUMBER
from server import ThreadingTCPServer


def main():
    with ThreadingTCPServer((HOST_NAME, PORT_NUMBER), SocksProxy) as server:
        print(f"SOCKS server started on {HOST_NAME}:{PORT_NUMBER}")
        server.serve_forever()


if __name__ == "__main__":
    main()
