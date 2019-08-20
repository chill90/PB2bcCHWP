# Boolean flag for Ethernet to IP
use_tcp = True

# MOXA IP address
tcp_ip = '192.168.2.52'
tcp_port = 4002

# CHWP Gripper ttyUSB port
if not tcp:
    rtu_port = '/dev/ttyUSB8'
