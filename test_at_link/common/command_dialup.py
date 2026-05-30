import re


def set_mdialupcfg_mode(mode=0):
    """
    设置拨号模式
    """
    mdialupcfg_mode = {
        'command': 'AT+MDIALUPCFG',
        'send_data': f'AT+MDIALUPCFG="mode",{mode}',
        'search_data': f'AT+MDIALUPCFG="mode"',
        'mode_range': {
            'default': [0, 2],
            'ML302S/ML307S/ML302A/ML307A/ML307R/ML307C/ML305A/ML305U/ML305M/ML551Z/ML307G/ML307H/ML307M/ML307X/ML307Y': [
                0, 1],  # 不支持NCM
            'ML307X/ML307Y': [0, 2, 11]  # 支持自适应模式
        },
        'mode_values': {
            0: 'RNDIS',
            1: 'ECM',
            2: 'NCM',
            11: '自适应'
        },
        'default_values': {
            'mode': 0
        },
        'special_notes': {
            'ML307M': 'RNDIS仅支持上位机Windows系统拨号，ECM仅支持上位机Linux系统拨号',
            'ML307X/ML307Y': '默认值11，优先RNDIS'
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MDIALUPCFG: "mode",{mode}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mdialupcfg_mode


def set_mdialupcfg_workmode(workmode=0):
    """
    设置拨号工作模式
    """
    mdialupcfg_workmode = {
        'command': 'AT+MDIALUPCFG',
        'send_data': f'AT+MDIALUPCFG="workmode",{workmode}',
        'search_data': f'AT+MDIALUPCFG="workmode"',
        'workmode_range': {
            'default': [0, 2],
            'ML302A/ML302S/ML305A/ML307A/ML307R/ML307C/ML307S/ML305M/ML551Z/ML307G/ML307H/ML307X/ML307Y/ML307M': []
            # 不支持
        },
        'workmode_values': {
            0: '路由模式',
            1: '网卡模式',
            2: '后路由模式'
        },
        'default_values': {
            'workmode': 0
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MDIALUPCFG: "workmode",{workmode}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mdialupcfg_workmode


def set_mdialupcfg_nicmaxcnt(nicmaxcnt=1):
    """
    设置最大支持网卡数量
    """
    mdialupcfg_nicmaxcnt = {
        'command': 'AT+MDIALUPCFG',
        'send_data': f'AT+MDIALUPCFG="nicmaxcnt",{nicmaxcnt}',
        'search_data': f'AT+MDIALUPCFG="nicmaxcnt"',
        'nicmaxcnt_range': {
            'default': [1, None],  # 具体范围参考测试命令返回
            'ML307C/ML307B': []  # 不支持
        },
        'default_values': {
            'nicmaxcnt': 1
        },
        'special_notes': {
            'MR880A': '只在网卡模式下支持多网卡'
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MDIALUPCFG: "nicmaxcnt",{nicmaxcnt}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mdialupcfg_nicmaxcnt


def set_mdialupcfg_auto(enable=0, conn_interface=0, cid=1):
    """
    设置开机自动拨号配置
    """
    mdialupcfg_auto = {
        'command': 'AT+MDIALUPCFG',
        'send_data': f'AT+MDIALUPCFG="auto",{enable},{conn_interface},{cid}',
        'search_data': f'AT+MDIALUPCFG="auto"',
        'enable_range': [0, 1],
        'conn_interface_range': [0, 1],
        'cid_range': {
            'default': [1, None],  # 范围参考AT+CGDCONT命令
            'ML302A/ML302S/ML305A/ML307A/ML307R/ML307C/ML307S/ML305M/ML551Z/ML307G/ML307H/ML307X/ML307Y/ML307M': [],
            # 不支持
            'ML307B': [0, 0]  # 仅支持cid0
        },
        'enable_values': {
            0: '关闭自动拨号',
            1: '打开自动拨号'
        },
        'conn_interface_values': {
            0: 'USB',
            1: '网口(以太网卡)'
        },
        'default_values': {
            'enable': 0,
            'conn_interface': 0,
            'cid': 1
        },
        'special_notes': {
            'ML307B': '配置自动拨号后需要执行AT+MREBOOT确保配置成功'
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MDIALUPCFG: "auto",{enable},{conn_interface},{cid}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mdialupcfg_auto


def set_mdialupcfg_dhcpv4(dhcp_en=1, dhcp_ip="", dhcp_start=100, dhcp_end=200, lease_time=86400):
    """
    设置DHCPv4服务配置
    """
    mdialupcfg_dhcpv4 = {
        'command': 'AT+MDIALUPCFG',
        'send_data': f'AT+MDIALUPCFG="dhcpv4",{dhcp_en},"{dhcp_ip}",{dhcp_start},{dhcp_end},{lease_time}',
        'search_data': f'AT+MDIALUPCFG="dhcpv4"',
        'dhcp_en_range': {
            'default': [0, 1],
            'ML302A/ML302S/ML305A/ML307S/ML305M/ML307M/ML307X/ML307Y': [],  # 不支持
            'ML307A/ML307R/ML307C/ML307G/ML307H/ML307B': [1, 1]  # 不支持关闭
        },
        'dhcp_start_range': [0, 255],
        'dhcp_end_range': [0, 255],
        'lease_time_range': [3600, 86400],
        'dhcp_en_values': {
            0: '关闭dhcp',
            1: '打开dhcp'
        },
        'default_values': {
            'dhcp_en': 1,
            'dhcp_ip': "",
            'dhcp_start': 100,
            'dhcp_end': 200,
            'lease_time': 86400
        },
        'special_notes': {
            'MR880A': '只支持查询，不可设置',
            'ML307B': '不支持dhcpv4配置与查询'
        },
        'result': [r'OK'],
        'search_result': [r'OK',
                          rf'\+MDIALUPCFG: "dhcpv4",{dhcp_en},"{re.escape(dhcp_ip)}",{dhcp_start},{dhcp_end},{lease_time}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mdialupcfg_dhcpv4


def set_mdialup(connect_params):
    """
    拨号连网操作（通用函数，支持不同产品线参数差异）
    """
    # 根据参数数量判断使用哪种格式
    if len(connect_params) == 2:
        # NB/4G模组格式: AT+MDIALUP=<cid>,<connect>
        cid, connect = connect_params
        send_data = f'AT+MDIALUP={cid},{connect}'
    else:
        # 5G系列模组格式: AT+MDIALUP=<cid>,<connect>[,<conn_interface>]
        cid, connect, conn_interface = connect_params
        send_data = f'AT+MDIALUP={cid},{connect},{conn_interface}'

    mdialup = {
        'command': 'AT+MDIALUP',
        'send_data': send_data,
        'search_data': 'AT+MDIALUP?',
        'cid_range': {
            'default': [1, 1],  # 仅为1有效
            'MR880A': [1, None],  # 网卡模式支持多cid
            'ML307B': [1, 4]  # 范围1-4
        },
        'connect_range': [0, 1],
        'conn_interface_range': [0, 1],
        'connect_values': {
            0: '断开连接',
            1: '建立连接'
        },
        'conn_interface_values': {
            0: 'USB',
            1: '网口(以太网卡)'
        },
        'default_values': {
            'cid': 1,
            'connect': 1,
            'conn_interface': 0
        },
        'special_notes': {
            'ML307M': '仅激活一路cid；且cid为1时，不允许使用AT+MDIALUP命令进行断开连接操作',
            'ML307B': '手动拨号时不支持使用默认cid 0，且不支持多路同时拨号，不支持获取网关信息',
            'MR880A': '路由模式下，cid 1拨号成功后，USB和网口共用一路PDP拨号'
        },
        'result': [r'OK', rf'\+MDIALUP: {cid},{connect}'],
        'search_result': [r'OK', r'\+MDIALUP: \d+,\d+'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mdialup

