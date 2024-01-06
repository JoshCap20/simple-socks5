import unittest
from src.utils import generate_general_socks_server_failure_reply, generate_connection_refused_reply, generate_network_unreachable_reply, generate_host_unreachable_reply, generate_address_type_not_supported_reply
from src.constants import AddressTypeCodes, ReplyCodes

# TODO: Make the commented out tests fail. 
# Need to raise exceptions if domain name is used after initial connection setup.

class TestErrorUtils(unittest.TestCase):
    def test_generate_general_socks_server_failure_reply__ipv4(self):
        address_type = AddressTypeCodes.IPv4
        expected_reply = generate_general_socks_server_failure_reply(address_type)
        self.assertEqual(expected_reply, b'\x05\x01\x00\x01\x00\x00\x00\x00\x00\x00')
        
    def test_generate_general_socks_server_failure_reply__ipv6(self):
        address_type = AddressTypeCodes.IPv6
        expected_reply = generate_general_socks_server_failure_reply(address_type)
        self.assertEqual(expected_reply, b'\x05\x01\x00\x04\x00\x00\x00\x00\x00\x00')
        
    # def test_generate_general_socks_server_failure_reply__domain_name(self):
    #     address_type = AddressTypeCodes.DOMAIN_NAME
    #     expected_reply = generate_general_socks_server_failure_reply(address_type)
    #     self.assertEqual(expected_reply, b'\x05\x01\x00\x03\x00\x00\x00\x00\x00\x00')
        
    def test_generate_connection_refused_reply__ipv4(self):
        address_type = AddressTypeCodes.IPv4
        expected_reply = generate_connection_refused_reply(address_type)
        self.assertEqual(expected_reply, b'\x05\x05\x00\x01\x00\x00\x00\x00\x00\x00')
        
    def test_generate_connection_refused_reply__ipv6(self):
        address_type = AddressTypeCodes.IPv6
        expected_reply = generate_connection_refused_reply(address_type)
        self.assertEqual(expected_reply, b'\x05\x05\x00\x04\x00\x00\x00\x00\x00\x00')
        
    # def test_generate_connection_refused_reply__domain_name(self):
    #     address_type = AddressTypeCodes.IPv4
    #     expected_reply = generate_connection_refused_reply(address_type)
    #     self.assertEqual(expected_reply, b'\x05\x05\x00\x03\x00\x00\x00\x00\x00\x00')
    
    def test_generate_network_unreachable_reply__ipv4(self):
        address_type = AddressTypeCodes.IPv4
        expected_reply = generate_network_unreachable_reply(address_type)
        self.assertEqual(expected_reply, b'\x05\x03\x00\x01\x00\x00\x00\x00\x00\x00')
        
    def test_generate_network_unreachable_reply__ipv6(self):
        address_type = AddressTypeCodes.IPv6
        expected_reply = generate_network_unreachable_reply(address_type)
        self.assertEqual(expected_reply, b'\x05\x03\x00\x04\x00\x00\x00\x00\x00\x00')
        
    # def test_generate_network_unreachable_reply__domain_name(self):
    #     address_type = AddressTypeCodes.DOMAIN_NAME
    #     expected_reply = generate_network_unreachable_reply(address_type)
    #     self.assertEqual(expected_reply, b'\x05\x03\x00\x03\x00\x00\x00\x00\x00\x00')
    
    def test_generate_host_unreachable_reply__ipv4(self):
        address_type = AddressTypeCodes.IPv4
        expected_reply = generate_host_unreachable_reply(address_type)
        self.assertEqual(expected_reply, b'\x05\x04\x00\x01\x00\x00\x00\x00\x00\x00')
        
    def test_generate_host_unreachable_reply__ipv6(self):
        address_type = AddressTypeCodes.IPv6
        expected_reply = generate_host_unreachable_reply(address_type)
        self.assertEqual(expected_reply, b'\x05\x04\x00\x04\x00\x00\x00\x00\x00\x00')
        
    # def test_generate_host_unreachable_reply__domain_name(self):
    #     address_type = AddressTypeCodes.DOMAIN_NAME
    #     expected_reply = generate_host_unreachable_reply(address_type)
    #     self.assertEqual(expected_reply, b'\x05\x04\x00\x03\x00\x00\x00\x00\x00\x00')
    
    def test_generate_address_type_not_supported_reply__ipv4(self):
        address_type = AddressTypeCodes.IPv4
        expected_reply = generate_address_type_not_supported_reply(address_type)
        self.assertEqual(expected_reply, b'\x05\x08\x00\x01\x00\x00\x00\x00\x00\x00')
        
    def test_generate_address_type_not_supported_reply__ipv6(self):
        address_type = AddressTypeCodes.IPv6
        expected_reply = generate_address_type_not_supported_reply(address_type)
        self.assertEqual(expected_reply, b'\x05\x08\x00\x04\x00\x00\x00\x00\x00\x00')
        
    # def test_generate_address_type_not_supported_reply__domain_name(self):
    #     address_type = AddressTypeCodes.DOMAIN_NAME
    #     expected_reply = generate_address_type_not_supported_reply(address_type)
    #     self.assertEqual(expected_reply, b'\x05\x08\x00\x03\x00\x00\x00\x00\x00\x00')
        
if __name__ == '__main__':
    unittest.main()