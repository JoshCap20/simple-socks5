## Simple Socks Proxy Server
### Introduction
This is a simple SOCKS Protocol Version 5 server written in Python. It is based on the SOCKS V5 protocol described in [RFC1928](https://www.ietf.org/rfc/rfc1928.txt) and [RFC1929](https://www.ietf.org/rfc/rfc1929.txt).

### Features
- **Concurrent Connections**: Supports multiple simultaneous client connections.
- **Performance Optimized**: Efficient handling of large data transfers.
- **Protocol Compliance**: Fully compliant with RFC1928 and RFC1929 for basic functionalities.

### Requirements
- Python 3.10 or above
- Only standard Python libraries are used. No additional dependencies are required.

### Usage
```bash
python3 app.py [--host HOST | -H HOST] [--port PORT | -P PORT] [--logging-level INT(0,6) | -L INT(0, 6)]
```
- `--host HOST` or `-H HOST`: The host address to bind to. Default is `localhost`. Use `0.0.0.0` to bind to all available interfaces.
- `--port PORT` or `-P PORT`: The port number to bind to. Default is `9999`.
- `--logging-level INT(0, 6)` or `-L INT(0, 6)`: Set logging level where 1 is debug, 5 is critical, and 0 is disabled.

### RFC 1928 & RFC 1929 Compliance
#### Covered Aspects
- TCP Connections: Implements SOCKS5 for TCP-based client-server applications.
- Authentication: Supports username/password authentication method (RFC 1929), including failure handling.
- Connection Requests: Handles SOCKS5 connection requests including parsing and responding to the VER, CMD, RSV, ATYP, DST.ADDR, and DST.PORT fields.
- Address Types: Supports IPv4, IPv6 and domain name address types.
- Reply Handling: Generates replies to the SOCKS5 requests based on different scenarios (success, general SOCKS server failure, connection refused, etc.).
#### Not Covered Aspects
- UDP Support: The current implementation does not support UDP-based client applications as described in Section 7 of RFC 1928. The UDP ASSOCIATE command is not implemented.
- BIND Command: Although the BIND command is recognized, it's not supported in the current implementation.
- Fragmentation in UDP: As the UDP support is not implemented, the handling of fragmentation in UDP datagrams is also not covered.
- GSSAPI Authentication: The GSSAPI authentication method (RFC 1961) is not implemented.
#### Security Considerations
- Data Encryption: The current implementation does not include data encryption for the transmission of data through the proxy. Data, including username and password for authentication, is transmitted in cleartext.
- Recommendation for Secure Environments: Additional security measures are recommended for use in environments where data interception is a risk.