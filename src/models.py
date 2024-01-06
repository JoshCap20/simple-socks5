from dataclasses import dataclass

from .constants import AddressTypeCodes


@dataclass
class Address:
    name: str  # Domain name
    ip: str  # IPv4 or IPv6 address
    port: int  # Port number
    address_type: AddressTypeCodes  # IPv4, IPv6, or domain name, see AddressTypeCodes


@dataclass
class Request:
    version: int  # SOCKS version
    command: int  # Command code
    address: Address
