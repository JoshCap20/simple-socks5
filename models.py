from dataclasses import dataclass
from constants import AddressTypeCodes

@dataclass
class Address:
    name: str # Domain name if address_type is DOMAIN_NAME, otherwise IP address
    ip: str # IPv4 or IPv6
    port: int # Port number
    address_type: AddressTypeCodes
    
@dataclass
class Request:
    version: int
    command: int
    address: Address