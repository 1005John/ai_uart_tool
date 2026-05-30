# TCP/IP AT Command Functions for China Mobile IoT Modules
# Extracted from TCP_IP用户手册.pdf V5.1.6
# 所有参数默认值均来自手册

def set_mipcfg_cid(connect_id, cid=1):
    """
    设置TCP/IP连接实例的PDP上下文
    """
    return {
        'command': 'AT+MIPCFG',
        'send_data': f'AT+MIPCFG="cid",{connect_id},{cid}',
        'connect_id_range': {
            'default': [0, 5],
            'MN316/MN316-S/MN326': [0, 4],
            'MN316A/MN326A/MN319': [0, 3],
            'MR880A': [0, 9],
            'ML307H': [1, 5]  # 默认使用第1路
        },
        'cid_type': ['ipv4', 'ipv6'],
        'default_values': {
            'cid': 1,
            'ML307H_cid': 1  # 默认使用第1路
        },
        'not_supported': {
            'MN316/MN316-S/MN326': True,
            'MN316A/MN326A/MN319': True,
            'MR880A': True
        },
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }


def set_mipcfg_encoding(connect_id, send_format=0, recv_format=0):
    """
    设置TCP/IP连接的数据输入输出格式
    """
    return {
        'command': 'AT+MIPCFG',
        'send_data': f'AT+MIPCFG="encoding",{connect_id},{send_format},{recv_format}',
        'connect_id_range': {
            'default': [0, 5],
            'MN316/MN316-S/MN326': [0, 4],
            'MN316A/MN326A/MN319': [0, 3],
            'MR880A': [0, 9]
        },
        'default_values': {
            'send_format': 0,  # ASCII字符串（原始数据）
            'recv_format': 0  # ASCII字符串（原始数据）
        },
        'send_format_range': [0, 1, 2],  # 0:ASCII, 1:HEX, 2:带转义的字符串
        'recv_format_range': [0, 1],  # 0:ASCII, 1:HEX
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }


def set_mipcfg_timeout(connect_id, send_timeout=10):
    """
    设置发送超时时间
    """
    return {
        'command': 'AT+MIPCFG',
        'send_data': f'AT+MIPCFG="timeout",{connect_id},{send_timeout}',
        'connect_id_range': {
            'default': [0, 5],
            'MN316/MN316-S/MN326': [0, 4],
            'MN316A/MN326A/MN319': [0, 3],
            'MR880A': [0, 9]
        },
        'default_values': {
            'send_timeout': 10  # 单位：s
        },
        'send_timeout_range': {
            'default': [1, 180],
            'ML302S/ML307S/ML302A/ML305A/ML307A/ML307G/ML305M/ML307M/ML307N/ML307R/ML307H/ML307C': [1, 120]
        },
        'not_supported': {
            'MN316/MN316-S/MN326': True,
            'MN318': True,
            'MN316A/MN326A/MN319': True
        },
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }


def set_mipcfg_autofree(connect_id, free_mode=0):
    """
    设置连接异常断开后资源释放模式
    """
    return {
        'command': 'AT+MIPCFG',
        'send_data': f'AT+MIPCFG="autofree",{connect_id},{free_mode}',
        'connect_id_range': {
            'default': [0, 5],
            'MN316/MN316-S/MN326': [0, 4],
            'MN316A/MN326A/MN319': [0, 3],
            'MR880A': [0, 9]
        },
        'default_values': {
            'free_mode': 0  # 0:自动释放
        },
        'free_mode_range': [0, 1],  # 0:自动释放, 1:手动释放
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }


def set_mipcfg_sndbuf(connect_id, send_buffer=1460):
    """
    设置发送缓存大小
    """
    return {
        'command': 'AT+MIPCFG',
        'send_data': f'AT+MIPCFG="sndbuf",{connect_id},{send_buffer}',
        'connect_id_range': {
            'default': [0, 5],
            'MN316/MN316-S/MN326': [0, 4],
            'MN316A/MN326A/MN319': [0, 3],
            'MR880A': [0, 9]
        },
        'default_values': {
            'send_buffer': 1460  # 单位：字节，适用于数据模式下发送缓存的设置
        },
        'send_buffer_range': [1, 8192],
        'not_supported': {
            'MN316/MN316-S/MN316A/MN326A/MN326/ML302A/ML305A/ML307A/ML307G/ML302S/ML307S/ML305U/ML305M/ML307M/ML307R/ML307C/ML307N': True
        },
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }


def set_mipcfg_rcvbuf(connect_id, recv_buffer=65535):
    """
    设置接收缓存大小
    """
    default_recv_buffer = 65535  # Cat1模组默认值
    if any(model in ['NB'] for model in ['NB']):  # NB模组
        default_recv_buffer = 4096

    return {
        'command': 'AT+MIPCFG',
        'send_data': f'AT+MIPCFG="rcvbuf",{connect_id},{recv_buffer}',
        'connect_id_range': {
            'default': [0, 5],
            'MN316/MN316-S/MN326': [0, 4],
            'MN316A/MN326A/MN319': [0, 3],
            'MR880A': [0, 9]
        },
        'default_values': {
            'recv_buffer': {
                'NB模组': 4096,
                'Cat1模组': 65535,
                'MN318_TCP': 2048,
                'MN318_UDP': 4096,
                'ML307H': 65535,
                'MR880A': 65535
            }
        },
        'recv_buffer_range': {
            'default': [1, 65535],
            'MN316/MN316-S/MN326_UDP': [4096, 8192],
            'MN316A/MN326A/MN319_UDP': [1, 4096]
        },
        'tcp_not_supported': [
            'MN316/MN316-S/MN326', 'ML302A/ML305A/ML307A/ML302S/ML307S/ML305M/ML307M/ML307N/ML307R/ML307C/ML307G',
            'ML305U', 'ML307X/ML307Y', 'MN316A/MN326A/MN319', 'MN318', 'ML307H'
        ],
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }


def set_mipcfg_ackmode(connect_id, ack_mode=0):
    """
    设置TCP响应模式
    """
    return {
        'command': 'AT+MIPCFG',
        'send_data': f'AT+MIPCFG="ackmode",{connect_id},{ack_mode}',
        'connect_id_range': {
            'default': [0, 5],
            'MN316/MN316-S/MN326': [0, 4],
            'MN316A/MN326A/MN319': [0, 3],
            'MR880A': [0, 9]
        },
        'default_values': {
            'ack_mode': 0  # TCP接收ACK包时不上报URC
        },
        'ack_mode_range': [0, 1],  # 0:不上报, 1:上报
        'not_supported': {
            'MN316/MN316-S/MN326': True
        },
        'udp_invalid': True,
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }


def set_miptka(connect_id, keepalive=0, keepidle=90, keepinterval=75, keepcount=3):
    """
    设置TCP心跳参数
    """
    # 根据型号设置默认值
    if any(model in ['MN316', 'MN316-S', 'MN326'] for model in ['MN316', 'MN316-S', 'MN326']):
        keepidle_default = 30
        keepinterval_default = 90
    else:
        keepidle_default = 90
        keepinterval_default = 75

    return {
        'command': 'AT+MIPTKA',
        'send_data': f'AT+MIPTKA={connect_id},{keepalive},{keepidle},{keepinterval},{keepcount}',
        'connect_id_range': {
            'default': [0, 5],
            'MN316/MN316-S/MN326': [0, 4],
            'MN316A/MN326A/MN319': [0, 3],
            'MR880A': [0, 9]
        },
        'default_values': {
            'keepalive': 0,  # 关闭心跳
            'keepidle': keepidle_default,  # 单位：s
            'keepinterval': keepinterval_default,  # 单位：s
            'keepcount': 3  # 心跳包重传次数
        },
        'keepalive_range': [0, 1],  # 0:关闭, 1:打开
        'keepidle_range': [30, 7200],
        'keepinterval_range': [30, 600],
        'keepcount_range': [1, 9],
        'udp_not_supported': True,
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }


def set_mipopen(connect_id, proto_type, address, remote_port, timeout=60, access_mode=0, local_port=0):
    """
    建立TCP/IP连接
    """
    mipopen_data = {'command': 'AT+MIPOPEN',
        'send_data': f'AT+MIPOPEN={connect_id},"{proto_type}","{address}",{remote_port},{timeout},{access_mode},{local_port}',
        'connect_id_range': {
            'default': [0, 5],
            'MN316/MN316-S/MN326': [0, 4],
            'MN316A/MN326A/MN319': [0, 3],
            'MR880A': [0, 9]
        },
        'default_values': {
            'timeout': 60,  # 单位：s
            'access_mode': 0,  # 普通模式
            'local_port': 0  # 系统自动分配本地端口号
        },
        'proto_type': ['TCP', 'UDP'],
        'remote_port_range': [0, 65535],
        'timeout_range': [1, 180],
        'access_mode_range': [0, 1, 2, 3],
        'local_port_range': [0, 65535],
        'address_type': ['域名', 'ip'],
        'not_supported_transparent': ['MN316/MN316-S/MN316A/MN326A/MN318/MN319/MN326'],
        'result': [
            r'OK',
            rf'\+MIPOPEN: {connect_id},\d+',
            r'CONNECT'  # 透传模式下连接成功
        ],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']}
    return mipopen_data


def set_mipclose(connect_id, mode=0):
    """
    关闭TCP/IP连接
    """
    return {
        'command': 'AT+MIPCLOSE',
        'send_data': f'AT+MIPCLOSE={connect_id},{mode}',
        'connect_id_range': {
            'default': [0, 5],
            'MN316/MN316-S/MN326': [0, 4],
            'MN316A/MN326A/MN319': [0, 3],
            'MR880A': [0, 9]
        },
        'default_values': {
            'mode': 0  # 等待发送缓存区数据发送完毕后关闭TCP连接
        },
        'mode_range': [0, 1, 2, 3, 4],
        'mode_not_supported': {
            'MN316/MN316-S/MN319/MN326': True,
            'MN316A/MN326A': True,
            'MN318': True,
            'ML302A/ML305A/ML307A/ML302S/ML307S/ML305U/ML305M/ML307M/ML307N/ML307R/ML307X/ML307Y': True,
            'ML307G': [0, 3],  # 支持0-3
            'ML307H': True,
            'MR880A': True
        },
        'result': [
            r'OK',
            rf'\+MIPCLOSE: {connect_id}'
        ],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }


def set_mipsend(connect_id, send_length=None, data=None, rai=0, seq=None, pri_flag=0):
    """
    发送TCP/UDP数据
    """
    if send_length is not None and data is not None:
        send_data = f'AT+MIPSEND={connect_id},{send_length},"{data}",{rai}'
        if seq is not None:
            send_data += f',{seq}'
        send_data += f',{pri_flag}'
    elif send_length is not None:
        send_data = f'AT+MIPSEND={connect_id},{send_length}'
    else:
        send_data = f'AT+MIPSEND={connect_id}'

    return {
        'command': 'AT+MIPSEND',
        'send_data': send_data,
        'connect_id_range': {
            'default': [0, 5],
            'MN316/MN316-S/MN326': [0, 4],
            'MN316A/MN326A/MN319': [0, 3],
            'MR880A': [0, 9]
        },
        'default_values': {
            'rai': 0,  # 无信息
            'pri_flag': 0  # IPTOS可靠性
        },
        'send_length_range': {
            'command_mode': [0, 1460],
            'data_mode': [1, 8192]
        },
        'rai_range': [0, 1, 2],
        'seq_range': [1, 255],
        'pri_flag_range': [0, 1, 2, 3],
        'not_supported_rai': ['MN316/MN316-S/MN316A/MN326A/MN318/MN326_TCP', 'AG系列/MN319/MR880A'],
        'not_supported_seq': ['AG系列/MR880A'],
        'not_supported_udp_empty': ['MN316/MN316-S/MN316A/MN326A/MN326/MN318'],
        'result': [
            r'OK',
            rf'\+MIPSEND: {connect_id},\d+'
        ],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }


def set_miprd_tcp(connect_id, read_len=None):
    """
    读取TCP缓存数据
    """
    if read_len is not None:
        send_data = f'AT+MIPRD={connect_id},{read_len}'
    else:
        send_data = f'AT+MIPRD={connect_id}'

    return {
        'command': 'AT+MIPRD',
        'send_data': send_data,
        'connect_id_range': {
            'default': [0, 5],
            'MN316/MN316-S/MN326': [0, 4],
            'MN316A/MN326A/MN319': [0, 3],
            'MR880A': [0, 9]
        },
        'read_len_range': {
            'default': [0, 4096],
            'MN316A/MN326A/MN319': [1, 1460]
        },
        'result': [
            r'OK',
            rf'\+MIPRD: {connect_id},\d+(,\d+,"[^"]*")?'
        ],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }


def set_miprd_udp(connect_id, pack_count=None):
    """
    读取UDP缓存数据
    """
    if pack_count is not None:
        send_data = f'AT+MIPRD={connect_id},{pack_count}'
    else:
        send_data = f'AT+MIPRD={connect_id}'

    return {
        'command': 'AT+MIPRD',
        'send_data': send_data,
        'connect_id_range': {
            'default': [0, 5],
            'MN316/MN316-S/MN326': [0, 4],
            'MN316A/MN326A/MN319': [0, 3],
            'MR880A': [0, 9]
        },
        'default_values': {
            'pack_count': 0  # 读取全部缓存数据
        },
        'pack_count_range': {
            'NB': [0, 12],
            'Cat1': [0, 256],
            'ML305A/ML307A/ML307N': [0, 128],
            'ML307H': [0, 45],
            'MR880A': [0, 256]
        },
        'not_supported_multi_pack': ['MN316A/MN326A/MN319'],
        'result': [
            r'OK',
            rf'\+MIPRD: {connect_id},\d+(,\d+,"[^"]*")?'
        ],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }


def set_mipmode(connect_id, access_mode=None, packet_size=1024, waittm=200):
    """
    切换数据模式
    """
    if access_mode is not None:
        send_data = f'AT+MIPMODE={connect_id},{access_mode},{packet_size},{waittm}'
    else:
        send_data = f'AT+MIPMODE={connect_id}'

    return {
        'command': 'AT+MIPMODE',
        'send_data': send_data,
        'connect_id_range': {
            'default': [0, 5],
            'MN316/MN316-S/MN326': [0, 4],
            'MN316A/MN326A/MN319': [0, 3],
            'MR880A': [0, 9]
        },
        'default_values': {
            'packet_size': 1024,  # 单位：字节
            'waittm': 200  # 单位：ms
        },
        'access_mode_range': [0, 1, 2, 3],
        'packet_size_range': [512, 1460],
        'waittm_range': [0, 2000],
        'not_supported_transparent': ['MN316/MN316-S/MN316A/MN326A/MN318/MN319/MN326'],
        'not_supported_packet_size': [
            'ML302S/ML307S/ML302A/ML305A/ML307A/ML307G/ML305U/ML305M/ML307M/ML307N/ML307R/ML307C/ML307X/ML307Y'],
        'not_supported_waittm': [
            'ML302A/ML305A/ML307A/ML302S/ML307S/ML307G/ML305U/ML305M/ML307M/ML307N/ML307R/ML307C/ML307X/ML307Y'],
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }


def set_mipstate(connect_id=None):
    """
    查询TCP/IP连接状态
    """
    if connect_id is not None:
        send_data = f'AT+MIPSTATE={connect_id}'
    else:
        send_data = 'AT+MIPSTATE?'

    return {
        'command': 'AT+MIPSTATE',
        'send_data': send_data,
        'connect_id_range': {
            'default': [0, 5],
            'MN316/MN316-S/MN326': [0, 4],
            'MN316A/MN326A/MN319': [0, 3],
            'MR880A': [0, 9]
        },
        'service_type': ['TCP', 'UDP'],
        'state_values': ['INITIAL', 'CONNECTING', 'CONNECTED', 'CLOSING', 'CLOSED'],
        'result': [
            r'OK',
            r'\+MIPSTATE: \d+,"(TCP|UDP)","[^"]*",\d+,"(INITIAL|CONNECTING|CONNECTED|CLOSING|CLOSED)"'
        ],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }


def set_mipsack(connect_id):
    """
    查询已发送数据的ACK信息
    """
    return {
        'command': 'AT+MIPSACK',
        'send_data': f'AT+MIPSACK={connect_id}',
        'connect_id_range': {
            'default': [0, 5],
            'MN316/MN316-S/MN326': [0, 4],
            'MN316A/MN326A/MN319': [0, 3]
        },
        'not_supported': ['MN316/MN316-S/MN326'],
        'udp_acked_fixed': 0,  # UDP连接acked固定为0
        'result': [
            r'OK',
            rf'\+MIPSACK: \d+,\d+,\d+,\d+'
        ],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }


def set_mdnscfg_ip(address1="", address2=""):
    """
    设置IPv4域名解析服务器地址
    """
    send_data = f'AT+MDNSCFG="ip","{address1}","{address2}"' if address1 or address2 else 'AT+MDNSCFG="ip"'

    return {
        'command': 'AT+MDNSCFG',
        'send_data': send_data,
        'default_values': {
            'address1': '119.29.29.29',
            'address2': '114.114.114.114',
            'NB_46003_46005_460011_address1': '218.4.4.4'  # SIM卡PLMN是46003、46005、460011时的默认值
        },
        'address_type': ['域名', 'ip'],
        'not_supported_setting': ['MR880A'],
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }


def set_mdnscfg_ipv6(address1="", address2=""):
    """
    设置IPv6域名解析服务器地址
    """
    send_data = f'AT+MDNSCFG="ipv6","{address1}","{address2}"' if address1 or address2 else 'AT+MDNSCFG="ipv6"'

    return {
        'command': 'AT+MDNSCFG',
        'send_data': send_data,
        'default_values': {
            'address1': '2400:3200::1',
            'address2': '2001:4860:4860::8888'
        },
        'address_type': ['ipv6'],
        'not_supported_setting': ['MR880A'],
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }


def set_mdnscfg_priority(priority=1):
    """
    设置解析协议优先级
    """
    return {
        'command': 'AT+MDNSCFG',
        'send_data': f'AT+MDNSCFG="priority",{priority}',
        'default_values': {
            'priority': 1  # IPv6优先
        },
        'priority_range': [0, 1],  # 0:IPv4优先, 1:IPv6优先
        'not_save_nv': ['ML302A/ML305A/ML307A/ML307G/ML302S/ML307S/ML305U/ML305M/ML307M/ML307N/ML307R/ML307H/ML307C'],
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }


def set_mdnscfg_cached(cached_mode=0, cached_period=3600):
    """
    设置DNS缓存模式
    """
    return {
        'command': 'AT+MDNSCFG',
        'send_data': f'AT+MDNSCFG="cached",{cached_mode},{cached_period}',
        'default_values': {
            'cached_mode': 0,  # 使用缓存
            'cached_period': 3600  # 单位：s，默认3600s
        },
        'cached_mode_range': [0, 1],  # 0:使用缓存, 1:不使用缓存
        'cached_period_range': [1, 65535],
        'not_supported_cached': ['MN316/MN316-S/MN316A/MN326A/MN318/MN319/MN326/ML307X/ML307Y'],
        'not_supported_period': ['ML307G/ML307H'],
        'special_defaults': {
            'ML307G': {'cached_mode': 1}  # ML307G默认值为1
        },
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }


def set_mdnscfg_timeout(time=10, retries=3):
    """
    设置DNS超时参数
    """
    return {
        'command': 'AT+MDNSCFG',
        'send_data': f'AT+MDNSCFG="timeout",{time},{retries}',
        'default_values': {
            'time': {
                'NB模组': 30,
                '4G/5G模组': 10
            },
            'retries': 3
        },
        'time_range': [1, 60],
        'retries_range': [1, 9],
        'not_supported_retry': ['MR880A'],
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }


def set_mdnsgip(domainname, cid=None):
    """
    域名解析
    """
    if cid is not None:
        send_data = f'AT+MDNSGIP="{domainname}",{cid}'
    else:
        send_data = f'AT+MDNSGIP="{domainname}"'

    return {
        'command': 'AT+MDNSGIP',
        'send_data': send_data,
        'domainname_max_length': 255,
        'cid_range': '与AT+CGDCONT命令支持的范围相同',
        'max_ip_return': 4,
        'default_cid': {
            '4G系列': 1  # 默认为1
        },
        'not_supported_cid': ['MN316/MN316-S/MN316A/MN326A/MN318/MN319/MN326/ML307G/MR880A/ML307H'],
        'result': [
            r'OK',
            r'\+MDNSGIP: "[^"]*"(,"[^"]*"){1,4}'
        ],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }


def set_mping(host, timeout=10, ping_num=4, packet_len=16, cid=None):
    """
    PING服务器
    """
    params = [f'"{host}"', str(timeout), str(ping_num), str(packet_len)]
    if cid is not None:
        params.append(str(cid))

    send_data = f'AT+MPING={",".join(params)}'

    return {
        'command': 'AT+MPING',
        'send_data': send_data,
        'default_values': {
            'timeout': 10,  # 单位：s
            'ping_num': 4,
            'packet_len': 16  # 单位：字节
        },
        'host_type': ['域名', 'ip'],
        'host_max_length': 255,
        'timeout_range': [1, 60],
        'ping_num_range': [1, 65535],
        'packet_len_range': [1, 1400],
        'cid_range': '与AT+CGDCONT命令支持的范围相同',
        'default_cid': {
            '4G系列': 1  # 默认为1
        },
        'not_supported_cid': ['MN316/MN316-S/MN316A/MN326A/MN319/MN326/ML307H/MR880A'],
        'result': [
            r'OK',
            r'\+MPING: \d+,"[^"]*",\d+,\d+,\d+',
            r'\+MPING: "statistics",\d+,\d+,\d+,\d+,\d+'
        ],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }


def exit_transparent_mode():
    """
    退出透传模式
    """
    return {
        'command': '+++',
        'send_data': '+++',
        'interval_requirement': {
            'ML307X/ML307Y': '1秒间隔'
        },
        'not_supported': ['MN316/MN316-S/MN316A/MN326A/MN318/MN319/MN326'],
        'result': [r'OK'],
        'err_result': []
    }


def set_mntp(server="ntp1.aliyun.com", port=123, sync=1, timeout=20):
    """
    网络时间同步
    """
    return {
        'command': 'AT+MNTP',
        'send_data': f'AT+MNTP="{server}",{port},{sync},{timeout}',
        'default_values': {
            'server': 'ntp1.aliyun.com',
            'port': 123,
            'sync': 1,  # 更新本地RTC计时器的时间
            'timeout': 20  # 单位：s
        },
        'special_defaults': {
            'server': {
                'ML307X/ML307Y': 'ntp7.aliyun.com'
            },
            'timeout': {
                'ML302A/ML305A/ML307A/ML307G/ML302S/ML307S/ML307R/ML307H/ML307C': 30
            }
        },
        'server_max_length': 255,
        'port_range': [0, 65535],
        'sync_range': [0, 1],  # 0:不更新, 1:更新
        'timeout_range': [1, 300],
        'result_codes': [0, 1, 2, 3],  # 0:成功, 1:DNS错误, 2:超时, 3:时间同步失败
        'result': [
            r'OK',
            r'\+MNTP: \d+,"\d{2}/\d{2}/\d{2},\d{2}:\d{2}:\d{2}\+\d+"'
        ],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }


# Server模式相关命令（仅适用于MR880A）
def set_mipsrvcfg_cid(sid, cid=None):
    """
    设置服务器实例的PDP上下文（仅MR880A）
    """
    if cid is not None:
        send_data = f'AT+MIPSRVCFG="cid",{sid},{cid}'
    else:
        send_data = f'AT+MIPSRVCFG="cid",{sid}'

    return {
        'command': 'AT+MIPSRVCFG',
        'send_data': send_data,
        'supported_models': ['MR880A'],
        'sid_range': [0, 3],
        'cid_range': '与AT+CGDCONT命令支持的范围相同',
        'not_supported_cid': ['MR880A'],
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }


def set_mipsrvcfg_encoding(sid, recv_format=0):
    """
    设置服务器新连接的数据接收格式（仅MR880A）
    """
    return {
        'command': 'AT+MIPSRVCFG',
        'send_data': f'AT+MIPSRVCFG="encoding",{sid},{recv_format}',
        'supported_models': ['MR880A'],
        'sid_range': [0, 3],
        'default_values': {
            'recv_format': 0  # ASCII字符串（原始数据）
        },
        'recv_format_range': [0, 1],  # 0:ASCII, 1:HEX
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }


def set_mipsrvcfg_rcvbuf(sid, recv_buffer=65535):
    """
    设置服务器新连接的接收缓存大小（仅MR880A）
    """
    return {
        'command': 'AT+MIPSRVCFG',
        'send_data': f'AT+MIPSRVCFG="rcvbuf",{sid},{recv_buffer}',
        'supported_models': ['MR880A'],
        'sid_range': [0, 3],
        'default_values': {
            'recv_buffer': 65535  # 单位：字节
        },
        'recv_buffer_range': [1, 65535],
        'tcp_config_valid': True,  # MR880A中TCP协议配置有效
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }


def set_miplisten(sid, protocol, port, ip_type="IP", access_mode=0):
    """
    进入服务器监听模式（仅MR880A）
    """
    return {
        'command': 'AT+MIPLISTEN',
        'send_data': f'AT+MIPLISTEN={sid},"{protocol}",{port},"{ip_type}",{access_mode}',
        'supported_models': ['MR880A'],
        'sid_range': [0, 3],
        'default_values': {
            'ip_type': 'IP',  # IPv4类型
            'access_mode': 0  # 普通模式
        },
        'protocol': ['TCP', 'UDP'],
        'port_range': [1, 65535],
        'ip_type': ['IP', 'IPV6'],  # IP:IPv4类型, IPV6:IPv6类型
        'access_mode_range': [0, 2, 3],  # 服务器模式不支持透传模式(1)
        'result': [
            r'OK',
            rf'\+MIPLISTEN: {sid},\d+'
        ],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }


def set_mipsrvstate(sid=None):
    """
    查询服务器状态（仅MR880A）
    """
    if sid is not None:
        send_data = f'AT+MIPSRVSTATE={sid}'
    else:
        send_data = 'AT+MIPSRVSTATE?'

    return {
        'command': 'AT+MIPSRVSTATE',
        'send_data': send_data,
        'supported_models': ['MR880A'],
        'sid_range': [0, 3],
        'svstate_values': ['INITIAL', 'OPENNING', 'LISTENING', 'CLOSING'],
        'result': [
            r'OK',
            r'\+MIPSRVSTATE( \d+,"(INITIAL|OPENNING|LISTENING|CLOSING)",\d+,\d+,\d+)+'
        ],
        'err_result': [r'ERROR']
    }


def set_mipsrvclose(sid, mode=0):
    """
    关闭服务器模式（仅MR880A）
    """
    return {
        'command': 'AT+MIPSRVCLOSE',
        'send_data': f'AT+MIPSRVCLOSE={sid},{mode}',
        'supported_models': ['MR880A'],
        'sid_range': [0, 3],
        'default_values': {
            'mode': 0  # 等待发送缓存区数据发送完毕后关闭TCP连接
        },
        'mode_range': [0, 1, 2, 3, 4],
        'mode_not_supported': ['MR880A'],  # MR880A不支持mode参数配置
        'result': [r'OK'],
        'err_result': [r'ERROR']
    }


def set_miprdu_udp(connect_id, pack_count=None):
    """
    UDP读取缓存数据（仅MR880A）
    """
    if pack_count is not None:
        send_data = f'AT+MIPRDU={connect_id},{pack_count}'
    else:
        send_data = f'AT+MIPRDU={connect_id}'

    return {
        'command': 'AT+MIPRDU',
        'send_data': send_data,
        'supported_models': ['MR880A'],
        'connect_id_range': [0, 9],
        'default_values': {
            'pack_count': 0  # 读取全部缓存数据
        },
        'pack_count_range': [0, 256],
        'tcp_not_supported': True,
        'result': [
            r'OK',
            r'\+MIPRDU: \d+,"[^"]*",\d+,\d+,\d+,"[^"]*"'
        ],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }


def set_mipsendto_udp(connect_id, addr, port, send_length=None, data=None, rai=0, seq=None, pri_flag=0):
    """
    UDP指定地址发送数据（仅MR880A）
    """
    if send_length is not None and data is not None:
        send_data = f'AT+MIPSENDTO={connect_id},{addr},{port},{send_length},"{data}",{rai}'
        if seq is not None:
            send_data += f',{seq}'
        send_data += f',{pri_flag}'
    elif send_length is not None:
        send_data = f'AT+MIPSENDTO={connect_id},{addr},{port},{send_length}'
    else:
        send_data = f'AT+MIPSENDTO={connect_id},{addr},{port}'

    return {
        'command': 'AT+MIPSENDTO',
        'send_data': send_data,
        'supported_models': ['MR880A'],
        'connect_id_range': [0, 9],
        'default_values': {
            'rai': 0,  # 无信息
            'pri_flag': 0  # IPTOS可靠性
        },
        'port_range': [1, 65535],
        'send_length_range': {
            'command_mode': [0, 1460],
            'data_mode': [1, 8192]
        },
        'not_supported_rai': ['MR880A'],
        'not_supported_seq': ['MR880A'],
        'result': [
            r'OK',
            rf'\+MIPSENDTO: {connect_id},\d+'
        ],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }