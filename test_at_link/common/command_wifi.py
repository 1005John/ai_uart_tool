def set_mwifiscancfg_hidden(hd_enable=0):
    """
    配置WiFi-SCAN隐藏网络设置
    """
    mwifiscancfg_hidden = {
        'command': 'AT+MWIFISCANCFG',
        'send_data': f'AT+MWIFISCANCFG="hidden",{hd_enable}',
        'search_data': 'AT+MWIFISCANCFG="hidden"',
        'hd_enable_range': (0, 1),
        'hd_enable_description': {
            '0': '不启用',
            '1': '启用'
        },
        'not_supported_models': ['ML302A', 'ML305A', 'ML307A', 'ML307R', 'ML307Y', 'ML307H', 'ML307N'],
        'default_values': {
            'hd_enable': 0
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MWIFISCANCFG: "hidden",{hd_enable}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mwifiscancfg_hidden


def set_mwifiscancfg_priority(priority=0):
    """
    配置WiFi-SCAN优先级设置
    """
    mwifiscancfg_priority = {
        'command': 'AT+MWIFISCANCFG',
        'send_data': f'AT+MWIFISCANCFG="priority",{priority}',
        'search_data': 'AT+MWIFISCANCFG="priority"',
        'priority_range': (0, 1),
        'priority_description': {
            '0': 'LTE优先',
            '1': 'WIFI优先'
        },
        'not_supported_models': ['ML307H', 'ML307N'],
        'default_values': {
            'priority': 0
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MWIFISCANCFG: "priority",{priority}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mwifiscancfg_priority


def set_mwifiscancfg_max(max=5):
    """
    配置WiFi-SCAN最大扫描数量设置
    """
    max_count_range = {
        'default': [4, 10],
        'ML307N': [1, 10]
    }

    mwifiscancfg_max = {
        'command': 'AT+MWIFISCANCFG',
        'send_data': f'AT+MWIFISCANCFG="max",{max}',
        'search_data': 'AT+MWIFISCANCFG="max"',
        'maxCount_range': max_count_range,
        'default_values': {
            'max': 5
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MWIFISCANCFG: "max",{max}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mwifiscancfg_max


def set_mwifiscanstart(round="", timeout="", ssid="", channel=""):
    """
    启动WiFi-SCAN扫描
    """
    # 构建参数列表
    params = []

    # 总是添加round参数，如果是空字符串则作为占位符
    params.append(str(round) if round != "" else "")

    # 总是添加timeout参数，如果是空字符串则作为占位符
    params.append(str(timeout) if timeout != "" else "")
    # 添加可选的ssid和channel参数
    if ssid:
        params.append(f'"{ssid}"')
    if channel:
        params.append(str(channel))

    # 检查params中是否只有空字符串（或者除了空字符串没有其他有效参数）
    non_empty_params = [param for param in params if param != ""]

    if not non_empty_params:
        # 如果没有非空参数，只发送基本命令
        send_data = 'AT+MWIFISCANSTART'
    else:
        # 否则构建完整命令
        send_data = f'AT+MWIFISCANSTART={",".join(params)}'

    # 构建URC响应正则表达式
    urc_pattern = r'\+MWIFISCANINFO: \d+(?:,"[^"]*",".*?",".*?",-?\d+,\d+,)?'

    mwifiscanstart = {
        'command': 'AT+MWIFISCANSTART',
        'send_data': send_data,
        'round_range': {
            'default': [1, 3],
            'ML307N': '该参数无实际意义，配置不生效'
        },
        'timeout_range': {
            'default': [10, 60],
            'ML302A/ML305A/ML307A/ML307R/ML307Y': [10, 60],
            'ML307N': [2, 255]
        },
        'timeout_default': {
            'default': 25,
            'ML307N': 2
        },
        'ssid_support': {
            'not_supported': ['ML302A', 'ML305A', 'ML307A', 'ML307R', 'ML307H', 'ML307N', 'ML307Y']
        },
        'channel_support': {
            'not_supported': ['ML302A', 'ML305A', 'ML307A', 'ML307R', 'ML307Y'],
            'supported_range': {
                'ML307N': [1, 13, 255]
            }
        },
        'special_notes': {
            'ML302A/ML305A/ML307A/ML307R/ML307N': '建议在IDLE态下执行WiFi-SCAN扫描操作',
            'ML307H/ML307Y': '不支持在连接态进行扫描，建议仅在IDLE态下执行WiFi-SCAN扫描操作'
        },
        'default_values': {
            'round': 3,
            'timeout': 60,
            'ssid': "",
            'channel': ""
        },
        'result': [r'OK', urc_pattern, r'\+MWIFISCANINFO: 0'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mwifiscanstart


def set_mwifiscanstop():
    """
    中断WiFi-SCAN流程
    """
    mwifiscanstop = {
        'command': 'AT+MWIFISCANSTOP',
        'send_data': 'AT+MWIFISCANSTOP',
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mwifiscanstop


def set_mwifiscanquery(sort=None):
    """
    查询最近一次WiFi-SCAN历史结果
    """
    if sort is None:
        send_data = 'AT+MWIFISCANQUERY'
    else:
        send_data = f'AT+MWIFISCANQUERY={sort}'
    mwifiscanquery = {
        'command': 'AT+MWIFISCANQUERY',
        'send_data': send_data,
        'search_data': 'AT+MWIFISCANQUERY',
        'sort_range': (0, 1),
        'sort_description': {
            '0': '不排序',
            '1': '按rssi由高到低排序'
        },
        'sort_support': {
            'ML302A/ML305A/ML307A/ML307R/ML307N': '仅支持由高到低排序'
        },
        'default_values': {
            'sort': 0
        },
        'result': [r'\+MWIFISCANQUERY: \d+(?:\n\d+,"[^"]*",".*?",".*?",-?\d+,\d+,)*', r'OK'],
        'search_result': [r'\+MWIFISCANQUERY: \d+(?:\n\d+,"[^"]*",".*?",".*?",-?\d+,\d+,)*', r'OK'],
        'err_result': [r'ERROR']
    }
    return mwifiscanquery