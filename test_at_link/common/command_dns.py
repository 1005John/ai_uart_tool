import re

def set_cgdcont_data(cid_id=1, pdp_type='IPV4V6', apn='cmnet.mnc002.mcc460.gprs'):
    cgdcont_data = {'command': 'AT+CGDCONT',
                    'send_data': f'AT+CGDCONT={cid_id},"{pdp_type}","{apn}"',
                    'result': [rf'OK'],
                    'err_result':[r'\+CME ERROR: [0-9A-Za-z]+']}
    return cgdcont_data

def set_mipcall_data(op=1, cid=1):
    mipcall_data = {'command': 'AT+MIPCALL',
                    'send_data': f'AT+MIPCALL={op},{cid}',
                    'result': [rf'OK', rf'\+MIPCALL: {cid},{op},.*'],
                    'err_result':[r'\+CME ERROR: [0-9A-Za-z]+']}
    return mipcall_data
def set_mdnscfg_ip(address1="119.29.29.29", address2="114.114.114.114"):
    """
    设置IPv4域名解析服务器地址
    """
    ipv4_pattern = r"([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})"
    if address1 == "" and address2 == "":
        send_data= f'AT+MDNSCFG="ip","",""'
        search_address1 = ipv4_pattern
        search_address2 = ipv4_pattern
    elif address1=="":
        send_data= f'AT+MDNSCFG="ip",,"{address2}"'
        search_address1 = ipv4_pattern
        search_address2 = address2
    elif address2=="":
        send_data= f'AT+MDNSCFG="ip","{address1}"'
        search_address2 = ipv4_pattern
        search_address1 = address1
    else:
        send_data= f'AT+MDNSCFG="ip","{address1}","{address2}"'
        search_address1 = address1
        search_address2 = address2
    mdnscfg_ip = {
        'command': 'AT+MDNSCFG',
        'send_data': send_data,
        'search_data': 'AT+MDNSCFG="ip"',
        'address_max_len': 255,
        'default_values': {
            'address1': "",
            'address2': ""
        },
        'special_notes': {
            'NB系列': '如SIM卡PLMN是46003、46005、460011，ipv4默认值是218.4.4.4',
            'default': 'ipv4默认值为"119.29.29.29"，配置空字符串将清空NV恢复默认'
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MDNSCFG: "ip","{search_address1}","{search_address2}"'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mdnscfg_ip

def set_mdnscfg_ipv6(address1="2400:3200::1", address2="2001:4860:4860::8888"):
    """
    设置IPv6域名解析服务器地址
    """
    # ipv6_pattern = r"([0-9a-fA-F]{0,4}:{1,2}[0-9a-fA-F]{0,4}(?::[0-9a-fA-F]{0,4}){0,6})"
    ipv6_pattern = r"([0-9a-fA-F]{0,4}:{1,2}[0-9a-fA-F]{0,4}(?::[0-9a-fA-F]{0,4}){0,7})"
    if address1 == "" and address2 == "":
        send_data = f'AT+MDNSCFG="ipv6","",""'
        search_address1 = ipv6_pattern
        search_address2 = ipv6_pattern
    elif address1=="":
        send_data= f'AT+MDNSCFG="ipv6",,"{address2}"'
        search_address1 = ipv6_pattern
        search_address2 = address2.upper()
    elif address2=="":
        send_data= f'AT+MDNSCFG="ipv6","{address1}"'
        search_address2 = ipv6_pattern
        search_address1 = address1.upper()
    else:
        send_data= f'AT+MDNSCFG="ipv6","{address1}","{address2}"'
        search_address1 = ipv6_pattern
        search_address2 = ipv6_pattern
    mdnscfg_ipv6 = {
        'command': 'AT+MDNSCFG',
        'send_data': send_data,
        'search_data': 'AT+MDNSCFG="ipv6"',
        'address_max_len': 255,
        'default_values': {
            'address1': "",
            'address2': ""
        },
        'special_notes': {
            'default': 'ipv6默认值为"2400:3200::1"，配置空字符串将清空NV恢复默认'
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MDNSCFG: "ipv6","{search_address1}","{search_address2}"'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mdnscfg_ipv6

def set_mdnscfg_priority(priority=1):
    """
    设置解析协议优先级
    """
    mdnscfg_priority = {
        'command': 'AT+MDNSCFG',
        'send_data': f'AT+MDNSCFG="priority",{priority}',
        'search_data': 'AT+MDNSCFG="priority"',
        'priority_range': (0, 1),
        'priority_range_all': {
            '0': 'IPv4优先',
            '1': 'IPv6优先'
        },
        'default_values': {
            'priority': 1
        },
        'special_notes': {
            'ML302A/ML305A/ML307A/ML307G/ML302S/ML307S/ML305U/ML305M/ML307M/ML307N/ML307R/ML307H/ML307C': '仅支持"priority"优先级设置，暂不保存NV'
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MDNSCFG: "priority",{priority}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mdnscfg_priority

def set_mdnscfg_cached(cached_mode=0, cached_period=3600):
    """
    设置DNS缓存模式
    """
    mdnscfg_cached = {
        'command': 'AT+MDNSCFG',
        'send_data': f'AT+MDNSCFG="cached",{cached_mode},{cached_period}',
        'search_data': 'AT+MDNSCFG="cached"',
        'cached_mode_range': (0, 1),
        'cached_mode_range_all': {
            '0': '使用缓存',
            '1': '不使用缓存'
        },
        'cached_period_range': [1, 65535],
        'default_values': {
            'cached_mode': 0,
            'cached_period': 3600
        },
        'special_notes': {
            'MN316/MN316-S/MN316A/MN326A/MN318/MN319/MN326/ML307X/ML307Y': '暂不支持"cached"缓存设置',
            'ML307G/ML307H': '暂不支持"cached_period"缓存周期',
            'ML307G': '默认值为1'
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MDNSCFG: "cached",{cached_mode},{cached_period}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mdnscfg_cached

def set_mdnscfg_timeout(time=10, retries=3):
    """
    设置DNS超时参数
    """
    mdnscfg_timeout = {
        'command': 'AT+MDNSCFG',
        'send_data': f'AT+MDNSCFG="timeout",{time},{retries}',
        'search_data': 'AT+MDNSCFG="timeout"',
        'time_range': [1, 60],
        'retries_range': [1, 9],
        'default_values': {
            'time': 10,
            'retries': 3
        },
        'special_notes': {
            'NB模组': '默认超时时间30s',
            '4G/5G模组': '默认超时时间10s',
            'MR880A': '不支持重试请求，设置无效，超时后直接退出'
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MDNSCFG: "timeout",{time},{retries}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mdnscfg_timeout

def set_mdnsgip(domainname="", cid=""):
    """
    域名解析命令
    """
    if cid == "" or cid == '""':
        send_data = f'AT+MDNSGIP="{domainname}"'
    else:
        send_data = f'AT+MDNSGIP="{domainname}",{cid}'
    mdnsgip = {
        'command': 'AT+MDNSGIP',
        'send_data': send_data,
        'domainname_max_len': 255,
        'cid_range': {
            'default': [1, 15]
        },
        'default_values': {
            'domainname': "",
            'cid': 1
        },
        'special_notes': {
            'MN316/MN316-S/MN316A/MN326A/MN318/MN319/MN326/ML307G/MR880A/ML307H': '暂不支持cid参数，默认不指定',
            '4G系列': '默认为1'
        },
        'result': [r'OK', rf'\+MDNSGIP: "{domainname}"'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mdnsgip