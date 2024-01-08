"""
Standardized log messages.
"""
import string

connection_template = string.Template("CONN | $name | $ip:$port | $address_type")
connection_closed_template = string.Template(
    "TERM | ($src_domain_name) $src_ip:$src_port <-> ($dst_domain_name) $dst_ip:$dst_port"
)
base_relay_template = string.Template(
    "RELAY | $protocol | $src_ip:$src_port -> $dst_ip:$dst_port | $data_size bytes"
)
detailed_relay_template = string.Template(
    "RELAY | $protocol | ($src_domain_name) $src_ip:$src_port -> ($dst_domain_name) $dst_ip:$dst_port | $data_size bytes"
)
