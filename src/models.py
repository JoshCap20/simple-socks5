from dataclasses import dataclass
from collections import namedtuple

from .constants import AddressTypeCodes


@dataclass
class Address:
    name: str  # Domain name
    ip: str  # IPv4 or IPv6 address
    port: int  # Port number
    address_type: AddressTypeCodes  # IPv4, IPv6, or domain name, see AddressTypeCodes

    def __str__(self):
        return f"{self.name}, {self.ip}:{self.port}"


@dataclass
class Request:
    version: int  # SOCKS version
    command: int  # Command code
    address: Address


BindAddress = namedtuple("BindAddress", ["ip", "port"])
