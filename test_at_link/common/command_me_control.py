def set_cpas():
    """
    AT+CPAS Mobile equipment activity status
    查询移动设备活动状态
    """
    cpas = {
        'command': 'AT+CPAS',
        'send_data': 'AT+CPAS',
        'search_data': 'AT+CPAS=?',
        'pas_range': {
            'default': [0, 6],
            'ML302S/ML307S': [0, 2, 4, 5],  # 不支持参数1,5,6
            'ML307G/ML307H': [0, 1, 2, 5],  # 不支持参数3,4,6
            'MF308C': [0, 1, 2, 4, 5],  # 不支持参数3,6
            'ML305U/ML305M/ML307M/ML307N/ML551Z/ML307X/ML307Y/ML307B': [],  # 不支持该命令
            'MR880A/MR380M': []  # 不支持该命令
        },
        'pas_meanings': {
            0: 'ready (MT allows commands from TA/TE)',
            1: 'unavailable (MT does not allow commands from TA/TE)',
            2: 'unknown (MT is not guaranteed to respond to instructions)',
            3: 'ringing (MT is ready for commands from TA/TE, but the ringer is active)',
            4: 'call in progress (MT is ready for commands from TA/TE, but a call is in progress)',
            5: 'asleep (MT is unable to process commands from TA/TE because it is in a low functionality state)',
            6: 'call in active'
        },
        'result': [r'OK', r'\+CPAS: \d+'],
        'search_result': [r'OK', r'\+CPAS: \([\d,]+\)'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+'],
        'special_notes': {
            'ML302S/ML307S': '不支持参数1,5,6',
            'ML307G/ML307H': '不支持参数3,4,6',
            'MF308C': '参数4表示数据服务已激活，不支持语音服务，因此不支持参数3和6',
            'ML305U/ML305M/ML307M/ML307N/ML551Z/ML307X/ML307Y/ML307B': '不支持该命令',
            'MR880A/MR380M': '不支持该命令'
        }
    }
    return cpas


def set_cfun(fun=1, rst=0):
    """
    AT+CFUN Set phone functionality
    设置电话功能级别
    """
    cfun = {
        'command': 'AT+CFUN',
        'send_data': f'AT+CFUN={fun},{rst}',
        'search_data': 'AT+CFUN=?',
        'read_data': 'AT+CFUN?',
        'fun_range': {
            'default': [0, 1, 3, 4, 5],
            'MN316/MN316A/MN326A/M5310-E/MN328/MN318/MN326/MN319/MN319-A': [0, 1],
            'ML302S/ML307S/ML305U': [0, 1, 4],
            'ML307B': [0, 1],
            'MR880A/MF572E/MF380C/MR380R': [0, 1, 4],
            'MR380M': [0, 1]
        },
        'rst_range': {
            'default': [0, 1],
            'MN316/MN316A/MN326A/M5310-E/MN328/MN318/MN326': [0],  # 不支持rst参数
            'ML305U': [0],  # 不支持rst参数
            'ML551Z': {'fun=0': [], 'fun=1': [0, 1]},  # fun=0时rst无效
            'ML307X/ML307Y': [0],  # 不支持参数1
            'MR880A': [0],  # 不支持rst参数
            'MR380M': []  # 不支持rst参数
        },
        'fun_meanings': {
            0: 'Minimum functionality',
            1: 'Full functionality',
            3: 'Disable phone receive RF circuits',
            4: 'Disable phone both transmit and receive RF circuits',
            5: 'Disable SIM'
        },
        'rst_meanings': {
            0: 'Do not reset the MT before setting it to <fun> power level (default value)',
            1: 'Reset the MT before setting it to <fun> power level'
        },
        'default_values': {
            'fun': 1,
            'rst': 0
        },
        'result': [r'OK'],
        'search_result': [r'OK', r'\+CFUN: \([0-9,]+\)'],
        'read_result': [r'OK', r'\+CFUN: {fun}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+'],
        'timeout_notes': {
            'M5310-E': 'AT+CFUN=1超时5s，AT+CFUN=1超时15s',
            'MN316/MN316A/MN326A/MN326': 'AT+CFUN=0或AT+CFUN=1超时10s',
            'MN327': 'AT+CFUN=0或AT+CFUN=1超时2min',
            'MN319/MN319-A': 'AT+CFUN=0超时90s',
            'MN318/MN328': 'AT+CFUN=1超时5s，AT+CFUN=1超时15s'
        },
        'special_notes': {
            'MN316/MN318/MN328/M5310-E': '设置为0时，AT+CGDCONT设置的PDP配置会自动删除',
            'MN319/MN319-A': 'CFUN为0时执行AT+CFUN=1，模块会重启，未保存到Flash的AT命令配置会丢失'
        }
    }
    return cfun


def set_csq():
    """
    AT+CSQ Signal quality
    查询信号质量
    """
    csq = {
        'command': 'AT+CSQ',
        'send_data': 'AT+CSQ',
        'search_data': 'AT+CSQ=?',
        'rssi_range': [0, 31, 99],
        'ber_range': [0, 7, 99],
        'rssi_meanings': {
            0: '-113 dBm or less',
            1: '-111 dBm',
            '2-30': '-109 to -53 dBm',
            31: '-51 dBm or greater',
            99: 'Not known or not detectable'
        },
        'ber_meanings': {
            '0-7': 'As RXQUAL values in the table in GSM 05.08 sub clause 8.2.4',
            99: 'Not known or not detectable'
        },
        'result': [r'OK', r'\+CSQ: \d+,\d+'],
        'search_result': [r'OK', r'\+CSQ: \([0-9,]+\)'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+'],
        'special_notes': {
            'M5310-E/MN328/MN319/MN319-A/MN318': '<ber>当前未实现，始终为99',
            'ML307G/ML307H': '<ber>始终为99',
            'MR380M': '<ber>始终为99',
            'MR880A/MR380M': '仅支持查询当前LTE服务小区的信号强度和信道错误率',
            'ML551Z': '请使用AT+MCSQ命令'
        },
        'valid_modes': ['GU模式']
    }
    return csq


def set_cesq():
    """
    AT+CESQ Extended signal quality
    查询扩展信号质量
    """
    cesq = {
        'command': 'AT+CESQ',
        'send_data': 'AT+CESQ',
        'search_data': 'AT+CESQ=?',
        'rxlev_range': [0, 63, 99],
        'ber_range': [0, 7, 99],
        'rscp_range': [0, 96, 255],
        'ecno_range': [0, 49, 255],
        'rsrq_range': [0, 34, 255],
        'rsrp_range': [0, 97, 255],
        'ss_rsrq_range': [0, 126, 255],
        'ss_rsrp_range': [0, 126, 255],
        'ss_sinr_range': [0, 126, 255],
        'default_values': {
            'rxlev': 99,
            'ber': 99,
            'rscp': 255,
            'ecno': 255,
            'rsrq': 255,
            'rsrp': 255,
            'ss_rsrq': 255,
            'ss_rsrp': 255,
            'ss_sinr': 255
        },
        'result': [r'OK', r'\+CESQ: \d+,\d+,\d+,\d+,\d+,\d+,\d+,\d+,\d+'],
        'search_result': [r'OK', r'\+CESQ: \([0-9,]+\)'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+'],
        'special_notes': {
            'ML307X/ML307Y/ML307B': '仅支持参数255',
            'MR880A': '不支持该命令',
            'MR380R/MR380M': '支持ss_sinr范围0-127'
        }
    }
    return cesq


def set_cclk(time=""):
    """
    AT+CCLK Real time clock
    实时时钟设置和查询
    """
    cclk = {
        'command': 'AT+CCLK',
        'send_data': f'AT+CCLK="{time}"' if time else 'AT+CCLK?',
        'search_data': 'AT+CCLK=?' if time else '',
        'read_data': 'AT+CCLK?',
        'time_format': 'yy/mm/dd,hh:mm:ss+zz',
        'time_zone_range': {
            'default': [-96, 96],
            'MN316/MN316A/MN326A/MN326': [-48, 48],
            'ML307X/ML307Y': [-48, 56],
            'MR880A/MR380R': [-48, 48]
        },
        'year_range': [1970, 2069],
        'special_year_ranges': {
            'ML302A/ML305A/ML307R/ML307B/ML307C/ML307A/ML307G/ML307H': [1970, 2037]
        },
        'default_values': {
            'time': ""
        },
        'result': [r'OK', r'\+CCLK: "[0-9/,:+\-]+"'],
        'search_result': [r'OK'] if time else [],
        'read_result': [r'OK', r'\+CCLK: "[0-9/,:+\-]+"'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+'],
        'special_notes': {
            'MN316/MN316A/MN326A/MN326': '成功连接到网络前或未执行配置命令，查询命令返回ERROR',
            'MN327': '连接到网络或重启会将时间保存到flash',
            'ML302S/ML307S': 'AT+CCLK设置的是GMT时间，时区不为0时需要AT+CTZU=3更新为对应时区的本地时间',
            'ML302A/ML305A/ML307R/ML307B/ML307C/ML307A/ML307G/ML307H': '时区不支持-01/+01',
            'MR380M': '不支持该命令',
            'MF572E': '时间格式yy/mm/dd,hh:mm:ss0zz等同于yy/mm/dd,hh:mm:ss+zz'
        }
    }
    return cclk


def set_clac():
    """
    AT+CLAC List all available AT commands
    列出所有可用的AT命令
    """
    clac = {
        'command': 'AT+CLAC',
        'send_data': 'AT+CLAC',
        'search_data': 'AT+CLAC=?',
        'result': [r'OK'],
        'search_result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+'],
        'special_notes': {
            'ML302A/ML302S/ML305A/ML307A/ML307R/ML307B/ML307C/ML307S/ML305U/ML305M/ML307M/ML307N/ML551Z/ML307X/ML307Y': '不支持该命令',
            'MF572E': '不支持测试命令',
            'MF308C/MR880A/MR380R/MR380M': '不支持该命令'
        }
    }
    return clac


def set_ctzu(mode=0):
    """
    AT+CTZU Automatic time zone update
    自动时区更新设置
    """
    ctzu = {
        'command': 'AT+CTZU',
        'send_data': f'AT+CTZU={mode}',
        'search_data': 'AT+CTZU=?',
        'read_data': 'AT+CTZU?',
        'mode_range': {
            'default': [0, 1, 2],
            'ML302S/ML307S': [0, 1, 3],  # 不支持2，3表示NITZ更新GMT时间到系统
            'ML305U/ML551Z': [0, 1]  # 不支持2
        },
        'mode_meanings': {
            0: 'NITZ not update system time',
            1: 'NITZ update local time to system',
            2: 'NITZ update GMT time to system',
            3: 'NITZ update GMT time to system (ML302S/ML307S)'
        },
        'default_values': {
            'mode': 0
        },
        'result': [r'OK'],
        'search_result': [r'OK', r'\+CTZU: \([0-9,]+\)'],
        'read_result': [r'OK', r'\+CTZU: {mode}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+'],
        'special_notes': {
            'ML302A/ML305A/ML307A/ML307R/ML307B/ML307C/ML305M/ML307M/ML307N/ML307H/ML307G': '不支持该命令',
            'ML302S/ML307S': '参数1表示启用NITZ自动时区更新并更新GMT时间到URC'
        }
    }
    return ctzu


def set_ctzr(reporting=0):
    """
    AT+CTZR Time zone report
    时区报告设置
    """
    ctzr = {
        'command': 'AT+CTZR',
        'send_data': f'AT+CTZR={reporting}',
        'search_data': 'AT+CTZR=?',
        'read_data': 'AT+CTZR?',
        'reporting_range': {
            'default': [0, 1, 2, 3],
            'ML302S/ML307S': [0, 1, 2],  # 不支持3
            'ML551Z': [0, 1],  # 不支持2和3
            'MR880A': [0, 1, 2]  # 不支持3，默认值为0
        },
        'reporting_meanings': {
            0: 'Disable time zone change event reporting',
            1: 'Enable time zone change event reporting by +CTZV:<tz>',
            2: 'Enable extended time zone and local time reporting by +CTZE: <tz>,<dst>,[<time>]',
            3: 'Enable extended time zone and universal time reporting by +CTZEU: <tz>,<dst>,[<utime>]'
        },
        'tz_range': [-48, 56],
        'dst_range': [0, 1, 2],
        'default_values': {
            'reporting': 0
        },
        'result': [r'OK'],
        'search_result': [r'OK', r'\+CTZR: \([0-9,]+\)'],
        'read_result': [r'OK', r'\+CTZR: {reporting}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+'],
        'special_notes': {
            'ML302A/ML305A/ML307A/ML307R/ML307B/ML307C/ML305M/ML307M': '不支持该命令',
            'MR380R': '不支持该命令'
        }
    }
    return ctzr


def set_cireg(mode=0):
    """
    AT+CIREG Network registration status (从手册上下文推断)
    网络注册状态设置
    """
    cireg = {
        'command': 'AT+CIREG',
        'send_data': f'AT+CIREG={mode}',
        'search_data': 'AT+CIREG=?',
        'read_data': 'AT+CIREG?',
        'mode_range': {
            'default': [0, 1, 2],
            'MR880A': [0, 1]  # 从手册上下文推断支持
        },
        'mode_meanings': {
            0: 'Disable network registration unsolicited result code',
            1: 'Enable network registration unsolicited result code',
            2: 'Enable network registration and location information unsolicited result code'
        },
        'default_values': {
            'mode': 0
        },
        'result': [r'OK'],
        'search_result': [r'OK', r'\+CIREG: \([0-9,]+\)'],
        'read_result': [r'OK', r'\+CIREG: {mode}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+'],
        'special_notes': {
            'MR880A': '支持该命令'
        }
    }
    return cireg


def set_cgpiaf():
    """
    AT+CGPIAF (从手册上下文推断)
    GPRS IP address format设置
    """
    cgpiaf = {
        'command': 'AT+CGPIAF',
        'send_data': 'AT+CGPIAF',
        'search_data': 'AT+CGPIAF=?',
        'read_data': 'AT+CGPIAF?',
        'result': [r'OK'],
        'search_result': [r'OK'],
        'read_result': [r'OK', r'\+CGPIAF: [0-9,]+'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+'],
        'special_notes': {
            'MR880A': '支持该命令'
        }
    }
    return cgpiaf