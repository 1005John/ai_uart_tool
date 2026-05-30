import re


def set_csms(service=1):
    """
    AT+CSMS - Select message service
    """
    csms = {
        'command': 'AT+CSMS',
        'send_data': f'AT+CSMS={service}',
        'search_data': 'AT+CSMS?',
        'service_range': {
            'default': [0, 510],
            'MN319/MN319-A': [0, 510],
            'ML302S/ML307S': [],  # 不支持此命令
            'medium_products': [0, 1],
            # ML302S/ML307S/ML302A/ML305A/ML307A/ML307R/ML307B/ML307C/ML305U/ML307H/ML307G-DC/ML307X/ML307Y等不支持参数2~128
            'nb_products': [0, 1],  # MN319/MN319-A不支持参数2~128
            'high_products': [0, 1],  # MF308C/MF572E/MR880A不支持参数2~128
            'tbd_products': [0]  # MN327不支持参数1,2~128
        },
        'not_supported_products': ['ML302S', 'ML307S'],
        'default_values': {
            'service': 1
        },
        'result': [r'OK', rf'\+CSMS: \d+,\d+,\d+'],
        'search_result': [r'OK', rf'\+CSMS: {service},\d+,\d+,\d+'],
        'err_result': [r'\+CMS ERROR: \d+', r'\+CME ERROR: \d+']
    }
    return csms


def set_cmgf(mode=0):
    """
    AT+CMGF - Select SMS message format
    """
    cmgf = {
        'command': 'AT+CMGF',
        'send_data': f'AT+CMGF={mode}',
        'search_data': 'AT+CMGF?',
        'mode_range': {
            'default': [0, 1],
            'nb_products': [0],  # MN316/MN316A/MN326A/MN319/MN319-A/MN326不支持参数1
            'tbd_products': [1]  # MN327默认1
        },
        'not_supported_products': [
            'ML305A-DL', 'ML307A-DL', 'ML307R-DL', 'ML307B', 'ML307R-BL',
            'ML307R-ML', 'ML307C-DL-CN', 'ML307C-DL-EM', 'ML305M', 'ML307M',
            'ML307N', 'ML307H-DU', 'ML307H-MU', 'ML307H-DC', 'ML307G-DL',
            'ML307G-BL', 'M5310-E', 'MN328', 'MN318', 'ML551Z'
        ],
        'default_values': {
            'mode': 0
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+CMGF: {mode}'],
        'err_result': [r'\+CMS ERROR: \d+', r'\+CME ERROR: \d+']
    }
    return cmgf


def set_csmp(fo=17, vp=167, pid=0, dcs=0):
    """
    AT+CSMP - Set SMS text mode parameters
    """
    csmp = {
        'command': 'AT+CSMP',
        'send_data': f'AT+CSMP={fo},{vp},{pid},{dcs}',
        'search_data': 'AT+CSMP?',
        'fo_range': {
            'default': [0, 255],
            'medium_products': [1, 17, 49]  # ML305U只支持17,49; ML307B只支持1
        },
        'vp_range': {
            'default': [0, 255],
            'medium_products': [167]  # ML307B必须配置为默认值
        },
        'pid_range': {
            'default': [0, 255],
            'medium_products': [0]  # ML307B只支持0
        },
        'dcs_range': {
            'default': [0, 27],
            'medium_products': [0, 11, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27]  # ML307B支持0-11和16-27
        },
        'not_supported_products': [
            'MN316', 'MN316A', 'MN326A', 'M5310-E', 'MN328', 'MN319',
            'MN319-A', 'MN318', 'MN326', 'ML305A-DL', 'ML307A-DL', 'ML307R-DL',
            'ML307B-DL', 'ML307B-AL', 'ML307R-BL', 'ML307R-ML', 'ML307C-DL-CN',
            'ML307C-DL-EM', 'ML307G-DL', 'ML307H-DU', 'ML307H-MU', 'ML307H-DC',
            'ML307G-BL'
        ],
        'default_values': {
            'fo': 17,
            'vp': 167,
            'pid': 0,
            'dcs': 0
        },
        'special_notes': {
            'ML551Z': '推荐设置AT+CSMP=49,255,0,0',
            'ML305M/ML307M/ML307N': 'vp值取决于fo参数的bit3和bit4组合'
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+CSMP: {fo},{vp},{pid},{dcs}'],
        'err_result': [r'\+CMS ERROR: \d+', r'\+CME ERROR: \d+']
    }
    return csmp


def set_csca(sca="", tosca=145):
    """
    AT+CSCA - Service center address
    """
    csca = {
        'command': 'AT+CSCA',
        'send_data': f'AT+CSCA="{sca}",{tosca}' if sca else 'AT+CSCA?',
        'search_data': 'AT+CSCA?',
        'sca_format': '字符串格式，GSM 04.11 RP SC地址',
        'tosca_range': [0, 255],
        'not_supported_products': [
            'ML305A-DL', 'ML307A-DL', 'ML307R-DL', 'ML307B-DL', 'ML307B-AL',
            'ML307R-BL', 'ML307R-ML', 'ML307C-DL-CN', 'ML307C-DL-EM',
            'ML307G-DL', 'ML307H-DU', 'ML307H-MU', 'ML307H-DC', 'ML307G-BL'
        ],
        'special_notes': {
            'M5310-E': '不支持"+"，请使用"00"代替',
            'MN318': '不支持"+"，请使用"00"代替',
            'MN328': '不支持"+"，请使用"00"代替',
            'MF308C/MF572E': '不支持"+"'
        },
        'default_values': {
            'sca': "",
            'tosca': 145
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+CSCA: "{re.escape(sca)}",{tosca}'] if sca else [r'OK', r'\+CSCA: ".+",\d+'],
        'err_result': [r'\+CMS ERROR: \d+', r'\+CME ERROR: \d+']
    }
    return csca


def set_csdh(show=0):
    """
    AT+CSDH - Show SMS text mode parameters
    """
    csdh = {
        'command': 'AT+CSDH',
        'send_data': f'AT+CSDH={show}',
        'search_data': 'AT+CSDH?',
        'show_range': [0, 1],
        'not_supported_products': [
            'MN316', 'MN316A', 'MN326A', 'M5310-E', 'MN327', 'MN328',
            'MN319', 'MN319-A', 'MN318', 'MN326', 'ML305A-DL', 'ML307A-DL',
            'ML307R-DL', 'ML307B-DL', 'ML307B-AL', 'ML307R-BL', 'ML307R-ML',
            'ML307C-DL-CN', 'ML307C-DL-EM', 'ML307G-DL', 'ML307H-DU',
            'ML307H-MU', 'ML307H-DC', 'ML307G-BL', 'MR880A'
        ],
        'default_values': {
            'show': 0
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+CSDH: {show}'],
        'err_result': [r'\+CMS ERROR: \d+', r'\+CME ERROR: \d+']
    }
    return csdh


def set_cnmi(mode=0, mt=0, bm=0, ds=0, bfr=0):
    """
    AT+CNMI - SMS event reporting configuration
    """
    cnmi = {
        'command': 'AT+CNMI',
        'send_data': f'AT+CNMI={mode},{mt},{bm},{ds},{bfr}',
        'search_data': 'AT+CNMI?',
        'mode_range': {
            'default': [0, 3],
            'nb_products': [3],  # M5310-E/MN328/MN319/MN319-A/MN318只支持3
            'medium_products': [0, 1, 2],  # ML302S/ML307S/ML307G-DC不支持3
            'high_products': [0, 1, 2]  # MR880A不支持3
        },
        'mt_range': {
            'default': [0, 3],
            'nb_products': [0, 2],  # MN318/MN328支持0和2
            'medium_products': [1, 2],  # ML307X/ML307Y/ML307B默认1，只支持1和2
            'high_products': [2]  # MR380M默认2
        },
        'bm_range': {
            'default': [0, 3],
            'nb_products': [0],  # M5310-E/MN328/MN318不支持
            'medium_products': [0, 2],  # 不同型号支持范围不同
            'high_products': [0, 2]  # MR880A/MR380M只支持0,2
        },
        'ds_range': {
            'default': [0, 2],
            'nb_products': [0],  # M5310-E/MN318/MN328不支持
            'medium_products': [0, 1],  # ML305U不支持2
            'high_products': [1]  # MR380M默认1
        },
        'bfr_range': {
            'default': [0, 1],
            'nb_products': [0]  # M5310-E/MN328/MN318不支持
        },
        'default_values': {
            'mode': 0,
            'mt': 0,
            'bm': 0,
            'ds': 0,
            'bfr': 0
        },
        'special_notes': {
            'ML551Z': '推荐设置AT+CNMI=2,2,0,1,0，不支持+CMTI/+CDSI URC'
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+CNMI: {mode},{mt},{bm},{ds},{bfr}'],
        'err_result': [r'\+CMS ERROR: \d+', r'\+CME ERROR: \d+']
    }
    return cnmi


def set_cmgr(index=1):
    """
    AT+CMGR - Read message
    """
    cmgr = {
        'command': 'AT+CMGR',
        'send_data': f'AT+CMGR={index}',
        'index_range': [1, 255],  # 具体范围取决于存储容量
        'not_supported_products': [
            'MN316', 'MN316A', 'MN326A', 'M5310-E', 'MN328', 'MN319',
            'MN319-A', 'MN318', 'MN326', 'ML305A-DL', 'ML307A-DL', 'ML307R-DL',
            'ML307B-DL', 'ML307B-AL', 'ML307R-BL', 'ML307R-ML', 'ML307C-DL-CN',
            'ML307C-DL-EM', 'ML307G-DL', 'ML307H-DU', 'ML307H-MU', 'ML307H-DC',
            'ML307G-BL'
        ],
        'default_values': {
            'index': 1
        },
        'result': [r'OK', r'\+CMGR: .+'],
        'err_result': [r'\+CMS ERROR: \d+', r'\+CME ERROR: \d+']
    }
    return cmgr


def set_cmgc(fo=2, ct=0, pid=0, mn=0, da="", toda=129):
    """
    AT+CMGC - Send command
    """
    cmgc = {
        'command': 'AT+CMGC',
        'send_data': f'AT+CMGC={fo},{ct},{pid},{mn},"{da}",{toda}' if da else f'AT+CMGC={fo},{ct},{pid},{mn}',
        'fo_range': [0, 255],
        'ct_range': [0, 255],
        'pid_range': [0, 255],
        'mn_range': [0, 255],
        'toda_range': [129, 145, 161],
        'not_supported_products': [
            'MN327', 'MN319', 'MN319-A', 'ML305A-DL', 'ML307A-DL', 'ML307R-DL',
            'ML307B', 'ML307R-BL', 'ML307R-ML', 'ML307C-DL-CN', 'ML307C-DL-EM',
            'ML305M', 'ML307M', 'ML307N', 'ML307G-DL', 'ML307H-DU', 'ML307H-MU',
            'ML307H-DC', 'ML307G-BL'
        ],
        'special_notes': {
            'MN319/MN319-A': 'PDU模式支持最大长度176'
        },
        'default_values': {
            'fo': 2,
            'ct': 0,
            'pid': 0,
            'mn': 0,
            'da': "",
            'toda': 129
        },
        'result': [r'OK', r'\+CMGC: \d+'],
        'err_result': [r'\+CMS ERROR: \d+', r'\+CME ERROR: \d+']
    }
    return cmgc


def set_cmgl(stat=4):
    """
    AT+CMGL - List messages
    """
    cmgl = {
        'command': 'AT+CMGL',
        'send_data': f'AT+CMGL={stat}',
        'search_data': 'AT+CMGL=?',
        'stat_range': {
            'default': [0, 8],
            'medium_products': [0, 1, 2, 3, 4],  # 不支持参数8
            'high_products': [0, 1, 2, 3, 4]  # MR880A只支持0~4
        },
        'not_supported_products': [
            'MN316', 'MN316A', 'MN326A', 'M5310-E', 'MN328', 'MN319',
            'MN319-A', 'MN318', 'MN326'
        ],
        'default_values': {
            'stat': 4  # "ALL"
        },
        'result': [r'OK', r'\+CMGL: .+'],
        'search_result': [r'OK', r'\+CMGL: \(.+\)'],
        'err_result': [r'\+CMS ERROR: \d+', r'\+CME ERROR: \d+']
    }
    return cmgl


def set_cmgd(index=1, delflag=0):
    """
    AT+CMGD - Delete message
    """
    cmdg = {
        'command': 'AT+CMGD',
        'send_data': f'AT+CMGD={index},{delflag}',
        'search_data': 'AT+CMGD=?',
        'index_range': [1, 255],  # 具体范围取决于存储容量
        'delflag_range': [0, 4],
        'not_supported_products': [
            'ML305A-DL', 'ML307A-DL', 'ML307R-DL', 'ML307B-DL', 'ML307B-AL',
            'ML307R-BL', 'ML307R-ML', 'ML307C-DL-CN', 'ML307C-DL-EM',
            'ML307G-DL', 'ML307H-DU', 'ML307H-MU', 'ML307H-DC', 'ML307G-BL'
        ],
        'default_values': {
            'index': 1,
            'delflag': 0
        },
        'result': [r'OK'],
        'search_result': [r'OK', r'\+CMGD: \(.+\),\(.+\)'],
        'err_result': [r'\+CMS ERROR: \d+', r'\+CME ERROR: \d+']
    }
    return cmdg


def set_cmgw(da="", toda=129, stat=2, length=0, message=""):
    """
    AT+CMGW - Write message to memory
    """
    if message:
        send_data = f'AT+CMGW="{da}",{toda},{stat}\r{message}\x1A'
    else:
        send_data = f'AT+CMGW={length},{stat}'

    cmgw = {
        'command': 'AT+CMGW',
        'send_data': send_data,
        'toda_range': [129, 145, 161],
        'stat_range': [0, 1, 2, 3],  # REC UNREAD, REC READ, STO UNSENT, STO SENT
        'not_supported_products': [
            'M5310-E', 'MN328', 'MN316', 'MN316A', 'MN326A', 'MN319',
            'MN319-A', 'MN318', 'MN326', 'ML305A-DL', 'ML307A-DL', 'ML307R-DL',
            'ML307B-DL', 'ML307B-AL', 'ML307R-BL', 'ML307R-ML', 'ML307C-DL-CN',
            'ML307C-DL-EM', 'ML307G-DL', 'ML307H-DU', 'ML307H-MU', 'ML307H-DC',
            'ML307G-BL', 'ML551Z'
        ],
        'special_notes': {
            'ML302S/ML307S/ML302A/ML305A/ML307A/ML307R/ML307B/ML307C/ML305U/ML307G/ML307H': '不支持长消息'
        },
        'default_values': {
            'da': "",
            'toda': 129,
            'stat': 2,  # STO UNSENT
            'length': 0,
            'message': ""
        },
        'result': [r'OK', r'\+CMGW: \d+'],
        'err_result': [r'\+CMS ERROR: \d+', r'\+CME ERROR: \d+']
    }
    return cmgw


def set_cmgs(da="", toda=129, length=0, message=""):
    """
    AT+CMGS - Send message
    """
    if message:
        send_data = f'AT+CMGS="{da}",{toda}\r{message}\x1A'
    else:
        send_data = f'AT+CMGS={length}'

    cmgs = {
        'command': 'AT+CMGS',
        'send_data': send_data,
        'toda_range': [129, 145],
        'not_supported_products': [
            'ML305A-DL', 'ML307A-DL', 'ML307R-DL', 'ML307B-DL', 'ML307B-AL',
            'ML307R-BL', 'ML307R-ML', 'ML307C-DL-CN', 'ML307C-DL-EM',
            'ML307G-DL', 'ML307H-DU', 'ML307H-MU', 'ML307H-DC', 'ML307G-BL'
        ],
        'special_notes': {
            'MN316/MN316A/MN326A/MN326': '响应时间不超过13分钟',
            'MN327': '响应时间不超过405秒',
            'MF308C': '发送短信前需发送AT+EIMSCFG=1,0,0,0,1,1激活IMS网络'
        },
        'default_values': {
            'da': "",
            'toda': 129,
            'length': 0,
            'message': ""
        },
        'result': [r'OK', r'\+CMGS: \d+'],
        'err_result': [r'\+CMS ERROR: \d+', r'\+CME ERROR: \d+']
    }
    return cmgs


def set_cmss(index=1, da="", toda=129):
    """
    AT+CMSS - Send message from storage
    """
    cmss = {
        'command': 'AT+CMSS',
        'send_data': f'AT+CMSS={index},"{da}",{toda}' if da else f'AT+CMSS={index}',
        'index_range': [1, 255],  # 具体范围取决于存储容量
        'toda_range': [129, 145],
        'not_supported_products': [
            'ML305A-DL', 'ML307A-DL', 'ML307R-DL', 'ML307B-DL', 'ML307B-AL',
            'ML307R-BL', 'ML307R-ML', 'ML307C-DL-CN', 'ML307C-DL-EM',
            'ML307G-DL', 'ML307H-DU', 'ML307H-MU', 'ML307H-DC', 'ML307G-BL',
            'ML551Z'
        ],
        'special_notes': {
            'MF308C': '发送短信前需发送AT+EIMSCFG=1,0,0,0,1,1激活IMS网络'
        },
        'default_values': {
            'index': 1,
            'da': "",
            'toda': 129
        },
        'result': [r'OK', r'\+CMSS: \d+'],
        'err_result': [r'\+CMS ERROR: \d+', r'\+CME ERROR: \d+']
    }
    return cmss


def set_cpms(mem1="SM", mem2="SM", mem3="SM"):
    """
    AT+CPMS - Preferred SMS message storage
    """
    cpms = {
        'command': 'AT+CPMS',
        'send_data': f'AT+CPMS="{mem1}","{mem2}","{mem3}"',
        'search_data': 'AT+CPMS?',
        'mem_options': {
            'SM': 'SIM message storage',
            'ME': 'ME message storage',
            'SR': 'Status Report message storage',
            'SM_P': 'Prioritize SIM storage (high products)',
            'ME_P': 'Prioritize ME storage (high products)',
            'MT': 'Mobile Terminated storage (high products)'
        },
        'mem_restrictions': {
            'medium_products': ['SM', 'ME'],  # 不支持SR等参数
            'high_products': ['SM', 'ME'],  # 不支持SR, SM_P, ME_P, MT等参数
            'ML551Z': ['SM']  # 只支持SIM存储
        },
        'not_supported_products': [
            'ML305A-DL', 'ML307A-DL', 'ML307R-DL', 'ML307B-DL', 'ML307B-AL',
            'ML307R-BL', 'ML307R-ML', 'ML307C-DL-CN', 'ML307C-DL-EM',
            'ML307G-DL', 'ML307H-DU', 'ML307H-MU', 'ML307H-DC', 'ML307G-BL'
        ],
        'default_values': {
            'mem1': "SM",
            'mem2': "SM",
            'mem3': "SM"
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+CPMS: "{mem1}",\d+,\d+,"{mem2}",\d+,\d+,"{mem3}",\d+,\d+'],
        'err_result': [r'\+CMS ERROR: \d+', r'\+CME ERROR: \d+']
    }
    return cpms


def set_cmms(n=0):
    """
    AT+CMMS - Set SMS concat
    """
    cmms = {
        'command': 'AT+CMMS',
        'send_data': f'AT+CMMS={n}',
        'search_data': 'AT+CMMS?',
        'n_range': {
            'default': [0, 2],
            'medium_products': [0, 1]  # ML305U不支持2
        },
        'not_supported_products': [
            'ML305A-DL', 'ML307A-DL', 'ML307R-DL', 'ML307B-DL', 'ML307B-AL',
            'ML307R-BL', 'ML307R-ML', 'ML307C-DL-CN', 'ML307C-DL-EM',
            'ML305M', 'ML307M', 'ML307N', 'ML307G-DL', 'ML307H-DU',
            'ML307H-MU', 'ML307H-DC', 'ML307G-BL', 'MR880A'
        ],
        'default_values': {
            'n': 0
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+CMMS: {n}'],
        'err_result': [r'\+CMS ERROR: \d+', r'\+CME ERROR: \d+']
    }
    return cmms