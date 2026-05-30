import re
def set_msslcfg_auth(ssl_id=0, cert_verify=0):
    mssslcfg_auth = {
        'command': 'AT+MSSLCFG',
        'send_data': f'AT+MSSLCFG="auth",{ssl_id},{cert_verify}',
        'search_data': f'AT+MSSLCFG="auth",{ssl_id}',
        'cert_verify_range': (0, 1, 2),
        'ssl_id_range': {
            'default': [0, 5],
            'NB系列': [0, 4]
        },
        'default_values': {
            'ssl_id': 0,
            'cert_verify': 0
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MSSLCFG: "auth",{ssl_id},{cert_verify}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+'],
        'special_notes': {
            'MN316/MN326': '从深睡眠唤醒后，SSL所有配置需要重新设置，包括写入的证书；最多同时建立两路SSL连接',
            'ML307X/ML307Y': '最多同时建立两路SSL连接'
        }
    }
    return mssslcfg_auth


def set_msslcfg_cert(ssl_id=0, srv_cert="", cli_cert="", prv_key=""):
    send_data = f'AT+MSSLCFG="cert",{ssl_id},"{srv_cert}","{cli_cert}","{prv_key}"'
    mssslcfg_cert = {
        'command': 'AT+MSSLCFG',
        'send_data': send_data,
        'search_data': f'AT+MSSLCFG="cert",{ssl_id}',
        'ssl_id_range': {
            'default': [0, 5],
            'NB系列': [0, 4]
        },
        'cert_name_max_len': 64,
        'default_values': {
            'ssl_id': 0,
            'srv_cert': "",
            'cli_cert': "",
            'prv_key': ""
        },
        'result': [r'OK'],
        'search_result': [r'OK',
                          rf'\+MSSLCFG: "cert",{ssl_id},"{re.escape(srv_cert)}","{re.escape(cli_cert)}","{re.escape(prv_key)}"'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+'],
        'special_notes': {
            'MN316/MN326': '从深睡眠唤醒后，SSL所有配置需要重新设置，包括写入的证书；最多同时建立两路SSL连接',
            'ML307X/ML307Y': '最多同时建立两路SSL连接'
        }
    }
    return mssslcfg_cert


def set_msslcfg_psk(ssl_id=0, pskid=""):
    mssslcfg_psk = {
        'command': 'AT+MSSLCFG',
        'send_data': f'AT+MSSLCFG="psk",{ssl_id},"{pskid}"',
        'search_data': f'AT+MSSLCFG="psk",{ssl_id}',
        'ssl_id_range': {
            'default': [0, 5],
            'NB系列': [0, 4]
        },
        'pskid_max_len': 64,
        'default_values': {
            'ssl_id': 0,
            'pskid': ""
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MSSLCFG: "psk",{ssl_id},"{re.escape(pskid)}"'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+'],
        'special_notes': {
            '4G系列/MR880A': '不支持该参数',
            'MN316/MN326': '从深睡眠唤醒后，SSL所有配置需要重新设置，包括写入的证书；最多同时建立两路SSL连接',
            'ML307X/ML307Y': '最多同时建立两路SSL连接'
        }
    }
    return mssslcfg_psk


def set_msslcfg_encoding(ssl_id=0, input_format=2):
    mssslcfg_encoding = {
        'command': 'AT+MSSLCFG',
        'send_data': f'AT+MSSLCFG="encoding",{ssl_id},{input_format}',
        'search_data': f'AT+MSSLCFG="encoding",{ssl_id}',
        'input_format_range': (2,),
        'ssl_id_range': {
            'default': [0, 5],
            'NB系列': [0, 4]
        },
        'default_values': {
            'ssl_id': 0,
            'input_format': 2
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MSSLCFG: "encoding",{ssl_id},{input_format}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+'],
        'special_notes': {
            'MN316/MN326/ML302S/ML307S/ML302A/ML305A/ML307A/ML307X/ML307Y/ML305U/ML305M/ML307M/ML307N/ML307G/MR880A/ML307R/ML307C/ML307H': '只支持2转义字符串',
            'MN316/MN326': '从深睡眠唤醒后，SSL所有配置需要重新设置，包括写入的证书；最多同时建立两路SSL连接',
            'ML307X/ML307Y': '最多同时建立两路SSL连接'
        }
    }
    return mssslcfg_encoding


def set_msslcfg_negotime(ssl_id=0, negotiate_timeout=300):
    mssslcfg_negotime = {
        'command': 'AT+MSSLCFG',
        'send_data': f'AT+MSSLCFG="negotime",{ssl_id},{negotiate_timeout}',
        'search_data': f'AT+MSSLCFG="negotime",{ssl_id}',
        'negotiate_timeout_range': [10, 300],
        'ssl_id_range': {
            'default': [0, 5],
            'NB系列': [0, 4]
        },
        'default_values': {
            'ssl_id': 0,
            'negotiate_timeout': 300
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MSSLCFG: "negotime",{ssl_id},{negotiate_timeout}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+'],
        'special_notes': {
            'MN316/MN326': '从深睡眠唤醒后，SSL所有配置需要重新设置，包括写入的证书；最多同时建立两路SSL连接',
            'ML307X/ML307Y': '最多同时建立两路SSL连接'
        }
    }
    return mssslcfg_negotime


def set_msslcfg_version(ssl_id=0, ssl_version=255):
    mssslcfg_version = {
        'command': 'AT+MSSLCFG',
        'send_data': f'AT+MSSLCFG="version",{ssl_id},{ssl_version}',
        'search_data': f'AT+MSSLCFG="version",{ssl_id}',
        'ssl_version_range': (0, 1, 2, 3, 255),
        'ssl_id_range': {
            'default': [0, 5],
            'NB系列': [0, 4]
        },
        'default_values': {
            'ssl_id': 0,
            'ssl_version': 255
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MSSLCFG: "version",{ssl_id},{ssl_version}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+'],
        'special_notes': {
            'MR880A': '不支持TLS1.2以下版本',
            'ML307X/ML307Y': '仅支持TLS 1.1和TLS 1.2',
            'MN316/MN326': '从深睡眠唤醒后，SSL所有配置需要重新设置，包括写入的证书；最多同时建立两路SSL连接',
            'ML307X/ML307Y': '最多同时建立两路SSL连接'
        }
    }
    return mssslcfg_version


def set_msslcfg_ciphersuite(ssl_id=0, cipher_suite=0):
    mssslcfg_ciphersuite = {
        'command': 'AT+MSSLCFG',
        'send_data': f'AT+MSSLCFG="ciphersuite",{ssl_id},{cipher_suite}',
        'search_data': f'AT+MSSLCFG="ciphersuite",{ssl_id}',
        'cipher_suite_type': '十六进制字符串',
        'ssl_id_range': {
            'default': [0, 5],
            'NB系列': [0, 4]
        },
        'default_values': {
            'ssl_id': 0,
            'cipher_suite': 0
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MSSLCFG: "ciphersuite",{ssl_id},{cipher_suite}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+'],
        'special_notes': {
            'ML307X/ML307Y': '十六进制输入加密套件值需携带"0x"',
            'MN316/MN326': '从深睡眠唤醒后，SSL所有配置需要重新设置，包括写入的证书；最多同时建立两路SSL连接',
            'ML307X/ML307Y': '最多同时建立两路SSL连接'
        }
    }
    return mssslcfg_ciphersuite


def set_msslcfg_session(ssl_id=0, session_enable=1):
    mssslcfg_session = {
        'command': 'AT+MSSLCFG',
        'send_data': f'AT+MSSLCFG="session",{ssl_id},{session_enable}',
        'search_data': f'AT+MSSLCFG="session",{ssl_id}',
        'session_enable_range': (0, 1),
        'ssl_id_range': {
            'default': [0, 5],
            'NB系列': [0, 4]
        },
        'default_values': {
            'ssl_id': 0,
            'session_enable': 1
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MSSLCFG: "session",{ssl_id},{session_enable}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+'],
        'special_notes': {
            'MN316/MN326': '从深睡眠唤醒后，SSL所有配置需要重新设置，包括写入的证书；最多同时建立两路SSL连接',
            'ML307X/ML307Y': '最多同时建立两路SSL连接'
        }
    }
    return mssslcfg_session


def set_msslcfg_ignorestamp(ssl_id=0, ignore_stamp=1):
    mssslcfg_ignorestamp = {
        'command': 'AT+MSSLCFG',
        'send_data': f'AT+MSSLCFG="ignorestamp",{ssl_id},{ignore_stamp}',
        'search_data': f'AT+MSSLCFG="ignorestamp",{ssl_id}',
        'ignore_stamp_range': (0, 1),
        'ssl_id_range': {
            'default': [0, 5],
            'NB系列': [0, 4]
        },
        'default_values': {
            'ssl_id': 0,
            'ignore_stamp': 1
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MSSLCFG: "ignorestamp",{ssl_id},{ignore_stamp}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+'],
        'special_notes': {
            'MN316/MN326': '从深睡眠唤醒后，SSL所有配置需要重新设置，包括写入的证书；最多同时建立两路SSL连接',
            'ML307X/ML307Y': '最多同时建立两路SSL连接'
        }
    }
    return mssslcfg_ignorestamp


def set_msslcfg_ignoreverify(ssl_id=0, ignore_verify=0):
    mssslcfg_ignoreverify = {
        'command': 'AT+MSSLCFG',
        'send_data': f'AT+MSSLCFG="ignoreverify",{ssl_id},{ignore_verify}',
        'search_data': f'AT+MSSLCFG="ignoreverify",{ssl_id}',
        'ignore_verify_range': (0, 1),
        'ssl_id_range': {
            'default': [0, 5],
            'NB系列': [0, 4]
        },
        'default_values': {
            'ssl_id': 0,
            'ignore_verify': 0
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MSSLCFG: "ignoreverify",{ssl_id},{ignore_verify}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+'],
        'special_notes': {
            'MN316/MN326': '从深睡眠唤醒后，SSL所有配置需要重新设置，包括写入的证书；最多同时建立两路SSL连接',
            'ML307X/ML307Y': '最多同时建立两路SSL连接'
        }
    }
    return mssslcfg_ignoreverify


def set_msslcfg_sni(ssl_id=0, sni_enable=0):
    mssslcfg_sni = {
        'command': 'AT+MSSLCFG',
        'send_data': f'AT+MSSLCFG="sni",{ssl_id},{sni_enable}',
        'search_data': f'AT+MSSLCFG="sni",{ssl_id}',
        'sni_enable_range': (0, 1),
        'ssl_id_range': {
            'default': [0, 5],
            'NB系列': [0, 4]
        },
        'default_values': {
            'ssl_id': 0,
            'sni_enable': 0
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MSSLCFG: "sni",{ssl_id},{sni_enable}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+'],
        'special_notes': {
            'MR880A': '当前仅MR880A支持该配置',
            'MN316/MN326': '从深睡眠唤醒后，SSL所有配置需要重新设置，包括写入的证书；最多同时建立两路SSL连接',
            'ML307X/ML307Y': '最多同时建立两路SSL连接'
        }
    }
    return mssslcfg_sni


def set_msslcertwr(cert_name="", remain_length=0, length=0, data=""):
    if data:
        send_data = f'AT+MSSLCERTWR="{cert_name}",{remain_length},{length},"{data}"'
    else:
        send_data = f'AT+MSSLCERTWR="{cert_name}",{remain_length},{length}'

    msslcertwr = {
        'command': 'AT+MSSLCERTWR',
        'send_data': send_data,
        'cert_name_max_len': 64,
        'remain_length_range': [0, 8192],
        'length_range': [1, 8192],
        'default_values': {
            'cert_name': "",
            'remain_length': 0,
            'length': 0,
            'data': ""
        },
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+'],
        'special_notes': {
            'MN316/MN326': '不支持">"下的数据输入模式，只能在AT命令中直接输入数据',
            'ML307H-DU': '不支持文件系统，写入的证书在掉电后不会保存'
        }
    }
    return msslcertwr


def set_msslkeywr(key_name="", remain_length=0, length=0, data=""):
    if data:
        send_data = f'AT+MSSLKEYWR="{key_name}",{remain_length},{length},"{data}"'
    else:
        send_data = f'AT+MSSLKEYWR="{key_name}",{remain_length},{length}'

    msslkeywr = {
        'command': 'AT+MSSLKEYWR',
        'send_data': send_data,
        'key_name_max_len': 64,
        'remain_length_range': [0, 8192],
        'length_range': [1, 8192],
        'default_values': {
            'key_name': "",
            'remain_length': 0,
            'length': 0,
            'data': ""
        },
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+'],
        'special_notes': {
            'MN316/MN326': '不支持">"下的数据输入模式，只能在AT命令中直接输入数据',
            'ML307H-DU': '不支持文件系统，写入的私钥在掉电后不会保存'
        }
    }
    return msslkeywr


def set_msslcertrd(cert_name=""):
    msslcertrd = {
        'command': 'AT+MSSLCERTRD',
        'send_data': f'AT+MSSLCERTRD="{cert_name}"',
        'cert_name_max_len': 64,
        'default_values': {
            'cert_name': ""
        },
        'result': [r'OK', rf'\+MSSLCERTRD: \d+,'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+'],
        'special_notes': {
            '客户端私钥': '无法被该命令读取'
        }
    }
    return msslcertrd


def set_mssllist(ca_type=1):
    mssllist = {
        'command': 'AT+MSSLLIST',
        'send_data': f'AT+MSSLLIST={ca_type}',
        'ca_type_range': (1, 2, 3),
        'default_values': {
            'ca_type': 1
        },
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mssllist


def set_msslrm(cert_name=""):
    msslrm = {
        'command': 'AT+MSSLRM',
        'send_data': f'AT+MSSLRM="{cert_name}"',
        'cert_name_max_len': 64,
        'default_values': {
            'cert_name': ""
        },
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return msslrm


def set_msslpsk(pskid="", psk=""):
    msslpsk = {
        'command': 'AT+MSSLPSK',
        'send_data': f'AT+MSSLPSK="{pskid}","{psk}"',
        'pskid_max_len': 64,
        'psk_max_len': 8192,
        'default_values': {
            'pskid': "",
            'psk': ""
        },
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+'],
        'special_notes': {
            'ML302S/ML307S/ML302A/ML305A/ML307A/ML305U/ML305M/ML307G/ML307M/MR880A/ML307X/ML307Y/ML307R/ML307C/ML307H/ML307N': '暂不支持该命令'
        }
    }
    return msslpsk


def set_msslcheck(cert_name="", verify_alg=0):
    msslcheck = {
        'command': 'AT+MSSLCHECK',
        'send_data': f'AT+MSSLCHECK="{cert_name}",{verify_alg}',
        'verify_alg_range': (0, 1, 2, 3),
        'default_values': {
            'cert_name': "",
            'verify_alg': 0
        },
        'result': [r'OK', rf'\+MSSLCHECK: [0-9a-f]+'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+'],
        'special_notes': {
            'MN316/MN326/ML302S/ML307S/ML302A/ML305A/ML307A/ML307G/ML305U/ML305M/ML307M/MR880A/ML307X/ML307Y/ML307R/ML307C/ML307H': '只支持MD5校验'
        }
    }
    return msslcheck


def set_msslcipher():
    msslcipher = {
        'command': 'AT+MSSLCIPHER',
        'send_data': 'AT+MSSLCIPHER=?',
        'result': [r'OK', r'\+MSSLCIPHER: \(.*\)'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+'],
        'special_notes': {
            'ML302S/ML307S': '暂不支持该命令'
        }
    }
    return msslcipher