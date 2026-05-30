import re


def set_mping(host="", timeout="", ping_num="", packet_len="", cid=""):
    """
    AT+MPING PING服务器
    AT+MPING=<host>[,<timeout>[,<ping_num>[,<packet_len>[,<cid>]]]]
    """
    # host 参数必须存在
    params = [f'{host}']

    # 按顺序检查可选参数，如果为空则不包含
    if cid != "":
        params.extend([
            str(timeout) if timeout != "" else "",
            str(ping_num) if ping_num != "" else "",
            str(packet_len) if packet_len != "" else "",
            str(cid)
        ])
    elif packet_len != "":
        params.extend([
            str(timeout) if timeout != "" else "",
            str(ping_num) if ping_num != "" else "",
            str(packet_len)
        ])
    elif ping_num != "":
        params.extend([
            str(timeout) if timeout != "" else "",
            str(ping_num)
        ])
    elif timeout != "":
        params.append(str(timeout))

    send_data = f'AT+MPING={",".join(params)}'

    mpng = {
        'command': 'AT+MPING',
        'send_data': send_data,
        'search_data': 'AT+MPING=?',
        'search_result': [
            r'\+MPING: \(1-60\),\(1-65535\),\(1-1400\),\(list of supported cids\)',
            r'\+MPING: \(1-60\),\(1-65535\),\(1-1400\)',
            r'\+MPING: \(1-60\),\(1-65535\)',
            r'\+MPING: \(1-60\)'
        ],
        'host_desc': '服务器地址，支持域名或IP，最大长度255字节',
        'timeout_range': (1, 60),
        'timeout_default': 10,
        'ping_num_range': (1, 65535),
        'ping_num_default': 4,
        'packet_len_range': (1, 1400),
        'packet_len_default': 16,
        'cid_desc': 'PDP上下文索引号，与AT+CGDCONT范围一致',
        'result_urc': [
            r'\+MPING: \d+,"[^"]+",\d+,\d+,\d+',
            r'\+MPING: "statistics",\d+,\d+,\d+,\d+,\d+'
        ],
        'result_codes': {
            0: '成功',
            1: 'DNS解析失败',
            2: 'DNS解析超时',
            3: '响应错误',
            4: '响应超时',
            'other': '其他错误'
        },
        'not_supported_models': [],  # 手册未明确列出不支持型号
        'notes': [
            '依赖AT+MDNSCFG中的优先级设置，影响IPv4/IPv6地址解析',
            '部分模组（如MR880A、MN系列）对参数支持可能有限'
        ],
        'default_values': {
            'host': "",
            'timeout': 10,
            'ping_num': 4,
            'packet_len': 16,
            'cid': ""
        },
        'result': [r'OK', r'\+MPING:'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mpng