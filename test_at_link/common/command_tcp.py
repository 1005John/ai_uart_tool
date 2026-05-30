def set_mipcfg_cid(connect_id=0, cid=1):
    mipcfg_cid = {
        'command': 'AT+MIPCFG',
        'send_data': f'AT+MIPCFG="cid",{connect_id},{cid}',
        'search_data': f'AT+MIPCFG="cid",{connect_id}',
        'cid_range': {
            'default': [1, 15],
            'ML302S/ML307S/ML302A/ML305A/ML307A/ML307R/ML307C': {"range": [1, 7], "extra_values": [9, 15]},  # 支持1-7以及9和15
            'ML307B': [0, 4],  # ML307B单独配置：支持0-4
            'ML305U': [1,7],
            'ML305M/ML307M/ML307N': [1,8],
            'ML307X/ML307Y': [1,15],
            'M5310-E': [],  # 不支持该参数
            'MN316/MN316-S/MN326': [],  # 不支持该参数
            'MN316A/MN326A/MN319/MN319-A': [],  # 不支持该参数
            'MR880A': [],  # 不支持该参数
            'ML307H-GU': [],  # 不支持该参数
            'MN327': [1, 7],
            'ML307G/ML307H': [1, 5]
        },
        'connect_id_range': {
            'default': [0, 5],
            'M5310-E/MN316/MN316-S/MN326': [0, 4],
            'MN316A/MN326A/MN319/MN319-A': [0, 3],
            'MR880A': [0, 9]
        },
        'default_values': {
            'connect_id': 0,
            'cid': 1
        },
        'model_specific_defaults': {
            'ML307B': {'cid': 0}
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MIPCFG: "cid",{connect_id},{cid}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mipcfg_cid

def set_mipcfg_encoding(connect_id=0, send_format=0, recv_format=0):
    mipcfg_encoding = {
        'command': 'AT+MIPCFG',
        'send_data': f'AT+MIPCFG="encoding",{connect_id},{send_format},{recv_format}',
        'search_data': f'AT+MIPCFG="encoding",{connect_id}',
        'send_format_range': (0, 1, 2),  # 0: ASCII, 1: HEX, 2: 转义字符串
        'recv_format_range': (0, 1),  # 0: ASCII, 1: HEX
        'connect_id_range': {
            'default': [0, 5],
            'M5310-E/MN316/MN316-S/MN326': [0, 4],
            'MN316A/MN326A/MN319/MN319-A': [0, 3],
            'MR880A': [0, 9]
        },
        'default_values': {
            'connect_id': 0,
            'send_format': 0,
            'recv_format': 0
        },
        'special_notes': {
            'MR880A': '不支持转义字符输入'
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MIPCFG: "encoding",{connect_id},{send_format},{recv_format}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mipcfg_encoding

def set_mipcfg_timeout(connect_id=0, send_timeout=10):
    mipcfg_timeout = {
        'command': 'AT+MIPCFG',
        'send_data': f'AT+MIPCFG="timeout",{connect_id},{send_timeout}',
        'search_data': f'AT+MIPCFG="timeout",{connect_id}',
        'send_timeout_range': {
            'default': [1, 180],
            'ML302S/ML307S/ML302A/ML305A/ML307A/ML307G/ML305M/ML307M/ML307N/ML307R/ML307B/ML307H/ML307C': [1, 120]
        },
        'connect_id_range': {
            'default': [0, 5],
            'M5310-E/MN316/MN316-S/MN326': [0, 4],
            'MN316A/MN326A/MN319/MN319-A': [0, 3],
            'MR880A': [0, 9]
        },
        'default_values': {
            'connect_id': 0,
            'send_timeout': 10
        },
        'not_supported': ['M5310-E', 'MN316', 'MN316-S', 'MN326', 'MN316A', 'MN326A', 'MN319', 'MN319-A', 'MR880A'],
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MIPCFG: "timeout",{connect_id},{send_timeout}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mipcfg_timeout

def set_mipcfg_autofree(connect_id=0, free_mode=0):
    mipcfg_autofree = {
        'command': 'AT+MIPCFG',
        'send_data': f'AT+MIPCFG="autofree",{connect_id},{free_mode}',
        'search_data': f'AT+MIPCFG="autofree",{connect_id}',
        'free_mode_range': (0, 1),  # 0: 自动释放, 1: 手动释放
        'connect_id_range': {
            'default': [0, 5],
            'M5310-E/MN316/MN316-S/MN326': [0, 4],
            'MN316A/MN326A/MN319/MN319-A': [0, 3],
            'MR880A': [0, 9]
        },
        'default_values': {
            'connect_id': 0,
            'free_mode': 0
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MIPCFG: "autofree",{connect_id},{free_mode}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mipcfg_autofree

def set_mipcfg_sndbuf(connect_id=0, send_buffer=1460):
    """
    设置TCP/IP发送缓冲区配置函数
    """
    mipcfg_sndbuf = {
        'command': 'AT+MIPCFG',
        'send_data': f'AT+MIPCFG="sndbuf",{connect_id},{send_buffer}',
        'search_data': f'AT+MIPCFG="sndbuf",{connect_id}',
        
        # 参数取值范围
        'connect_id_range': {
            'default': [0, 5],
            'M5310-E/MN316/MN316-S/MN326': [0, 4],
            'MN316A/MN326A/MN319/MN319-A': [0, 3],
            'MR880A': [0, 9]
        },
        'send_buffer_range': {
            'default': [1, 8192]
        },
        
        # 不支持设置的型号列表
        'not_supported_models': [
            "M5310-E", "MN316", "MN316-S", "MN316A", "MN326A", "MN326", 
            "ML302A", "ML305A", "ML307A", "ML307G", "ML302S", "ML307S", 
            "ML305U", "ML305M", "ML307M", "ML307R", "ML307B", "ML307C"
        ],
        
        # 默认值
        'default_values': {
            'connect_id': 0,
            'send_buffer': 1460
        },
        
        # 预期结果
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MIPCFG: "sndbuf",{connect_id},{send_buffer}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mipcfg_sndbuf

def set_mipcfg_rcvbuf(connect_id=0, recv_buffer=65535):
    mipcfg_rcvbuf = {
        'command': 'AT+MIPCFG',
        'send_data': f'AT+MIPCFG="rcvbuf",{connect_id},{recv_buffer}',
        'search_data': f'AT+MIPCFG="rcvbuf",{connect_id}',
        'recv_buffer_range': {
            'default': [1, 65535],
            'MN316/MN316-S/MN326': [4096, 8192],  # UDP协议范围
            'ML302A/ML305A/ML307A/ML302S/ML307S/ML305M/ML307M/ML307N/ML307R/ML307C/ML307G': [1460, 65535],  # UDP协议范围
            'MN316A/MN326A/MN319/MN319-A': [1, 4096],  # UDP协议范围
            'MN318/MN328': []  # 不支持设置
        },
        'connect_id_range': {
            'default': [0, 5],
            'M5310-E/MN316/MN316-S/MN326': [0, 4],
            'MN316A/MN326A/MN319/MN319-A': [0, 3],
            'MR880A': [0, 9]
        },
        'default_values': {
            'connect_id': 0,
            'recv_buffer': 65535
        },
        'special_notes': {
            'NB模组': '默认值4096',
            'Cat1模组': '默认值65535',
            'MN316/MN316-S/MN326': 'TCP滑动窗口大小为4096不可变',
            'ML302A系列': 'TCP接收缓存为滑动窗口大小，默认64240字节，配置无效',
            'ML305U': 'TCP配置无效，默认63920字节',
            'ML307X/ML307Y': 'TCP配置无效，默认65534字节',
            'MN316A系列': 'TCP配置无效，滑动窗口默认2048字节',
            'MN318/MN328': 'TCP滑动窗口默认2048字节，UDP缓存默认4096字节'
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MIPCFG: "rcvbuf",{connect_id},{recv_buffer}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mipcfg_rcvbuf

def set_mipcfg_ackmode(connect_id=0, ack_mode=0):
    mipcfg_ackmode = {
        'command': 'AT+MIPCFG',
        'send_data': f'AT+MIPCFG="ackmode",{connect_id},{ack_mode}',
        'search_data': f'AT+MIPCFG="ackmode",{connect_id}',
        'ack_mode_range': (0, 1),  # 0: 不上报URC, 1: 上报URC
        'connect_id_range': {
            'default': [0, 5],
            'M5310-E/MN316/MN316-S/MN326': [0, 4],
            'MN316A/MN326A/MN319/MN319-A': [0, 3],
            'MR880A': [0, 9]
        },
        'default_values': {
            'connect_id': 0,
            'ack_mode': 0
        },
        'not_supported': ['MN316', 'MN316-S', 'MN326'],
        'special_notes': {
            'UDP协议': '该参数无效'
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MIPCFG: "ackmode",{connect_id},{ack_mode}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mipcfg_ackmode

def set_mipcfg_ssl(connect_id=0, ssl_enable=0, ssl_id=0):
    mipcfg_ssl = {
        'command': 'AT+MIPCFG',
        'send_data': f'AT+MIPCFG="ssl",{connect_id},{ssl_enable},{ssl_id}',
        'search_data': f'AT+MIPCFG="ssl",{connect_id}',
        'ssl_enable_range': (0, 1),  # 0: 关闭, 1: 开启
        'ssl_id_range': [1, 15],  # 参考SSL用户手册
        'connect_id_range': {
            'default': [0, 5],
            'M5310-E/MN316/MN316-S/MN326': [0, 4],
            'MN316A/MN326A/MN319/MN319-A': [0, 3],
            'MR880A': [0, 9]
        },
        'default_values': {
            'connect_id': 0,
            'ssl_enable': 0,
            'ssl_id': 0
        },
        'not_supported': ['M5310-E', 'MN316', 'MN316-S', 'MN326', 'MN316A', 'MN326A', 'MN319', 'MN319-A', 'MR880A', 'ML307H-GU'],
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MIPCFG: "ssl",{connect_id},{ssl_enable},{ssl_id}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mipcfg_ssl

def set_miptka(connect_id=0, keepalive=0, keepidle=90, keepinterval=75, keepcount=3):
    miptka = {
        'command': 'AT+MIPTKA',
        'send_data': f'AT+MIPTKA={connect_id},{keepalive},{keepidle},{keepinterval},{keepcount}',
        'search_data': f'AT+MIPTKA={connect_id}',
        'keepalive_range': (0, 1),  # 0: 关闭, 1: 开启
        'keepidle_range': {
            'default': [30, 7200],
            'MN316/MN316-S/MN326': [30, 7200]  # 默认值30
        },
        'keepinterval_range': {
            'default': [30, 600],
            'MN316/MN316-S/MN326': [30, 600]  # 默认值90
        },
        'keepcount_range': [1, 9],
        'connect_id_range': {
            'default': [0, 5],
            'M5310-E/MN316/MN316-S/MN326': [0, 4],
            'MN316A/MN326A/MN319/MN319-A': [0, 3],
            'MR880A': [0, 9]
        },
        'default_values': {
            'connect_id': 0,
            'keepalive': 0,
            'keepidle': 90,
            'keepinterval': 75,
            'keepcount': 3
        },
        'special_notes': {
            'MN316/MN316-S/MN326': 'keepidle默认值30, keepinterval默认值90',
            'UDP连接': '不可设置心跳参数'
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MIPTKA: {connect_id},{keepalive},{keepidle},{keepinterval},{keepcount}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return miptka

def set_mipopen(connect_id=0, proto_type="TCP", address="120.27.12.119", remote_port=2040, timeout=60, access_mode=0, local_port=0):
    # 预处理输入参数，去除可能已包含的引号
    proto_type = str(proto_type).strip('"\'')  # 去除可能存在的首尾双引号或单引号
    address = str(address).strip('"\'')  # 去除可能存在的首尾双引号或单引号
    
    mipopen = {
        'command': 'AT+MIPOPEN',
        'send_data': f'AT+MIPOPEN={connect_id},"{proto_type}","{address}",{remote_port},{timeout},{access_mode},{local_port}',
        'proto_type': ['TCP', 'UDP'],
        'remote_port_range': [0, 65535],
        'timeout_range': {
            'default': [1, 180],
            'MN316/MN316-S/MN326': [1, 180]  # 参数不生效
        },
        'access_mode_range': (0, 1, 2, 3),  # 0: 普通模式, 1: 透传模式, 2: 流缓存模式, 3: 包缓存模式
        'local_port_range': [0, 65535],
        'connect_id_range': {
            'default': [0, 5],
            'M5310-E/MN316/MN316-S/MN326': [0, 4],
            'MN316A/MN326A/MN319/MN319-A': [0, 3],
            'MR880A': [0, 9]
        },
        'default_values': {
            'connect_id': 0,
            'proto_type': 'TCP',
            'address': '120.27.12.119',
            'remote_port': 2040,
            'timeout': 60,
            'access_mode': 0,
            'local_port': 0
        },
        'not_supported_modes': {
            'M5310-E/MN327/MN328/MN316/MN316-S/MN316A/MN326A/MN318/MN319/MN319-A/MN326': [1],  # 不支持透传模式
        },
        'special_notes': {
            'MN319/MN319-A': '建立TCP连接时，建议使用指令AT+MLPMCFG锁定睡眠',
            'SSL协议': '流缓存模式下需要将当前数据读取完后才能收到后续数据',
            'local_port': '0表示系统自动分配，建议配置5位以上的端口'
        },
        'result': [r'OK', rf'\+MIPOPEN: {connect_id},0', r'CONNECT'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mipopen

def set_mipclose(connect_id=0, mode=0, project=None):
    # 定义不支持mode参数的设备型号列表
    unsupported_models = [
        'MN316', 'MN316-S', 'MN319', 'MN319-A', 'MN326', 'MN327',
        'MN316A', 'MN326A',
        'M5310-E', 'MN318', 'MN328',
        'ML302A', 'ML305A', 'ML307A', 'ML302S', 'ML307S', 'ML305U', 'ML305M', 
        'ML307M', 'ML307R', 'ML307N', 'ML307C', 'ML307X', 'ML307Y', 'ML307B',
        'ML307H',
        'MR880A'
    ]

    # 检查当前项目是否在不支持mode参数的列表中
    mode_not_supported = False
    if project:
        for model in unsupported_models:
            if model in project:
                mode_not_supported = True
                break

    # 根据设备型号决定生成哪种格式的指令
    if mode_not_supported:
        # 不支持mode参数的设备，只生成AT+MIPCLOSE={connect_id}格式
        send_data = f'AT+MIPCLOSE={connect_id}'
        search_data = f'AT+MIPCLOSE={connect_id}'  # 查询也是同一种格式
    else:
        # 支持mode参数的设备，生成AT+MIPCLOSE={connect_id},{mode}格式
        send_data = f'AT+MIPCLOSE={connect_id},{mode}'
        search_data = f'AT+MIPCLOSE={connect_id}'  # 查询仍然是同一种格式

    mipclose = {
        'command': 'AT+MIPCLOSE',
        'send_data': send_data,
        'search_data': search_data,
        'mode_range': {
            'default': [0, 3],
            'ML307G': [0, 3],
            'MN316/MN316-S/MN319/MN319-A/MN326/MN327': [],  # 不支持mode参数
            'MN316A/MN326A': [],  # 不支持mode参数
            'M5310-E/MN318/MN328': [],  # 不支持mode参数
            'ML302A/ML305A/ML307A/ML302S/ML307S/ML305U/ML305M/ML307M/ML307R/ML307N/ML307C/ML307X/ML307Y/ML307B': [],  # 不支持mode参数
            'ML307H': [],  # 不支持mode参数
            'MR880A': []  # 不支持mode参数
        },
        'connect_id_range': {
            'default': [0, 5],
            'M5310-E/MN316/MN316-S/MN326': [0, 4],
            'MN316A/MN326A/MN319/MN319-A': [0, 3],
            'MR880A': [0, 9]
        },
        'default_values': {
            'connect_id': 0,
            'mode': 0
        },
        'special_notes': {
            'mode 0': '等待发送缓存区数据发送完毕后关闭',
            'mode 1': '立即关闭不等待缓存区数据发送完毕',
            'mode 2': '不等待发送缓存区数据发送完毕，等待2MSL后关闭',
            'mode 3': '向服务器发送RST消息重置连接后关闭',
            'mode 4': '等待发送缓存区数据发送完毕后，再等待2MSL后关闭',
            'TCP协议': 'mode参数仅对TCP生效'
        },
        'result': [r'OK', rf'\+MIPCLOSE: {connect_id}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mipclose

def set_mipsend(connect_id=0, send_length=0, data="", rai=0, seq=1, pri_flag=0):
    mipsend = {
        'command': 'AT+MIPSEND',
        'send_data': f'AT+MIPSEND={connect_id},{send_length},"{data}",{rai},{seq},{pri_flag}',
        'send_length_range': {
            'default': [0, 1460],  # 命令直接输入模式
            '数据模式': [1, 8192],
            'ML307H': [1, 16384],  # 首个数据包最大16K
            'ML307N': [1, 2048]  # 受平台单条命令长度限制
        },
        'rai_range': (0, 1, 2),  # 0: 无信息, 1: 发送上行包, 2: 发送上行包并期望下行包
        'seq_range': [1, 255],  # UDP空口回传序列号
        'pri_flag_range': (0, 1, 2, 3),  # 0: 可靠性, 1: 低延时, 2: 吞吐量, 3: 低消耗
        'connect_id_range': {
            'default': [0, 5],
            'M5310-E/MN316/MN316-S/MN326': [0, 4],
            'MN316A/MN326A/MN319/MN319-A': [0, 3],
            'MR880A': [0, 9]
        },
        'default_values': {
            'connect_id': 0,
            'send_length': 0,
            'data': "",
            'rai': 0,
            'seq': 1,
            'pri_flag': 0
        },
        'not_supported': {
            'rai': ['MN316/MN316-S/MN316A/MN326A/MN318/MN326/M5310-E/MN327/MN328/MN319/MN319-A/MR880A/ML302A/ML305A/ML307A/ML307G/ML302S/ML307S/ML305U/ML305M/ML307M/ML307N/ML307R/ML307B/ML307H/ML307C/ML307X/ML307Y'],
            'seq': ['ML302A/ML305A/ML307A/ML307G/ML302S/ML307S/ML305U/ML305M/ML307M/ML307N/ML307R/ML307B/ML307H/ML307C/ML307X/ML307Y/MR880A'],
            'pri_flag': ['ALL']  # 暂不支持
        },
        'special_notes': {
            'MN316系列': '不支持">"数据输入模式，只能在AT命令中直接输入数据',
            'ML305U': '">"数据模式输入数据时，数据长度最大支持4096字节',
            'MN327': '命令直接输入模式下，单条命令最大长度为2048',
            'UDP协议': '单包超过MTU长度时IP层将自动分包',
            'RAI和SEQ': '使用时不支持灌包'
        },
        'result': [r'OK', rf'\+MIPSEND: {connect_id},{send_length}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mipsend

def set_miprd(connect_id=0, read_len=0):
    miprd = {
        'command': 'AT+MIPRD',
        'send_data': f'AT+MIPRD={connect_id},{read_len}',
        'search_data': f'AT+MIPRD={connect_id}',
        'read_len_range': {
            'default': [0, 4096],
            'MN316A/MN326A/MN319/MN319-A': [1, 1460]  # 不支持大包读取
        },
        'connect_id_range': {
            'default': [0, 5],
            'M5310-E/MN316/MN316-S/MN326': [0, 4],
            'MN316A/MN326A/MN319/MN319-A': [0, 3],
            'MR880A': [0, 9]
        },
        'default_values': {
            'connect_id': 0,
            'read_len': 0
        },
        'special_notes': {
            'TCP连接': '流缓存模式，按数据长度读取',
            'UDP连接': '包缓存模式，按数据包个数读取',
            'read_len=0': '读取全部缓存数据'
        },
        'result': [r'OK', rf'\+MIPRD: {connect_id},\d+,\d+,".*"'],
        'search_result': [r'OK', rf'\+MIPRD: {connect_id},\d+'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return miprd

def set_mipmode(connect_id=0, access_mode=0, packet_size=1024, waittm=200):
    mipmode = {
        'command': 'AT+MIPMODE',
        'send_data': f'AT+MIPMODE={connect_id},{access_mode},{packet_size},{waittm}',
        'search_data': f'AT+MIPMODE={connect_id}',
        'access_mode_range': (0, 1, 2, 3),  # 0:普通模式, 1:透传模式, 2:流缓存模式, 3:包缓存模式
        'packet_size_range': {
            'default': [512, 1460],
            'ML302A/ML305A/ML307A/ML307G/ML305U/ML305M/ML307M/ML307N/ML307R/ML307C/ML307X/ML307Y': []  # 不支持配置
        },
        'waittm_range': {
            'default': [0, 2000],
            'ML302A/ML305A/ML307A/ML307G/ML305U/ML305M/ML307M/ML307N/ML307R/ML307C/ML307X/ML307Y': []  # 不支持配置
        },
        'connect_id_range': {
            'default': [0, 5],
            'M5310-E/MN316/MN316-S/MN326': [0, 4],
            'MN316A/MN326A/MN319/MN319-A': [0, 3],
            'MR880A': [0, 9]
        },
        'default_values': {
            'connect_id': 0,
            'access_mode': 0,
            'packet_size': 1024,
            'waittm': 200
        },
        'not_supported': {
            'access_mode=1': ['M5310-E', 'MN316', 'MN316-S', 'MN316A', 'MN326A', 'MN318', 'MN319', 'MN319-A', 'MN326', 'MN327', 'MN328'],
            'packet_size': ['ML302A', 'ML305A', 'ML307A', 'ML302S', 'ML307S', 'ML307G', 'ML305U', 'ML305M', 'ML307M', 'ML307N', 'ML307R', 'ML307C', 'ML307X', 'ML307Y'],
            'waittm': ['ML302A', 'ML305A', 'ML307A', 'ML302S', 'ML307S', 'ML307G', 'ML305U', 'ML305M', 'ML307M', 'ML307N', 'ML307R', 'ML307C', 'ML307X', 'ML307Y']
        },
        'special_notes': {
            '透传模式': 'packet_size和waittm参数仅在透传模式下有效',
            '缓存模式切换': '当连接为缓存模式且接收缓存区中有数据未读取，切换到普通模式时自动读取所有缓存数据',
            '数据模式限制': 'MN316/MN316-S/MN316A/MN326A/MN318/MN319/MN319-A/MN326/M5310-E/MN327/MN328暂不支持透传模式'
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MIPMODE: {connect_id},{access_mode}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mipmode

def set_mipstate(connect_id=0):
    mipstate = {
        'command': 'AT+MIPSTATE',
        'send_data': f'AT+MIPSTATE={connect_id}',
        'search_data': 'AT+MIPSTATE?',
        'connect_id_range': {
            'default': [0, 5],
            'M5310-E/MN316/MN316-S/MN326': [0, 4],
            'MN316A/MN326A/MN319/MN319-A': [0, 3],
            'MR880A': [0, 9]
        },
        'default_values': {
            'connect_id': 0
        },
        'state_values': ['INITIAL', 'CONNECTING', 'CONNECTED', 'CLOSING', 'CLOSED'],
        'result': [r'OK', rf'\+MIPSTATE: {connect_id},".*",".*",\d+,".*"'],
        'search_result': [r'OK', r'\+MIPSTATE: \d+,".*",".*",\d+,".*"'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mipstate

def set_mipsack(connect_id=0):
    mipsack = {
        'command': 'AT+MIPSACK',
        'send_data': f'AT+MIPSACK={connect_id}',
        'connect_id_range': {
            'default': [0, 5],
            'M5310-E/MN316/MN316-S/MN326': [0, 4],
            'MN316A/MN326A/MN319/MN319-A': [0, 3]
        },
        'default_values': {
            'connect_id': 0
        },
        'not_supported': ['MN316/MN316-S/MN326'],
        'special_notes': {
            'UDP连接': '所有发送的数据都计算在nack中，acked固定为0'
        },
        'result': [r'OK', rf'\+MIPSACK: \d+,\d+,\d+,\d+'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mipsack

def set_mdnscfg_ip(address1="119.29.29.29", address2="114.114.114.114"):
    mdnscfg_ip = {
        'command': 'AT+MDNSCFG',
        'send_data': f'AT+MDNSCFG="ip","{address1}","{address2}"',
        'search_data': 'AT+MDNSCFG="ip"',
        'address_type': 'IPv4',
        'default_values': {
            'address1': '119.29.29.29',
            'address2': '114.114.114.114'
        },
        'special_notes': {
            'NB系列': '如SIM卡PLMN是46003、46005、460011，ipv4默认值是218.4.4.4',
            '空字符串': '配置为空字符串""将清空NV并恢复默认配置'
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MDNSCFG: "ip","{address1}","{address2}"'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mdnscfg_ip

def set_mdnscfg_ipv6(address1="2400:3200::1", address2="2001:4860:4860::8888"):
    mdnscfg_ipv6 = {
        'command': 'AT+MDNSCFG',
        'send_data': f'AT+MDNSCFG="ipv6","{address1}","{address2}"',
        'search_data': 'AT+MDNSCFG="ipv6"',
        'address_type': 'IPv6',
        'default_values': {
            'address1': '2400:3200::1',
            'address2': '2001:4860:4860::8888'
        },
        'special_notes': {
            '空字符串': '配置为空字符串""将清空NV并恢复默认配置'
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MDNSCFG: "ipv6","{address1}","{address2}"'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mdnscfg_ipv6

def set_mdnscfg_priority(priority=1):
    mdnscfg_priority = {
        'command': 'AT+MDNSCFG',
        'send_data': f'AT+MDNSCFG="priority",{priority}',
        'search_data': 'AT+MDNSCFG="priority"',
        'priority_range': (0, 1),  # 0: IPv4优先, 1: IPv6优先
        'default_values': {
            'priority': 1
        },
        'not_save_nv': ['ML302A/ML305A/ML307A/ML307G/ML302S/ML307S/ML305U/ML305M/ML307M/ML307N/ML307R/ML307H/ML307C'],
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MDNSCFG: "priority",{priority}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mdnscfg_priority

def set_mdnscfg_cached(cached_mode=0, cached_period=3600):
    mdnscfg_cached = {
        'command': 'AT+MDNSCFG',
        'send_data': f'AT+MDNSCFG="cached",{cached_mode},{cached_period}',
        'search_data': 'AT+MDNSCFG="cached"',
        'cached_mode_range': (0, 1),  # 0: 使用缓存, 1: 不使用缓存
        'cached_period_range': [1, 65553],
        'default_values': {
            'cached_mode': 0,
            'cached_period': 3600
        },
        'not_supported': ['MN316/MN316-S/MN316A/MN326A/MN318/MN319/MN319-A/MN326/M5310-E/MN327/MN328/ML307X/ML307Y/ML307B'],
        'special_notes': {
            'ML307G': '默认值为1',
            'ML307G/ML307H': '暂不支持cached_period缓存周期'
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MDNSCFG: "cached",{cached_mode},{cached_period}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mdnscfg_cached

def set_mdnscfg_timeout(time=10, retries=3):
    mdnscfg_timeout = {
        'command': 'AT+MDNSCFG',
        'send_data': f'AT+MDNSCFG="timeout",{time},{retries}',
        'search_data': 'AT+MDNSCFG="timeout"',
        'time_range': [1, 60],
        'retries_range': [1, 9],
        'default_values': {
            'time': 10,  # 4G、5G模组默认10s
            'retries': 3
        },
        'special_notes': {
            'NB模组': '默认30s',
            'MR880A': '不支持重试请求，设置无效，超时后直接退出'
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MDNSCFG: "timeout",{time},{retries}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mdnscfg_timeout

def set_mdnsgip(domainname="iot.10086.cn", cid=1):
    mdnsgip = {
        'command': 'AT+MDNSGIP',
        'send_data': f'AT+MDNSGIP="{domainname}",{cid}',
        'domainname_max_len': 255,
        'cid_range': {
            'default': [1, 15],
            'MN316/MN316-S/MN316A/MN326A/MN318/MN319/MN319-A/MN326/ML307G/MR880A/ML307H/M5310-E/MN327/MN328': []  # 不支持cid参数
        },
        'default_values': {
            'domainname': 'iot.10086.cn',
            'cid': 1
        },
        'special_notes': {
            '4G系列': '默认为1',
            'ML307B': '默认不指定'
        },
        'result': [r'OK', rf'\+MDNSGIP: "{domainname}",".*"'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mdnsgip

def set_mping(host="ipv6.sjtu.edu.cn", timeout=10, ping_num=4, packet_len=16, cid=1):
    mping = {
        'command': 'AT+MPING',
        'send_data': f'AT+MPING="{host}",{timeout},{ping_num},{packet_len},{cid}',
        'host_max_len': 255,
        'timeout_range': [1, 60],
        'ping_num_range': [1, 65535],
        'packet_len_range': [1, 1400],
        'cid_range': {
            'default': [1, 15],
            'M5310-E/MN316/MN316-S/MN316A/MN326A/MN319/MN319-A/MN326/ML307H/MR880A': []  # 不支持cid参数
        },
        'default_values': {
            'host': 'ipv6.sjtu.edu.cn',
            'timeout': 10,
            'ping_num': 4,
            'packet_len': 16,
            'cid': 1
        },
        'special_notes': {
            'MN327': 'cid范围1~7',
            '4G系列': '默认为1',
            'ML307B': '默认不指定'
        },
        'result': [r'OK', r'\+MPING: \d+,".*",\d+,\d+,\d+', r'\+MPING: "statistics",\d+,\d+,\d+,\d+,\d+'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mping

def set_mntp(server="ntp1.aliyun.com", port=123, sync=1, timeout=20):
    mntp = {
        'command': 'AT+MNTP',
        'send_data': f'AT+MNTP="{server}",{port},{sync},{timeout}',
        'server_max_len': 255,
        'port_range': [0, 65535],
        'sync_range': (0, 1),  # 0: 不更新, 1: 更新
        'timeout_range': [1, 300],
        'default_values': {
            'server': 'ntp1.aliyun.com',
            'port': 123,
            'sync': 1,
            'timeout': 20
        },
        'special_notes': {
            'ML307X/ML307Y': '默认服务器"ntp7.aliyun.com"',
            'ML302A系列': '默认值30s',
            'ML307N': '仅支持0、3结果码'
        },
        'result': [r'OK', rf'\+MNTP: \d+,".*"'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mntp

def set_exit_transparent_mode():
    exit_transparent = {
        'command': '+++',
        'send_data': '+++',
        'not_supported': ['MN316/MN316-S/MN316A/MN326A/MN318/MN319/MN319-A/MN326/M5310-E/MN327/MN328'],
        'special_notes': {
            'ML307X/ML307Y': '执行+++请与数据发送保持1秒的间隔'
        },
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return exit_transparent