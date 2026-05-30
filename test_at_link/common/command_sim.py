import re


def set_cpin(pin="", newpin=""):
    """
    AT+CPIN PIN authentication
    Set command sends to the MT a password which is necessary before it can be operated
    """
    if pin and newpin:
        send_data = f'AT+CPIN={pin},{newpin}'
    elif pin:
        send_data = f'AT+CPIN={pin}'
    else:
        send_data = 'AT+CPIN'

    cpin = {
        'command': 'AT+CPIN',
        'send_data': send_data,
        'search_data': 'AT+CPIN?',
        'pin_max_len': {
            'default': [1, 8]  # PIN码通常为4-8位，最小长度为1
        },
        'newpin_max_len': {
            'default': [1, 8]  # 新PIN码通常为4-8位，最小长度为1
        },
        'code_values': ['READY', 'SIM PIN', 'SIM PUK', 'SIM PIN2', 'SIM PUK2'],
        'default_values': {
            'pin': "",
            'newpin': ""
        },
        'special_notes': {
            'MR880A': '仅支持AT+CPIN, AT+CPWD, AT+CSIM, AT+CRSM, AT+CIMI, AT+CCHO, AT+CCHC, AT+CGLA命令',
            'general': '输入三次错误PIN码后SIM卡将被锁定'
        },
        'result': [r'OK'],
        'search_result': [r'OK', r'\+CPIN: (READY|SIM PIN|SIM PUK|SIM PIN2|SIM PUK2)'],
        'err_result': [r'\+CME ERROR: \d+']
    }
    return cpin


def set_cpwd(fac="SC", oldpwd="", newpwd=""):
    """
    AT+CPWD Change password
    This command is used to change password [PIN/PIN2]
    """
    cpwd = {
        'command': 'AT+CPWD',
        'send_data': f'AT+CPWD={fac},{oldpwd},{newpwd}',
        'search_data': 'AT+CPWD=?',
        'fac_values': {
            'default': ['SC', 'P2'],
            'ML307X/ML307Y': ['SC']  # 仅支持"SC"
        },
        'pwdlength_range': {
            'default': [1, 8]  # 密码长度通常为4-8位，最小长度为1
        },
        'fac_type': ['SIM PIN', 'SIM PIN2'],
        'default_values': {
            'fac': 'SC',
            'oldpwd': "",
            'newpwd': ""
        },
        'response_time': {
            'MN316/MN316A/MN326A/MN326': '不超过10s',
            'MN327': '不超过20s'
        },
        'special_notes': {
            'general': '执行此命令需要一些时间返回ok或error，在此期间其他AT命令输入可能会返回错误或等待'
        },
        'result': [r'OK'],
        'search_result': [r'OK', r'\+CPWD: \((SC|P2),\d+\)'],
        'err_result': [r'\+CME ERROR: \d+']
    }
    return cpwd


def set_csim(length=0, command=""):
    """
    AT+CSIM Generic SIM access
    This command allows a direct control of the SIM
    """
    csim = {
        'command': 'AT+CSIM',
        'send_data': f'AT+CSIM={length},{command}',
        'search_data': 'AT+CSIM=?',
        'length_range': {
            'default': [0, 510],  # 基于手册中的范围说明
            'MN319/MN319-A': [0, 255]
        },
        'command_type': 'hex格式的3GPP 102.221 SIM命令',
        'response_type': 'hex格式的SIM响应',
        'default_values': {
            'length': 0,
            'command': ""
        },
        'special_notes': {
            'ML302S/ML307S': '不支持此命令',
            'MN316/MN316A/MN326A/MN326': '确保在文件读取命令执行前基本文件不被更改，卡断电不会在用户发送命令后15秒内发生',
            'general': '如果使用AT+CSIM命令打开逻辑通道，操作后应运行AT+CSIM/AT+CCHC命令关闭逻辑通道'
        },
        'result': [r'OK', rf'\+CSIM: {length},{command}'],
        'search_result': [r'OK'],
        'err_result': [r'\+CME ERROR: \d+']
    }
    return csim


def set_crsm(command=176, fileid="", P1=0, P2=0, P3=0, data="", pathid=""):
    """
    AT+CRSM Restricted SIM access
    This command supports limited access to SIM database
    """
    params = [str(command)]
    if fileid:
        params.append(str(fileid))
    if P1 is not None and P2 is not None and P3 is not None:
        params.extend([str(P1), str(P2), str(P3)])
        if data:
            params.append(data)
            if pathid:
                params.append(pathid)

    send_data = f'AT+CRSM={",".join(params)}'

    crsm = {
        'command': 'AT+CRSM',
        'send_data': send_data,
        'search_data': 'AT+CRSM=?',
        'command_values': {
            'default': [176, 178, 192, 214, 220, 242],
            'ML302S/ML307S/ML302A/ML305A/ML307A/ML307R/ML307B/ML307C/ML305U/ML307G/ML307H': [176, 178, 192, 214, 220],
            'ML305M/ML307M/ML307N/ML551Z': [176, 178, 192, 214, 220],
            'MF308C/MF572E/MR380M': [176, 178, 192, 214, 220],
            'MN327': [176, 178, 192, 214, 220]
        },
        'command_descriptions': {
            176: 'READ BINARY',
            178: 'READ RECORD',
            192: 'GET RESPONSE',
            214: 'UPDATE BINARY',
            220: 'UPDATE RECORD',
            242: 'STATUS'
        },
        'fileid_type': ['整数类型(SIM)', '字符串类型(USIM)'],
        'pathid_support': {
            'default': True,
            'MN327': False
        },
        'default_values': {
            'command': 176,
            'fileid': "",
            'P1': 0,
            'P2': 0,
            'P3': 0,
            'data': "",
            'pathid': ""
        },
        'special_notes': {
            'MR880A': '不支持测试命令',
            'general': 'STATUS和GET RESPONSE以外的命令需要fileid参数'
        },
        'result': [r'OK', r'\+CRSM: \d+,\d+(,[0-9A-Fa-f]*)?'],
        'search_result': [r'OK'],
        'err_result': [r'\+CME ERROR: \d+']
    }
    return crsm


def set_cnum():
    """
    AT+CNUM Subscriber number
    This command returns the MSISDNs related to the subscriber
    """
    cnum = {
        'command': 'AT+CNUM',
        'send_data': 'AT+CNUM',
        'search_data': 'AT+CNUM=?',
        'speed_values': [0, 1, 2, 3, 4, 5, 6, 7, 12, 14, 15, 16, 17, 34, 36, 38, 39, 43, 47, 48, 49, 50, 51, 65, 66, 68,
                         70, 71, 75, 79, 80, 81, 82, 83, 84, 115, 116, 120, 121, 130, 131, 132, 133, 134],
        'service_values': [0, 1, 2, 3, 4, 5],
        'itc_values': [0, 1],
        'service_descriptions': {
            0: 'asynchronous modem',
            1: 'synchronous modem',
            2: 'PAD Access (asynchronous)',
            3: 'Packet Access (synchronous)',
            4: 'voice',
            5: 'fax'
        },
        'itc_descriptions': {
            0: '3.1 kHz',
            1: 'UDI'
        },
        'special_notes': {
            'ML302A-DCLM/ML302A-GCLM/ML307A-DCLN/ML307A-GCLN/ML307A-DL/ML307R/ML307B/ML307C/ML305A-DC/ML305A-DL/ML305M/ML307M/ML307N/ML307G/ML307H/ML307X/ML307Y': '不支持此命令',
            'MR880A/MR380M': '不支持此命令',
            'ML551Z/MF572E': '如果SIM卡的EF MSISDN文件未预设号码，则无法读取'
        },
        'result': [r'OK', r'\+CNUM: (".*",)?".*",\d+(,\d+(,\d+)?)?'],
        'search_result': [r'OK'],
        'err_result': [r'\+CME ERROR: \d+']
    }
    return cnum


def set_cimi():
    """
    AT+CIMI Request international mobile subscriber identity
    This command is used to request international mobile subscriber identity
    """
    cimi = {
        'command': 'AT+CIMI',
        'send_data': 'AT+CIMI',
        'imsi_format': '国际移动用户识别码(无引号的字符串)',
        'default_values': {},
        'special_notes': {
            'ML551Z': '指示格式为+CIMI: <IMSI>',
            'ML302A/ML305A/ML307A': '如果查询失败，可通过运行AT+CPBW=1,"138000000XX"等命令将号码写入SIM卡'
        },
        'result': [r'OK', r'(\+CIMI: )?\d+'],
        'search_result': [],
        'err_result': [r'\+CME ERROR: \d+']
    }
    return cimi


def set_ccho(dfname=""):
    """
    AT+CCHO Open UICC logical channel
    This command is used to open UICC logical channel
    """
    ccho = {
        'command': 'AT+CCHO',
        'send_data': f'AT+CCHO={dfname}' if dfname else 'AT+CCHO',
        'dfname_type': '十六进制字符串格式(1-16字节)',
        'sessionid_range': {
            'default': [1, 19],
            'MN319/MN319-A': [1, 3],
            'ML305M/ML307M/ML307N/ML307X/ML307Y': [1, 19]
        },
        'default_values': {
            'dfname': ""
        },
        'special_notes': {
            'ML302S/ML307S': '不支持此命令'
        },
        'result': [r'OK', r'\d+'],
        'search_result': [],
        'err_result': [r'\+CME ERROR: \d+']
    }
    return ccho


def set_cchc(sessionid=1):
    """
    AT+CCHC Close UICC logical channel
    This command is used to close UICC logical channel
    """
    cchc = {
        'command': 'AT+CCHC',
        'send_data': f'AT+CCHC={sessionid}',
        'sessionid_range': {
            'default': [1, 19],
            'MN319/MN319-A': [1, 3],
            'ML305M/ML307M/ML307N/ML307X/ML307Y': [1, 19]
        },
        'default_values': {
            'sessionid': 1
        },
        'special_notes': {
            'ML302S/ML307S': '不支持此命令',
            'MF572E': '执行命令仅返回OK'
        },
        'result': [r'OK', r'\+CCHC'] if sessionid == 1 else [r'OK'],
        'search_result': [],
        'err_result': [r'\+CME ERROR: \d+']
    }
    return cchc


def set_cgla(sessionid=1, length=0, command=""):
    """
    AT+CGLA Generic UICC logical channel access
    This command is used to access generic UICC logical channel
    """
    cgla = {
        'command': 'AT+CGLA',
        'send_data': f'AT+CGLA={sessionid},{length},{command}',
        'sessionid_range': {
            'default': [1, 19],
            'ML307X/ML307Y': '不能是默认通道号0'
        },
        'length_range': {
            'default': [0, 510],
            'MN319/MN319-A': [0, 255]
        },
        'command_type': '十六进制格式的APDU命令',
        'response_type': '十六进制格式的UICC响应',
        'default_values': {
            'sessionid': 1,
            'length': 0,
            'command': ""
        },
        'special_notes': {
            'ML302S/ML307S': '不支持此命令',
            'ML307X/ML307Y': '通道号由+CCHO打开，不能是默认通道号0'
        },
        'result': [r'OK', rf'\+CGLA: {length},{command}'],
        'search_result': [],
        'err_result': [r'\+CME ERROR: \d+']
    }
    return cgla