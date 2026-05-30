import re

def set_cgdcont(cid=1, pdp_type="IP", apn=""):
    """
    AT+CGDCONT - Define PDP Context
    """
    # 构建发送数据，处理可选参数
    params = [str(int(cid)), f"{pdp_type}"]

    if apn:
        params.append(f"{apn}")
    # else:
    #     params.append("")

    # PDP_addr参数被忽略，仅用于向后兼容
    params.append("")


    send_data = f"AT+CGDCONT={','.join(params)}"

    cgdcont = {
        'command': 'AT+CGDCONT',
        'send_data': send_data,
        'search_data': 'AT+CGDCONT?',
        'cid_range': {
            'default': [1, 15],
            'ML302S/ML307S/ML302A/ML305A/ML307A/ML307R/ML307B/ML307C': [1, 15],
            'ML305U': [1, 7],
            'ML305M/ML307M/ML307N': [1, 8],
            'ML307G/ML307H': [1, 5],
            'ML307X/ML307Y': [1, 15],
            'ML551Z': [1, 1]
        },
        'pdp_type_range': ("IP", "IPV6", "IPV4V6"),
        'd_comp_range': {
            'default': [0, 3],
            'ML307X/ML307Y': [0, 0]
        },
        'h_comp_range': {
            'default': [0, 4],
            'ML307X/ML307Y': [0, 0]
        },
        'apn_max_len': 100,
        'default_values': {
            'cid': 1,
            'pdp_type': "IP",
            'apn': "",
            'd_comp': 0,
            'h_comp': 0
        },
        'special_notes': {
            'ML302A/ML305A/ML307A/ML307R/ML307B/ML307C': '不支持PPP和Non-IP类型',
            'ML307X/ML307Y': 'd_comp和h_comp仅支持参数0',
            'ML305M/ML307M/ML307N': 'cid1是默认配置，其他cid需用户配置后才生效',
            'ML551Z': '仅支持CID1设置'
        },
        'result': [r'OK'],
        'search_result': [r'OK',
                          rf'\+CGDCONT: {cid},{re.escape(pdp_type)},{re.escape(apn)}'],
        'err_result': [r'\+CME ERROR: \d+']
    }
    return cgdcont


def set_cgatt(state=1):
    """
    AT+CGATT - Attachment or detachment of PS
    """
    cgatt = {
        'command': 'AT+CGATT',
        'send_data': f'AT+CGATT={state}',
        'search_data': 'AT+CGATT?',
        'state_range': (0, 1),
        'default_values': {
            'state': 1
        },
        'special_notes': {
            'MN327': '响应时间不超过2分钟，期间其他AT命令输入将等待',
            'MN319/MN319-A': '响应时间不超过120秒，期间其他AT命令输入将等待'
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+CGATT: {state}'],
        'err_result': [r'\+CME ERROR: \d+']
    }
    return cgatt


def set_cgact(state=1, cids=None):
    """
    AT+CGACT - Activate or deactivate PDP context
    """
    if cids is None:
        cids = [1]

    cid_list = ','.join(map(str, cids))
    send_data = f'AT+CGACT={state},{cid_list}' if cids else f'AT+CGACT={state}'

    cgact = {
        'command': 'AT+CGACT',
        'send_data': send_data,
        'search_data': 'AT+CGACT?',
        'state_range': (0, 1),
        'cid_range': {
            'default': [1, 15],
            'ML302S/ML307S/ML302A/ML305A/ML307A/ML307R/ML307B/ML307C': [1, 15],
            'ML307G/ML307H': [1, 5],
            'ML305U': [1, 7],
            'ML305M/ML307M/ML307N/ML551Z': [1, 8],
            'ML307X/ML307Y': [1, 15],
            'MF308C': [1, 49],
            'MF572E': [2, 49],
            'MR880A': [0, 31]
        },
        'default_values': {
            'state': 1,
            'cids': [1]
        },
        'special_notes': {
            'MN316/MN316A/MN326A/MN326': '不允许同时激活多个PDP上下文',
            'MN319/MN319-A': '一次只能激活或去激活一个cid',
            'ML302A/ML305A/ML307A/ML307R/ML307B/ML307C/ML307G/ML307H/ML307X/ML307Y': '必须至少激活一个PDP上下文',
            'ML551Z/ML305M/ML307M/ML307N': '不支持AT+CGACT=0去激活所有PDP上下文',
            'MR880A': '使用CGACT命令激活的PDP连接只能使用CGACT命令激活',
            'MR380R': 'CID8专用于IMS'
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+CGACT: {cid_list},{state}'],
        'err_result': [r'\+CME ERROR: \d+']
    }
    return cgact


def set_cgpaddr(cids=None):
    """
    AT+CGPADDR - Show PDP address
    """
    if cids is None:
        cids = []

    cid_list = ','.join(map(str, cids)) if cids else ""
    send_data = f'AT+CGPADDR={cid_list}' if cids else 'AT+CGPADDR'

    cgpaddr = {
        'command': 'AT+CGPADDR',
        'send_data': send_data,
        'search_data': 'AT+CGPADDR=?',
        'cid_range': {
            'default': [1, 15],
            'MN319/MN319-A': [1, 1]
        },
        'default_values': {
            'cids': []
        },
        'special_notes': {
            'MN316/MN316A/MN326A/MN326': '静态地址无法返回，仅输出当前活动PDP的有效IPv6地址',
            'ML551Z': '指定的cid必须已附着'
        },
        'result': [r'OK', r'\+CGPADDR: \d+,".*?"(,".*?")?'],
        'search_result': [r'OK', r'\+CGPADDR: \(\d+(,\d+)*\)'],
        'err_result': [r'\+CME ERROR: \d+']
    }
    return cgpaddr


def set_cgreg(n=1):
    """
    AT+CGREG - Network registration status
    """
    cgreg = {
        'command': 'AT+CGREG',
        'send_data': f'AT+CGREG={n}',
        'search_data': 'AT+CGREG?',
        'n_range': {
            'default': [0, 3],
            'ML551Z': [0, 1],
            'MR880A': [0, 2]
        },
        'default_values': {
            'n': 1
        },
        'special_notes': {
            'ML551Z': '默认n=1，不支持参数3',
            'MR880A': '当驻留在5G时，+CGREG消息报告和查询只有stat，建议使用+C5GREG命令',
            'MR380R': '当驻留在LTE或NR时，+CGREG消息报告和查询只有stat，建议使用+CEREG或+C5GREG命令'
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+CGREG: {n},\d+'],
        'err_result': [r'\+CME ERROR: \d+']
    }
    return cgreg


def set_cereg(n=1):
    """
    AT+CEREG - EPS network registration status
    """
    cereg = {
        'command': 'AT+CEREG',
        'send_data': f'AT+CEREG={n}',
        'search_data': 'AT+CEREG?',
        'n_range': {
            'default': [0, 5],
            'ML302S/ML307S/ML305M/ML307M/ML307N/ML551Z': [0, 2],
            'ML307G/ML307H': [0, 2],
            'MF308C/MF572E': [0, 3],
            'MR880A/MR380M': [0, 2]
        },
        'default_values': {
            'n': 1
        },
        'special_notes': {
            'ML551Z': '当网络掉线时，n将被设置为2'
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+CEREG: {n},\d+'],
        'err_result': [r'\+CME ERROR: \d+']
    }
    return cereg


def set_cgcontrdp(cid=1):
    """
    AT+CGCONTRDP - PDP context read dynamic
    """
    cgcontrdp = {
        'command': 'AT+CGCONTRDP',
        'send_data': f'AT+CGCONTRDP={cid}',
        'search_data': 'AT+CGCONTRDP=?',
        'cid_range': {
            'default': [1, 15]
        },
        'default_values': {
            'cid': 1
        },
        'special_notes': {
            'ML302S/ML307S/ML302A/ML305A/ML307A/ML307R/ML307B/ML307C/ML305U': '子网掩码参数不支持'
        },
        'result': [r'OK', r'\+CGCONTRDP: \d+,\d+,".*?"(,".*?")*'],
        'search_result': [r'OK', r'\+CGCONTRDP: \(\d+(,\d+)*\)'],
        'err_result': [r'\+CME ERROR: \d+']
    }
    return cgcontrdp


def set_cgauth(cid=1, auth_prot=0, userid="", password=""):
    """
    AT+CGAUTH - Define PDP context authentication parameters
    """
    params = [str(cid), str(auth_prot)]

    if userid:
        params.append(f'"{userid}"')
        if password:
            params.append(f'"{password}"')
    elif password:
        params.append('""')
        params.append(f'"{password}"')

    send_data = f"AT+CGAUTH={','.join(params)}"

    cgauth = {
        'command': 'AT+CGAUTH',
        'send_data': send_data,
        'search_data': 'AT+CGAUTH?' if not any(model in ['ML307A', 'ML307R', 'ML307B', 'ML307C'] for model in
                                               ['ML307A', 'ML307R', 'ML307B', 'ML307C']) else None,
        'cid_range': {
            'default': [1, 15]
        },
        'auth_prot_range': {
            'default': [0, 3],
            'MN316A/MN326A': [0, 1],
            'ML307X/ML307Y': [0, 1],
            'MR380M': [0, 1]
        },
        'userid_max_len': {
            'default': 64,
            'ML307X/ML307Y': 16
        },
        'password_max_len': {
            'default': 64,
            'ML307X/ML307Y': 16
        },
        'default_values': {
            'cid': 1,
            'auth_prot': 0,
            'userid': "",
            'password': ""
        },
        'special_notes': {
            'MN319/MN319-A': '命令参数在深度睡眠中不会保存，深度睡眠唤醒后需要重新配置',
            'ML305M/ML307M/ML307N': '支持PAP+CHAP参数',
            'MR380M': '设置命令不支持参数默认值'
        },
        'result': [r'OK'],
        'search_result': [r'OK',
                          rf'\+CGAUTH: {cid},{auth_prot},"{re.escape(userid)}","{re.escape(password)}"'] if not any(
            model in ['ML307A', 'ML307R', 'ML307B', 'ML307C'] for model in
            ['ML307A', 'ML307R', 'ML307B', 'ML307C']) else None,
        'err_result': [r'\+CME ERROR: \d+']
    }
    return cgauth