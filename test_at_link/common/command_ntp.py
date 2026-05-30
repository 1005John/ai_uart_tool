import re



def set_mntp(server=None, port=None, sync=None, timeout=None):
    """
    AT+MNTP - 网络时间同步
    从手册第64-65页提取
    """
    import math
    import pandas as pd

    # 检查参数是否为 NaN、None 或空字符串
    def is_empty(value):
        if value is None:
            return True
        if isinstance(value, str) and value == "":
            return True
        if isinstance(value, float) and pd.isna(value):
            return True
        if value == "nan":
            return True
        return False

    # 如果所有参数都是空值，发送基本命令
    if is_empty(server) and is_empty(port) and is_empty(sync) and is_empty(timeout):
        send_data = 'AT+MNTP'
    else:
        # 构建参数列表，保留中间的空值
        params = []

        # 添加所有参数，如果是空值则用空字符串表示
        params.append('' if is_empty(server) else str(server))
        params.append('' if is_empty(port) else str(
            int(float(port)) if isinstance(port, (float, str)) and not is_empty(port) and port != '' else port))
        params.append('' if is_empty(sync) else str(
            int(float(sync)) if isinstance(sync, (float, str)) and not is_empty(sync) and sync != '' else sync))
        params.append('' if is_empty(timeout) else str(
            int(float(timeout)) if isinstance(timeout, (float, str)) and not is_empty(
                timeout) and timeout != '' else timeout))

        # 去除末尾的连续空参数（但保留中间的空参数）
        while len(params) > 0 and params[-1] == '':
            params.pop()

        send_data = f'AT+MNTP={",".join(params)}'

    mntp = {
        'command': 'AT+MNTP',
        'send_data': send_data,
        'search_data': 'AT+MNTP=?',
        'search_result': [
            r'\+MNTP: \(list of supported <port>\), \(list of supported <sync>\), \(list of supported <timeout>s\)',
            'OK'],
        'server_type': ['NTP服务器IP地址', '域名'],
        'server_max_length': [1 - 255],
        'port_range': [0 - 65535],
        'sync_range': (0, 1),
        'timeout_range': [1 - 300],
        'default_values': {
            'server': 'ntp1.aliyun.com',
            'port': 123,
            'sync': 1,
            'timeout': 20
        },
        'parameter_order': ['server', 'port', 'sync', 'timeout'],
        'parameter_optional': {
            'server': True,  # 可缺省，使用默认服务器
            'port': True,  # 可缺省，使用默认值123
            'sync': True,  # 可缺省，使用默认值1
            'timeout': True  # 可缺省，使用默认值20
        },
        'model_specific_defaults': {
            'server_default': {
                'default': 'ntp1.aliyun.com',
                'ML307X/ML307Y': 'ntp7.aliyun.com'
            },
            'timeout_default': {
                'default': 20,
                'ML302A/ML305A/ML307A/ML307G/ML302S/ML307S/ML307R/ML307H/ML307C': 30
            }
        },
        'result_codes': {
            '0': '成功',
            '1': 'DNS错误',
            '2': '超时',
            '3': '时间同步失败'
        },
        'time_format': '格式为"yy/MM/dd,hh:mm:ss ±zz"，其中zz代表时区的4倍',
        'result': [
            r'OK',
            r'\+MNTP: 0,\"\d{2}/\d{1,2}/\d{1,2},\d{2}:\d{2}:\d{2}[+-]\d+\"'
        ],
        'err_result': [r'\+CME ERROR:?\s*\d+'],
        'special_notes': {
            '时区格式': '获取到的时区为1/4制式时区',
            '时间同步': 'sync=1时更新本地RTC计时器的时间',
            '命令格式': '所有参数均可缺省，按顺序传递'
        },
        'example_commands': {
            '仅指定服务器': 'AT+MNTP="cn.ntp.org.cn"',
            '指定服务器和端口': 'AT+MNTP="cn.ntp.org.cn",123',
            '指定服务器、端口和同步': 'AT+MNTP="cn.ntp.org.cn",123,1',
            '指定全部参数': 'AT+MNTP="cn.ntp.org.cn",123,1,30',
            '使用默认服务器': 'AT+MNTP=""  # 使用默认服务器ntp1.aliyun.com'
        }
    }
    return mntp



