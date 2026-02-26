"""
Standardized log messages.
"""
import string

connection_established_template = string.Template(
    "CONNECTION | ($src_domain_name) $src_ip:$src_port <-> ($dst_domain_name) $dst_ip:$dst_port"
)
connection_closed_template = string.Template(
    "CLOSED | ($src_domain_name) $src_ip:$src_port <-> ($dst_domain_name) $dst_ip:$dst_port"
)
base_relay_template = string.Template(
    "RELAY | $protocol | $src_ip:$src_port -> $dst_ip:$dst_port | $data_size bytes"
)
detailed_relay_template = string.Template(
    "RELAY | $protocol | ($src_domain_name) $src_ip:$src_port -> "
    "($dst_domain_name) $dst_ip:$dst_port | $data_size bytes"
)
