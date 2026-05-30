def set_mlockfreq(mode=0, earfcn=None, pci=None, rat=None, scstype=None):
    """
    AT+MLOCKFREQ - 指定搜索频率
    """
    # 构建发送数据
    params = [str(mode)]
    if earfcn is not None:
        params.append(str(earfcn))
        if pci is not None:
            params.append(str(pci))
            if scstype is not None and rat == "NR":
                params.append(str(scstype))

    if rat is not None:
        send_data = f'AT+MLOCKFREQ="{rat}",{",".join(params)}'
    else:
        send_data = f'AT+MLOCKFREQ={",".join(params)}'

    mlockfreq = {
        'command': 'AT+MLOCKFREQ',
        'send_data': send_data,
        'search_data': 'AT+MLOCKFREQ?',
        'mode_range': {
            'default': [0, 2],
            'MN316/MN316-S/MN316A/MN326A/MN326/ML302S/ML307S/ML302A/ML307A/ML307R/ML307C/ML305A/ML305U/ML305M/ML551Z/ML307M/MF308C/MF572E': [
                0, 1]
        },
        'earfcn_range': {
            'default': [1, 262143],
            'MN316/MN316-S/MN316A/MN326A/MN319/MN326': [1, 65535],
            'MF308C/MF572E': [1, 2279166],
            'ML551Z': [1, 4294967294]
        },
        'pci_range': {
            'default': [0, 503],
            'MF308C': [0, 1007],
            'MF572E': [0, 1008]
        },
        'scstype_range': (0, 1, 2, 3),
        'rat_type': ['LTE', 'NR'],
        'default_values': {
            'mode': 0,
            'earfcn': None,
            'pci': None,
            'rat': None,
            'scstype': None
        },
        'special_notes': {
            'MN316/MN316-S/MN316A/MN326A/MN327/MN319/MN318/MN328/MN326': '仅支持同时配置一路pci和earfcn',
            'ML302S/ML307S/ML302A/ML307A/ML307R/ML307C/ML305A/ML305U/ML305M/ML551Z/ML307M': '为LTE only产品，earfcn有特定支持范围',
            'MR880A': '支持LTE和NR制式，配置将保存至Flash'
        },
        'result': [r'OK'],
        'search_result': [r'OK', r'\+MLOCKFREQ: .*'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mlockfreq


def set_mcsearfcn(mode=0):
    """
    AT+MCSEARFCN - 清除历史频点
    """
    mcsearfcn = {
        'command': 'AT+MCSEARFCN',
        'send_data': f'AT+MCSEARFCN={mode}',
        'mode_range': [0, 0],
        'default_values': {
            'mode': 0
        },
        'special_notes': {
            'MN327/MN316/MN316-S/MN316A/MN326A/M5310-E/MN319/MN318/MN328/MN326': '应执行AT+CFUN=0后使用本命令',
            'MF308C/MR880A/MF572E': '不支持该命令',
            'ML551Z': '不支持该命令',
            'ML307G/ML307H': '应执行AT+CFUN=0后使用本命令'
        },
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mcsearfcn


def set_muestats(type_param="radio"):
    """
    AT+MUESTATS - 查询UE网络信息
    """
    muestats = {
        'command': 'AT+MUESTATS',
        'send_data': f'AT+MUESTATS="{type_param}"',
        'search_data': 'AT+MUESTATS=?',
        'type_range': ['radio', 'cell', 'bler', 'thp', 'sband', 'all'],
        'type_range_limited': {
            'MF308C/MF572E': ['radio', 'cell', 'sband'],
            'MR880A': ['radio', 'cell', 'sband'],
            'ML302S/ML307S/ML302A/ML307A/ML307R/ML307C/ML305A/ML305U/ML305M/ML307M': ['radio', 'cell', 'sband', 'all']
        },
        'rat_range': {
            '0': '无效的网络',
            '1': 'GSM',
            '2': 'WCDMA',
            '3': 'TDSCDMA',
            '4': 'LTE',
            '5': 'eMTC',
            '6': 'NB-IoT',
            '7': 'CDMA',
            '8': 'EVDO',
            '11': 'NR'
        },
        'default_values': {
            'type_param': "radio"
        },
        'special_notes': {
            '单制式模组': 'rat参数为固定值',
            'MN327': 'PSM及eDRX状态下查询到的网络信息均为无效值',
            'ML551Z': '仅当驻网成功后能查询到相关网络信息'
        },
        'result': [r'OK', r'\+MUESTATS: .*'],
        'search_result': [r'OK', r'\+MUESTATS: .*'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return muestats


def set_madc(channel=0):
    """
    AT+MADC - ADC电压读取
    """
    madc = {
        'command': 'AT+MADC',
        'send_data': f'AT+MADC={channel}',
        'search_data': 'AT+MADC=?',
        'channel_range': {
            'default': [0, 3],
            'MN316/MN316-S/MN328/MN327': [0, 0],
            'MN318': [0, 1],
            'ML307A/ML307M': [0, 0],
            'ML305A/ML305U/ML305M/ML307R/ML307C': [0, 1],
            'MF308C': [0, 0],
            'MR880A': [0, 1],
            'MF572E': [1, 3]
        },
        'default_values': {
            'channel': 0
        },
        'special_notes': {
            'ML302S/ML307S/ML551Z': '暂不支持该命令',
            'ML302A/ML305A/ML307A/ML307R/ML307C/ML307G/ML307H': '不支持缺省channel参数'
        },
        'result': [r'OK', rf'\+MADC: \d+'],
        'search_result': [r'OK', r'\+MADC: .*'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return madc


def set_mgpio(pin, control=None, pull=None):
    """
    AT+MGPIO - 控制GPIO
    """
    if control is None:
        send_data = f'AT+MGPIO={pin}'
    elif control == 0:
        send_data = f'AT+MGPIO={pin},{control}'
    else:
        if pull is not None:
            send_data = f'AT+MGPIO={pin},{control},{pull}'
        else:
            send_data = f'AT+MGPIO={pin},{control}'

    mgpio = {
        'command': 'AT+MGPIO',
        'send_data': send_data,
        'search_data': 'AT+MGPIO=?',
        'pin_range': {
            'default': [0, 49],
            'MN316/MN316-S': [16, 17, 34, 35],
            'MN316A/MN326A': [34, 35],
            'M5310-E': [9, 14, 17, 20, 22],
            'MN318': [11, 16, 18, 19, 33, 34, 35, 39, 40, 41, 42],
            'MN319': [7, 34, 35],
            'ML302S': [2, 7, 31, 35, 42, 43, 44, 45, 46],
            'ML302A': [0, 14],
            'ML307A/ML307R-DC/ML307B-DC-CN/ML307R-DL/ML307M-DL': [0, 3],
            'ML307C': [0, 2],
            'ML307M-DA': [0, 1, 3],
            'ML305U': [0, 15],
            'ML305M': [1, 2, 7, 8, 9, 10],
            'MF308C': [153, 156],
            'MR880A': [23, 23],
            'MF572E': [0, 24]
        },
        'control_range': {
            'default': [0, 3],
            'MR880A': [1, 2],
            'MN316/MN316-S/MN316A/MN326A/M5311-E/MN319/MF308C/MF572E': [0, 2],
            'ML302S/ML302A/ML307A/ML307R/ML307C/ML305M/ML307G/ML307H/ML307M': [0, 2]
        },
        'pull_range': (0, 1, 2),
        'dir_range': {
            'default': [0, 2],
            'ML302S/ML302A/ML307A/ML307R/ML307C/ML307G/ML307H/MF308C/MR880A/MF572E': [0, 1]
        },
        'value_range': (0, 1),
        'default_values': {
            'pin': 0,
            'control': None,
            'pull': 0
        },
        'special_notes': {
            'ML307S/ML305A/ML551Z': '暂不支持该命令',
            'MN327/MN326/MN328': '暂不支持该命令'
        },
        'result': [r'OK'],
        'search_result': [r'OK', r'\+MGPIO: .*'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mgpio


def set_mled(led_mode, enable=None):
    """
    AT+MLED - 开关指示灯功能
    """
    if enable is None:
        send_data = f'AT+MLED={led_mode}'
    else:
        send_data = f'AT+MLED={led_mode},{enable}'

    mled = {
        'command': 'AT+MLED',
        'send_data': send_data,
        'search_data': 'AT+MLED=?',
        'led_mode_range': {
            'default': [0, 1],
            'M5310-E/MN318/MN328/MF308C/MR880A': [0, 0]
        },
        'enable_range': (0, 1),
        'default_values': {
            'led_mode': 0,
            'enable': 0
        },
        'special_notes': {
            'ML307S/ML551Z': '暂不支持该命令',
            'MF572E': '暂不支持该命令',
            'MN316-S-DLVS': '不支持运行状态指示灯'
        },
        'result': [r'OK'],
        'search_result': [r'OK', r'\+MLED: .*'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mled


def set_mband(key=None, bands=None):
    """
    AT+MBAND - 频段配置
    """
    if key is None and bands is None:
        send_data = 'AT+MBAND'
    elif key is None:
        send_data = f'AT+MBAND={",".join(map(str, bands))}'
    else:
        send_data = f'AT+MBAND="{key}",{",".join(map(str, bands))}'

    mband = {
        'command': 'AT+MBAND',
        'send_data': send_data,
        'search_data': 'AT+MBAND?',
        'key_range': ['GSM', 'WCDMA', 'TDSCDMA', 'LTE', 'eMTC', 'NBIOT', 'CDMA', 'NR'],
        'key_range_limited': {
            'MR880A/MF572E': ['LTE', 'NR']
        },
        'n_range': {
            'GSM': [0, 9],
            'NBIOT': [0, 1, 3, 5, 8, 20, 28],
            'LTE': [0, 64],
            'NR': [0, 128]
        },
        'n_range_limited': {
            'MN316/MN316-S/MN316A/MN326A/MN326': [1, 3, 5, 8, 20, 28],
            'MN319': [0, 5, 8],
            'MR880A': [0, 1, 3, 5, 8, 34, 38, 39, 40, 41],
            'MF572E': [1, 3, 5, 8, 34, 38, 39, 40, 41],
            'ML307M': [1, 3, 5, 8, 34, 39, 40, 41]
        },
        'default_values': {
            'key': None,
            'bands': []
        },
        'special_notes': {
            'MN316/MN316-S/MN316A/MN326A/MN327/MN319/MN326': '不支持BAND的优先级顺序配置',
            'ML305M/ML307M/ML551Z': '不支持BAND的优先级顺序配置',
            'MF308C/MF572E': '不支持BAND的优先级顺序配置',
            'MR880A': '设置BAND后需执行AT+CFUN=0才能保存至Flash'
        },
        'result': [r'OK'],
        'search_result': [r'OK', r'\+MBAND: .*'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mband


def set_mpsrat(preferred_acts=None):
    """
    AT+MPSRAT - 设置模组制式及优先级
    """
    if preferred_acts is None:
        send_data = 'AT+MPSRAT'
    else:
        acts_str = ','.join([f'"{act}"' for act in preferred_acts])
        send_data = f'AT+MPSRAT={acts_str}'

    mpsrat = {
        'command': 'AT+MPSRAT',
        'send_data': send_data,
        'search_data': 'AT+MPSRAT?',
        'preferred_act_range': ['GSM', 'WCDMA', 'TDSCDMA', 'LTE', 'eMTC', 'NBIOT', 'CDMA', 'NR'],
        'preferred_act_range_limited': {
            'MR880A/MF572E': ['LTE', 'NR']
        },
        'default_values': {
            'preferred_acts': None
        },
        'special_notes': {
            'MF308C': '不支持制式优先级顺序配置',
            'MR880A/MF572E': '设置完后立即生效，重启后仍然保存配置',
            'ML302S/ML307S/ML302A/ML307A/ML307R/ML307C/ML305A/ML305U/ML305M/ML307M/ML551Z/ML307G/ML307H': '不支持该命令'
        },
        'result': [r'OK'],
        'search_result': [r'OK', r'\+MPSRAT: .*'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mpsrat


def set_mchipinfo(cmd):
    """
    AT+MCHIPINFO - 查询芯片信息
    """
    mchipinfo = {
        'command': 'AT+MCHIPINFO',
        'send_data': f'AT+MCHIPINFO="{cmd}"',
        'search_data': 'AT+MCHIPINFO=?',
        'cmd_range': ['vbat', 'temp'],
        'cmd_range_limited': {
            'ML302S/ML307S/ML302A/ML307A/ML307R/ML307B/ML305A/MR880A/MF572E': ['temp'],
            'ML307R/ML307C': ['vbat']
        },
        'default_values': {
            'cmd': 'vbat'
        },
        'special_notes': {
            'MF308C/MR880A/MR880A Mini-PCIe/MR880A M.2/ML307R': '不支持该命令',
            'ML551Z/ML307R/ML307C': '暂不支持该命令'
        },
        'result': [r'OK', rf'\+MCHIPINFO: "{cmd}",.*'],
        'search_result': [r'OK', r'\+MCHIPINFO: .*'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mchipinfo


def set_mmemmtimer(enable=0):
    """
    AT+MEMMTIMER - 使能/禁用EMM定时器URC上报
    """
    memmtimer = {
        'command': 'AT+MEMMTIMER',
        'send_data': f'AT+MEMMTIMER={enable}',
        'search_data': 'AT+MEMMTIMER=?',
        'enable_range': (0, 1),
        'backoff_timerId_range': [0, 3],
        'event_range': [0, 3],
        'default_values': {
            'enable': 0
        },
        'special_notes': {
            'MN316/MN316-S/MN316A/MN326A/M5310-E/MN327/MN319/MN318/MN328/MN326': '不支持该命令',
            'ML302S/ML307S/ML302A/ML307A/ML307R/ML307C/ML305A/ML305U/ML305M/ML551Z/ML307M': '不支持该命令',
            'MF308C/MR880A/MF572E': '不支持该命令',
            'ML307G/ML307H': '仅支持T3346/T3396'
        },
        'result': [r'OK'],
        'search_result': [r'OK', r'\+MEMMTIMER: .*'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return memmtimer


def set_mueconfig(cmd, pdp_type=None, defapn=None, autoconn=None, release_version=None,
                  as_rai=None, two_harq=None, emulti_carrier=None, reestablish=None,
                  hpt_enable=None, hpt_certainty=None, simenable=None, simtype=None,
                  simswap=None, simslot=None, ims_enable=None, ims_rat=None, mac_enable=None):
    """
    AT+MUECONFIG - UE基础行为配置
    """
    params = []
    if pdp_type is not None:
        params.append(f'"{pdp_type}"')
    if defapn is not None:
        params.append(f'"{defapn}"')
    if autoconn is not None:
        params.append(str(autoconn))
    if release_version is not None:
        params.append(str(release_version))
    if as_rai is not None:
        params.append(str(as_rai))
    if two_harq is not None:
        params.append(str(two_harq))
    if emulti_carrier is not None:
        params.append(str(emulti_carrier))
    if reestablish is not None:
        params.append(str(reestablish))
    if hpt_enable is not None:
        params.append(str(hpt_enable))
    if hpt_certainty is not None:
        params.append(str(hpt_certainty))
    if simenable is not None:
        params.append(str(simenable))
    if simtype is not None:
        params.append(str(simtype))
    if simswap is not None:
        params.append(str(simswap))
    if simslot is not None:
        params.append(str(simslot))
    if ims_enable is not None:
        params.append(str(ims_enable))
    if ims_rat is not None:
        params.append(str(ims_rat))
    if mac_enable is not None:
        params.append(str(mac_enable))

    send_data = f'AT+MUECONFIG="{cmd}"'
    if params:
        send_data += f',{",".join(params)}'

    mueconfig = {
        'command': 'AT+MUECONFIG',
        'send_data': send_data,
        'search_data': 'AT+MUECONFIG=?',
        'cmd_range': ['defapn', 'autoconn', 'relver', 'asrai', '2harq', 'emulticar', 'reestablish', 'hpt', 'simenable',
                      'simswap', 'ims', 'mac'],
        'cmd_range_limited': {
            'MN316/MN316-S/MN316A/MN326A/MN326': ['autoconn', 'relver', 'asrai'],
            'M5310-E/MN318/MN328': ['defapn', 'autoconn', 'relver', 'asrai', '2harq', 'reestablish'],
            'MN327': ['defapn', 'relver'],
            'MN319': ['defapn', 'autoconn', 'relver', 'asrai', '2harq', 'emulticar'],
            'ML302A/ML307A/ML307R/ML307C/ML305A/ML305U/ML305M/ML307M': ['autoconn'],
            'MF308C': ['autoconn'],
            'MR880A': ['autoconn', 'hpt', 'simenable', 'simswap', 'ims', 'mac']
        },
        'pdp_type_range': ['IP', 'IPV6', 'IPV4V6', 'PPP', 'Non-IP'],
        'autoconn_range': (0, 1),
        'release_version_range': [13, 16],
        'as_rai_range': (0, 1),
        'two_harq_range': (0, 1),
        'emulti_carrier_range': (0, 1),
        'reestablish_range': (0, 1),
        'hpt_enable_range': (0, 1),
        'simenable_range': (0, 1),
        'simtype_range': (0, 1),
        'simswap_range': (0, 1),
        'ims_enable_range': (0, 1),
        'ims_rat_range': [0, 4, 11],
        'mac_enable_range': (0, 1),
        'default_values': {
            'cmd': 'autoconn',
            'pdp_type': None,
            'defapn': None,
            'autoconn': 1,
            'release_version': 14,
            'as_rai': 1,
            'two_harq': 1,
            'emulti_carrier': None,
            'reestablish': 1,
            'hpt_enable': None,
            'hpt_certainty': None,
            'simenable': None,
            'simtype': 0,
            'simswap': 1,
            'simslot': None,
            'ims_enable': 1,
            'ims_rat': 0,
            'mac_enable': 0
        },
        'special_notes': {
            'ML302S/ML307S/ML551Z': '暂不支持该命令',
            'MF572E': '不支持该命令',
            'ML307M': '设置autoconn为1时，若开机成功连接到网络则模组和上位机均建立数据连接'
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MUECONFIG: "{cmd}",.*'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mueconfig


def set_meid():
    """
    AT+MEID - 读取SIM eID
    """
    meid = {
        'command': 'AT+MEID',
        'send_data': 'AT+MEID',
        'search_data': 'AT+MEID?',
        'result': [r'OK', r'\+MEID: .*'],
        'search_result': [r'OK', r'\+MEID: .*'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return meid


def set_mpwmdata(channel, period=None, duty=None, periods=None, duties=None):
    """
    AT+MPWMDATA - 设置PWM数据
    """
    if period is None and duty is None and periods is None and duties is None:
        send_data = f'AT+MPWMDATA={channel}'
    else:
        if periods is not None and duties is not None:
            # 多组数据
            data_parts = []
            for i in range(len(periods)):
                data_parts.append(str(periods[i]))
                data_parts.append(str(duties[i]))
            data_str = ','.join(data_parts)
            send_data = f'AT+MPWMDATA={channel},{data_str}'
        else:
            # 单组数据
            send_data = f'AT+MPWMDATA={channel},{period},{duty}'

    mpwmdata = {
        'command': 'AT+MPWMDATA',
        'send_data': send_data,
        'search_data': 'AT+MPWMDATA?',
        'channel_range': [0, 1],
        'period_range': {
            'default': [10, 10000],
            'ML307G': [3, 655],
            'ML307H': [10, 2521]
        },
        'duty_range': [0, 100],
        'default_values': {
            'channel': 0,
            'period': None,
            'duty': None,
            'periods': None,
            'duties': None
        },
        'special_notes': {
            'ML307A/ML307C/ML307R': '仅支持单个波形重复',
            'ML307G/ML307H': 'PWM波周期只能是2.56us的整数倍，输入命令时向上取整'
        },
        'result': [r'OK'],
        'search_result': [r'OK', r'\+MPWMDATA: .*'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mpwmdata


def set_mpwmctrl(channel, onoff, cycles=None):
    """
    AT+MPWMCTRL - PWM控制
    """
    if cycles is None:
        send_data = f'AT+MPWMCTRL={channel},{onoff}'
    else:
        send_data = f'AT+MPWMCTRL={channel},{onoff},{cycles}'

    mpwmctrl = {
        'command': 'AT+MPWMCTRL',
        'send_data': send_data,
        'onoff_range': (0, 1),
        'cycles_range': [0, 1000],
        'default_values': {
            'channel': 0,
            'onoff': 0,
            'cycles': 0
        },
        'special_notes': {
            'ML307A/ML307C/ML307R': '暂不支持cycles参数'
        },
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mpwmctrl