from enum import Enum

SOCKS_VERSION: int = 5

# Sample username and password for testing

USERNAME: str = "myusername"
PASSWORD: str = "mypassword"

# See https://www.ietf.org/rfc/rfc1928.txt for more information about the below codes


class MethodCodes(Enum):
    NO_AUTHENTICATION_REQUIRED = 0x00
    GSSAPI = 0x01
    USERNAME_PASSWORD = 0x02
    NO_ACCEPTABLE_METHODS = 0xFF


class ReplyCodes(Enum):
    SUCCEEDED = 0x00
    GENERAL_SOCKS_SERVER_FAILURE = 0x01
    CONNECTION_NOT_ALLOWED_BY_RULESET = 0x02
    NETWORK_UNREACHABLE = 0x03
    HOST_UNREACHABLE = 0x04
    CONNECTION_REFUSED = 0x05
    TTL_EXPIRED = 0x06
    COMMAND_NOT_SUPPORTED = 0x07
    ADDRESS_TYPE_NOT_SUPPORTED = 0x08
    UNASSIGNED = 0x09


class AddressTypeCodes(Enum):
    IPv4 = 0x01
    DOMAIN_NAME = 0x03
    IPv6 = 0x04


class CommandCodes(Enum):
    CONNECT = 0x01
    BIND = 0x02
    UDP_ASSOCIATE = 0x03
