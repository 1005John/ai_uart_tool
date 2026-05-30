import re


def set_mdmpcfg(enable=0, update_period=1440, appkey="", password=""):
    """
    配置移动DM平台参数
    """
    if appkey and password:
        send_data = f'AT+MDMPCFG={enable},{update_period},"{appkey}","{password}"'
    elif appkey and not password:
        send_data = f'AT+MDMPCFG={enable},{update_period},"{appkey}"'
    elif password and not appkey:
        send_data = f'AT+MDMPCFG={enable},{update_period},,"{password}"'
    else:
        send_data = f'AT+MDMPCFG={enable}'

    mdmpcfg = {
        'command': 'AT+MDMPCFG',
        'send_data': send_data,
        'search_data': 'AT+MDMPCFG=?',
        'enable_range': {
            'default': [0, 1],
            'ML307M': [0, 1, 2]
        },
        'update_period_range': [1, 1440],
        'appkey_max_len': 16,
        'password_max_len': 48,
        'default_values': {
            'enable': 0,
            'update_period': 1440,
            'appkey': "",
            'password': ""
        },
        'special_notes': {
            'ML307M': '支持DM4.0功能，enable参数可设置为2'
        },
        'result': [r'OK'],
        'search_result': [r'\+MDMPCFG: \(list of supported<enable>s\),\(list of supported<updatePeriod>s\),,', r'OK'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mdmpcfg


def set_mdmpcfgex_url(host="m.fxltsbl.com", port=5683):
    """
    配置移动DM平台扩展参数 - 服务器地址和端口
    """
    mdmpcfgex_url = {
        'command': 'AT+MDMPCFGEX',
        'send_data': f'AT+MDMPCFGEX="url","{host}",{port}',
        'search_data': 'AT+MDMPCFGEX="url"',
        'host_max_len': 48,
        'port_range': [0, 65535],
        'default_values': {
            'host': "m.fxltsbl.com",
            'port': 5683
        },
        'result': [r'OK', rf'\+MDMPCFGEX: "url","{re.escape(host)}",{port}'],
        'search_result': [r'OK', rf'\+MDMPCFGEX: "url","{re.escape(host)}",{port}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mdmpcfgex_url


def set_mdmpcfgex_app(app_info="NULL"):
    """
    配置移动DM平台扩展参数 - 应用信息
    """
    mdmpcfgex_app = {
        'command': 'AT+MDMPCFGEX',
        'send_data': f'AT+MDMPCFGEX="app","{app_info}"',
        'search_data': 'AT+MDMPCFGEX="app"',
        'app_info_max_len': 255,
        'default_values': {
            'app_info': "NULL"
        },
        'not_supported_models': ['MN316', 'MN316-S', 'MN319', 'MN319-A', 'MN318', 'MN316A',
                                 'MN326A', 'MN326', 'ML305M', 'ML307M', 'ML307H', 'MR880A',
                                 'ML307X', 'ML307Y', 'ML307N'],
        'result': [r'OK', rf'\+MDMPCFGEX: "app","{re.escape(app_info)}"'],
        'search_result': [r'OK', rf'\+MDMPCFGEX: "app","{re.escape(app_info)}"'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mdmpcfgex_app


def set_mdmpcfgex_hw(tm_type=0, mac="NULL", cpu="NULL", ram="NULL", rom="NULL", gpu="NULL", board="NULL"):
    """
    配置移动DM平台扩展参数 - 硬件信息
    """
    send_data = f'AT+MDMPCFGEX="hw",{tm_type},"{mac}","{cpu}","{ram}","{rom}","{gpu}","{board}"'

    mdmpcfgex_hw = {
        'command': 'AT+MDMPCFGEX',
        'send_data': send_data,
        'search_data': 'AT+MDMPCFGEX="hw"',
        'tm_type_range': (0, 1, 2),
        'mac_max_len': 48,
        'cpu_max_len': 16,
        'ram_max_len': 8,
        'rom_max_len': 8,
        'gpu_max_len': 16,
        'board_max_len': 16,
        'default_values': {
            'tm_type': 0,
            'mac': "NULL",
            'cpu': "NULL",
            'ram': "NULL",
            'rom': "NULL",
            'gpu': "NULL",
            'board': "NULL"
        },
        'special_notes': {
            'MF572E': 'tm_type参数默认值为1',
            'ML307H/ML307M/ML307B': '必采项不支持时设置为"***"'
        },
        'result': [r'OK',
                   rf'\+MDMPCFGEX: "hw",{tm_type},"{re.escape(mac)}","{re.escape(cpu)}","{re.escape(ram)}","{re.escape(rom)}","{re.escape(gpu)}","{re.escape(board)}"'],
        'search_result': [r'OK',
                          rf'\+MDMPCFGEX: "hw",{tm_type},"{re.escape(mac)}","{re.escape(cpu)}","{re.escape(ram)}","{re.escape(rom)}","{re.escape(gpu)}","{re.escape(board)}"'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mdmpcfgex_hw


def set_mdmpcfgex_sw(osver="NULL", firmver="NULL", firmname="NULL"):
    """
    配置移动DM平台扩展参数 - 软件信息
    """
    send_data = f'AT+MDMPCFGEX="sw","{osver}","{firmver}","{firmname}"'

    mdmpcfgex_sw = {
        'command': 'AT+MDMPCFGEX',
        'send_data': send_data,
        'search_data': 'AT+MDMPCFGEX="sw"',
        'osver_max_len': 16,
        'firmver_max_len': 16,
        'firmname_max_len': 16,
        'default_values': {
            'osver': "NULL",
            'firmver': "NULL",
            'firmname': "NULL"
        },
        'special_notes': {
            'ML307H/ML307M/ML307B': '必采项不支持时设置为"***"'
        },
        'result': [r'OK', rf'\+MDMPCFGEX: "sw","{re.escape(osver)}","{re.escape(firmver)}","{re.escape(firmname)}"'],
        'search_result': [r'OK',
                          rf'\+MDMPCFGEX: "sw","{re.escape(osver)}","{re.escape(firmver)}","{re.escape(firmname)}"'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mdmpcfgex_sw


def set_mdmpcfgex_net(nettype="NULL", volte="NULL", phonenum="NULL", account="NULL",
                      location="NULL", rtmac="NULL", btmac="NULL"):
    """
    配置移动DM平台扩展参数 - 网络信息
    """
    send_data = f'AT+MDMPCFGEX="net","{nettype}","{volte}","{phonenum}","{account}","{location}","{rtmac}","{btmac}"'

    mdmpcfgex_net = {
        'command': 'AT+MDMPCFGEX',
        'send_data': send_data,
        'search_data': 'AT+MDMPCFGEX="net"',
        'nettype_max_len': 16,
        'volte_max_len': 8,
        'phonenum_max_len': 16,
        'account_max_len': 16,
        'location_max_len': 16,
        'rtmac_max_len': 48,
        'btmac_max_len': 48,
        'default_values': {
            'nettype': "NULL",
            'volte': "NULL",
            'phonenum': "NULL",
            'account': "NULL",
            'location': "NULL",
            'rtmac': "NULL",
            'btmac': "NULL"
        },
        'special_notes': {
            'ML307H/ML307M/ML307B': '必采项不支持时设置为"***"'
        },
        'result': [r'OK',
                   rf'\+MDMPCFGEX: "net","{re.escape(nettype)}","{re.escape(volte)}","{re.escape(phonenum)}","{re.escape(account)}","{re.escape(location)}","{re.escape(rtmac)}","{re.escape(btmac)}"'],
        'search_result': [r'OK',
                          rf'\+MDMPCFGEX: "net","{re.escape(nettype)}","{re.escape(volte)}","{re.escape(phonenum)}","{re.escape(account)}","{re.escape(location)}","{re.escape(rtmac)}","{re.escape(btmac)}"'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mdmpcfgex_net


def set_mdmpcfgex_prod(brand="NULL", model="NULL", tmplid="NULL"):
    """
    配置移动DM平台扩展参数 - 产品信息
    """
    send_data = f'AT+MDMPCFGEX="prod","{brand}","{model}","{tmplid}"'

    mdmpcfgex_prod = {
        'command': 'AT+MDMPCFGEX',
        'send_data': send_data,
        'search_data': 'AT+MDMPCFGEX="prod"',
        'brand_max_len': 16,
        'model_max_len': 32,
        'tmplid_max_len': 16,
        'default_values': {
            'brand': "NULL",
            'model': "NULL",
            'tmplid': "NULL"
        },
        'special_notes': {
            'ML307H/ML307M/ML307B': '必采项不支持时设置为"***"'
        },
        'result': [r'OK', rf'\+MDMPCFGEX: "prod","{re.escape(brand)}","{re.escape(model)}","{re.escape(tmplid)}"'],
        'search_result': [r'OK',
                          rf'\+MDMPCFGEX: "prod","{re.escape(brand)}","{re.escape(model)}","{re.escape(tmplid)}"'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mdmpcfgex_prod


def set_mdmpcfgex_dev(batcap="NULL", scrnsz="NULL", resolution="NULL", wearing=0):
    """
    配置移动DM平台扩展参数 - 外设信息
    """
    send_data = f'AT+MDMPCFGEX="dev","{batcap}","{scrnsz}","{resolution}",{wearing}'

    mdmpcfgex_dev = {
        'command': 'AT+MDMPCFGEX',
        'send_data': send_data,
        'search_data': 'AT+MDMPCFGEX="dev"',
        'batcap_max_len': 16,
        'scrnsz_max_len': 16,
        'resolution_max_len': 16,
        'wearing_range': [0, 1],
        'default_values': {
            'batcap': "NULL",
            'scrnsz': "NULL",
            'resolution': "NULL",
            'wearing': 0
        },
        'special_notes': {
            'ML307H/ML307M/ML307B': '必采项不支持时设置为"***"'
        },
        'result': [r'OK',
                   rf'\+MDMPCFGEX: "dev","{re.escape(batcap)}","{re.escape(scrnsz)}","{re.escape(resolution)}",{wearing}'],
        'search_result': [r'OK',
                          rf'\+MDMPCFGEX: "dev","{re.escape(batcap)}","{re.escape(scrnsz)}","{re.escape(resolution)}",{wearing}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mdmpcfgex_dev


def set_mpdsregswt(enable=0):
    """
    电信自注册开关
    """
    mpdsregswt = {
        'command': 'AT+MPDSREGSWT',
        'send_data': f'AT+MPDSREGSWT={enable}',
        'search_data': 'AT+MPDSREGSWT=?',
        'enable_range': {
            'default': [0, 1],
            'MN316/MN316-S/ML307X/ML307Y': [0, 1]  # 不支持模式2
        },
        'default_values': {
            'enable': 0
        },
        'special_notes': {
            'MN316/MN316-S': '模组在未进入深度睡眠前提下将自动重试2次',
            '一般模组': '模组在未进入深度睡眠前提下将自动重试9次',
            '不支持型号': ['ML305U', 'ML551Z', 'ML305M', 'MR880A', 'ML307H', 'ML307M', 'MF572E', 'ML307N']
        },
        'result': [r'OK'],
        'search_result': [r'\+MPDSREGSWT: \(list of supported<enable>s\),', r'OK'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mpdsregswt


def set_mpdsregcfg_url(url="http://zzhc.vnet.cn:9999/"):
    """
    电信自注册参数配置 - 服务器地址
    """
    mpdsregcfg_url = {
        'command': 'AT+MPDSREGCFG',
        'send_data': f'AT+MPDSREGCFG="url","{url}"',
        'search_data': 'AT+MPDSREGCFG="url"',
        'url_max_len': 64,
        'default_values': {
            'url': "http://zzhc.vnet.cn:9999/"
        },
        'not_supported_models': ['ML305U', 'ML551Z', 'ML305M', 'MR880A', 'ML307H', 'ML307M', 'MF572E', 'ML307N'],
        'result': [r'OK', rf'\+MPDSREGCFG: "url","{re.escape(url)}"'],
        'search_result': [r'OK', rf'\+MPDSREGCFG: "url","{re.escape(url)}"'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mpdsregcfg_url


def set_mpdsregcfg_meid(meid="NULL"):
    """
    电信自注册参数配置 - 模组串号
    """
    mpdsregcfg_meid = {
        'command': 'AT+MPDSREGCFG',
        'send_data': f'AT+MPDSREGCFG="meid","{meid}"',
        'search_data': 'AT+MPDSREGCFG="meid"',
        'meid_max_len': 32,
        'default_values': {
            'meid': "NULL"
        },
        'not_supported_models': ['ML305U', 'ML551Z', 'ML305M', 'MR880A', 'ML307H', 'ML307M', 'MF572E', 'ML307N'],
        'result': [r'OK', rf'\+MPDSREGCFG: "meid","{re.escape(meid)}"'],
        'search_result': [r'OK', rf'\+MPDSREGCFG: "meid","{re.escape(meid)}"'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mpdsregcfg_meid


def set_mpdsregcfg_model(model="NULL"):
    """
    电信自注册参数配置 - 模组型号
    """
    mpdsregcfg_model = {
        'command': 'AT+MPDSREGCFG',
        'send_data': f'AT+MPDSREGCFG="model","{model}"',
        'search_data': 'AT+MPDSREGCFG="model"',
        'model_max_len': 20,
        'default_values': {
            'model': "NULL"
        },
        'not_supported_models': ['ML305U', 'ML551Z', 'ML305M', 'MR880A', 'ML307H', 'ML307M', 'MF572E', 'ML307N'],
        'result': [r'OK', rf'\+MPDSREGCFG: "model","{re.escape(model)}"'],
        'search_result': [r'OK', rf'\+MPDSREGCFG: "model","{re.escape(model)}"'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mpdsregcfg_model


def set_mpdsregcfg_swver(swver="NULL"):
    """
    电信自注册参数配置 - 模组软件版本号
    """
    mpdsregcfg_swver = {
        'command': 'AT+MPDSREGCFG',
        'send_data': f'AT+MPDSREGCFG="swver","{swver}"',
        'search_data': 'AT+MPDSREGCFG="swver"',
        'swver_max_len': 60,
        'default_values': {
            'swver': "NULL"
        },
        'not_supported_models': ['ML305U', 'ML551Z', 'ML305M', 'MR880A', 'ML307H', 'ML307M', 'MF572E', 'ML307N'],
        'result': [r'OK', rf'\+MPDSREGCFG: "swver","{re.escape(swver)}"'],
        'search_result': [r'OK', rf'\+MPDSREGCFG: "swver","{re.escape(swver)}"'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mpdsregcfg_swver


def set_mpdsregcfg_tmodel(tmodel=""):
    """
    电信自注册参数配置 - 终端型号
    """
    mpdsregcfg_tmodel = {
        'command': 'AT+MPDSREGCFG',
        'send_data': f'AT+MPDSREGCFG="tmodel","{tmodel}"',
        'search_data': 'AT+MPDSREGCFG="tmodel"',
        'tmodel_max_len': 20,
        'default_values': {
            'tmodel': ""
        },
        'not_supported_models': ['MN316', 'MN316-S', 'ML307X', 'ML307Y', 'ML305U', 'ML551Z',
                                 'ML305M', 'MR880A', 'ML307H', 'ML307M', 'MF572E', 'ML307N'],
        'special_notes': {
            'tmodel': '该选项为终端自注册必须参数'
        },
        'result': [r'OK', rf'\+MPDSREGCFG: "tmodel","{re.escape(tmodel)}"'],
        'search_result': [r'OK', rf'\+MPDSREGCFG: "tmodel","{re.escape(tmodel)}"'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mpdsregcfg_tmodel


def set_mpdsregcfg_tswver(tswver=""):
    """
    电信自注册参数配置 - 终端软件版本号
    """
    mpdsregcfg_tswver = {
        'command': 'AT+MPDSREGCFG',
        'send_data': f'AT+MPDSREGCFG="tswver","{tswver}"',
        'search_data': 'AT+MPDSREGCFG="tswver"',
        'tswver_max_len': 60,
        'default_values': {
            'tswver': ""
        },
        'not_supported_models': ['MN316', 'MN316-S', 'ML307X', 'ML307Y', 'ML305U', 'ML551Z',
                                 'ML305M', 'MR880A', 'ML307H', 'ML307M', 'MF572E', 'ML307N'],
        'special_notes': {
            'tswver': '该选项为终端自注册必须参数'
        },
        'result': [r'OK', rf'\+MPDSREGCFG: "tswver","{re.escape(tswver)}"'],
        'search_result': [r'OK', rf'\+MPDSREGCFG: "tswver","{re.escape(tswver)}"'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mpdsregcfg_tswver


def set_mpdsregcfg_tuetype(tuetype=99):
    """
    电信自注册参数配置 - 终端类型
    """
    mpdsregcfg_tuetype = {
        'command': 'AT+MPDSREGCFG',
        'send_data': f'AT+MPDSREGCFG="tuetype","{tuetype}"',
        'search_data': 'AT+MPDSREGCFG="tuetype"',
        'tuetype_max_len': 4,
        'default_values': {
            'tuetype': "99"
        },
        'not_supported_models': ['MN316', 'MN316-S', 'ML307X', 'ML307Y', 'ML305U', 'ML551Z',
                                 'ML305M', 'MR880A', 'ML307H', 'ML307M', 'MF572E', 'ML307N'],
        'result': [r'OK', rf'\+MPDSREGCFG: "tuetype","{re.escape(tuetype)}"'],
        'search_result': [r'OK', rf'\+MPDSREGCFG: "tuetype","{re.escape(tuetype)}"'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mpdsregcfg_tuetype


def set_mpdsregcfg_tmacid(tmacid="NULL"):
    """
    电信自注册参数配置 - 终端Mac地址
    """
    mpdsregcfg_tmacid = {
        'command': 'AT+MPDSREGCFG',
        'send_data': f'AT+MPDSREGCFG="tmacid","{tmacid}"',
        'search_data': 'AT+MPDSREGCFG="tmacid"',
        'tmacid_max_len': 48,
        'default_values': {
            'tmacid': "NULL"
        },
        'not_supported_models': ['MN316', 'MN316-S', 'ML307X', 'ML307Y', 'ML305U', 'ML551Z',
                                 'ML305M', 'MR880A', 'ML307H', 'ML307M', 'MF572E', 'ML307N'],
        'result': [r'OK', rf'\+MPDSREGCFG: "tmacid","{re.escape(tmacid)}"'],
        'search_result': [r'OK', rf'\+MPDSREGCFG: "tmacid","{re.escape(tmacid)}"'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mpdsregcfg_tmacid


def set_mpdsregcfg_tosver(tosver="NULL"):
    """
    电信自注册参数配置 - 终端操作系统版本号
    """
    mpdsregcfg_tosver = {
        'command': 'AT+MPDSREGCFG',
        'send_data': f'AT+MPDSREGCFG="tosver","{tosver}"',
        'search_data': 'AT+MPDSREGCFG="tosver"',
        'tosver_max_len': 32,
        'default_values': {
            'tosver': "NULL"
        },
        'not_supported_models': ['MN316', 'MN316-S', 'ML307X', 'ML307Y', 'ML305U', 'ML551Z',
                                 'ML305M', 'MR880A', 'ML307H', 'ML307M', 'MF572E', 'ML307N'],
        'result': [r'OK', rf'\+MPDSREGCFG: "tosver","{re.escape(tosver)}"'],
        'search_result': [r'OK', rf'\+MPDSREGCFG: "tosver","{re.escape(tosver)}"'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mpdsregcfg_tosver


def set_mpdsregcfg_timei(timei="NULL"):
    """
    电信自注册参数配置 - 终端IMEI号
    """
    mpdsregcfg_timei = {
        'command': 'AT+MPDSREGCFG',
        'send_data': f'AT+MPDSREGCFG="timei","{timei}"',
        'search_data': 'AT+MPDSREGCFG="timei"',
        'timei_max_len': 15,
        'default_values': {
            'timei': "NULL"
        },
        'not_supported_models': ['MN316', 'MN316-S', 'ML307X', 'ML307Y', 'ML305U', 'ML551Z',
                                 'ML305M', 'MR880A', 'ML307H', 'ML307M', 'MF572E', 'ML307N'],
        'result': [r'OK', rf'\+MPDSREGCFG: "timei","{re.escape(timei)}"'],
        'search_result': [r'OK', rf'\+MPDSREGCFG: "timei","{re.escape(timei)}"'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mpdsregcfg_timei


def set_mpdsregcfg_state():
    """
    电信自注册参数配置 - 查询模组电信自注册状态
    """
    mpdsregcfg_state = {
        'command': 'AT+MPDSREGCFG',
        'send_data': 'AT+MPDSREGCFG="state"',
        'search_data': 'AT+MPDSREGCFG="state"',
        'state_range': (0, 1, 2, 3),
        'not_supported_models': ['ML305U', 'ML551Z', 'ML305M', 'MR880A', 'ML307H', 'ML307M', 'MF572E', 'ML307N'],
        'result': [r'OK', r'\+MPDSREGCFG: "state",\d+(,"[^"]*")?'],
        'search_result': [r'OK', r'\+MPDSREGCFG: "state",\d+(,"[^"]*")?'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mpdsregcfg_state


def set_mpdsregcfg_tstate():
    """
    电信自注册参数配置 - 查询终端电信自注册状态
    """
    mpdsregcfg_tstate = {
        'command': 'AT+MPDSREGCFG',
        'send_data': 'AT+MPDSREGCFG="tstate"',
        'search_data': 'AT+MPDSREGCFG="tstate"',
        'tstate_range': (0, 1, 2, 3),
        'not_supported_models': ['MN316', 'MN316-S', 'ML307X', 'ML307Y', 'ML305U', 'ML551Z',
                                 'ML305M', 'MR880A', 'ML307H', 'ML307M', 'MF572E', 'ML307N'],
        'result': [r'OK', r'\+MPDSREGCFG: "tstate",\d+(,"[^"]*")?'],
        'search_result': [r'OK', r'\+MPDSREGCFG: "tstate",\d+(,"[^"]*")?'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mpdsregcfg_tstate