## Simple Socks Proxy Server
### Introduction
This is a simple SOCKS Protocol Version 5 server written in Python. It is based on the SOCKS V5 protocol described in [RFC1928](https://www.ietf.org/rfc/rfc1928.txt) and [RFC1929](https://www.ietf.org/rfc/rfc1929.txt).

### Requirements
- Python 3.10 or above

### Usage
```bash
python3 main.py [--host HOST] [--port PORT] 
```

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