"""
This file contains the configuration for the proxy server set at runtime.
"""
from .models import BaseAddress


class ProxyConfiguration:
    _host: str
    _port: int
    _logging_level: int
    _use_tor: bool = False

    @classmethod
    def initialize(cls, host: str, port: int, logging_level: int) -> None:
        ProxyConfiguration._host = host
        ProxyConfiguration._port = port
        ProxyConfiguration._logging_level = logging_level

    @classmethod
    def enable_tor(cls) -> None:
        ProxyConfiguration._use_tor = True

    @classmethod
    def is_tor_enabled(cls) -> bool:
        return ProxyConfiguration._use_tor

    @classmethod
    def is_initialized(cls) -> bool:
        return (
            hasattr(ProxyConfiguration, "host")
            and hasattr(ProxyConfiguration, "port")
            and hasattr(ProxyConfiguration, "logging_level")
        )

    @classmethod
    def get_logging_level(cls) -> int:
        return ProxyConfiguration._logging_level * 10

    @classmethod
    def get_host(cls) -> str:
        return ProxyConfiguration._host

    @classmethod
    def get_port(cls) -> int:
        return ProxyConfiguration._port

    @classmethod
    def get_address(cls) -> BaseAddress:
        return BaseAddress(ProxyConfiguration._host, ProxyConfiguration._port)
