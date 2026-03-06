def format_packet_log(packet):
    """
    Format a packet dictionary into a readable log string for AI analysis.
    """
    src_ip = packet.get('src_ip', 'unknown')
    dst_ip = packet.get('dst_ip', 'unknown')
    protocol = packet.get('protocol', 'unknown')
    length = packet.get('length', 'unknown')
    src_port = packet.get('src_port', 'unknown')
    dst_port = packet.get('dst_port', 'unknown')
    flags = packet.get('flags', 'unknown')
    direction = packet.get('direction', 'unknown')

    log_text = f"Packet log: Source IP {src_ip}, Destination IP {dst_ip}, Protocol {protocol}, Length {length}, Source Port {src_port}, Destination Port {dst_port}, Flags {flags}, Direction {direction}."
    return log_text
