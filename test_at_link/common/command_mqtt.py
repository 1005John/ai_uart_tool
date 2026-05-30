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

def set_mqttcfg_version(connect_id=0, version=4):
    mqttcfg_version = {
        'command': 'AT+MQTTCFG',
        'send_data': f'AT+MQTTCFG="version",{connect_id},{version}',
        'search_data': f'AT+MQTTCFG="version",{connect_id}',
        'version_range': (3, 4),  # 3: MQTT v3.1, 4: MQTT v3.1.1
        'not_supported_version': {
            'current': [3],  # 当前仅支持version=4
            'default': []  # 默认都支持
        },
        'default_values': {
            'connect_id': 0,
            'version': 4
        },
        'connect_id_range': {
            'default': [0, 5],
            'MN316A/MN326A/MN319': [0, 2]
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MQTTCFG: "version",{version}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mqttcfg_version


def set_mqttcfg_cid(connect_id=0, cid=1):

    mqttcfg_cid = {
        'command': 'AT+MQTTCFG',
        'send_data': f'AT+MQTTCFG="cid",{connect_id},{cid}',
        'search_data': f'AT+MQTTCFG="cid",{connect_id}',
        'cid_range': {
            'default': [1, 15],
            'MN316/MN316A/MN326A/MN318/MN319/MN326/MR880A': [],  # 不支持该参数配置
            'ML307G/ML307H': [1, 5],
            'ML305U': [1, 7],
            'ML305M/ML307M/ML307N': [1, 8],
            'ML307X/ML307Y': [1, 15]
        },
        'not_supported_cid': ['MN316', 'MN316A', 'MN326A', 'MN318', 'MN319', 'MN326', 'MR880A'],
        'cid_type': ['ipv4', 'ipv6'],  # 参数类型为PDP类型
        'default_values': {
            'connect_id': 0,
            'cid': 1
        },
        'connect_id_range': {
            'default': [0, 5],
            'MN316A/MN326A/MN319': [0, 2]
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MQTTCFG: "cid",{cid}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mqttcfg_cid


def set_mqttcfg_ssl(connect_id=0, ssl_enable=0, ssl_id=0):
    if ssl_enable != "" and ssl_id != "":
        send_data = f'AT+MQTTCFG="ssl",{connect_id},{ssl_enable},{ssl_id}'
    elif ssl_enable == "":
        send_data = f'AT+MQTTCFG="ssl",{connect_id},,{ssl_id}'
    elif ssl_id == "":
        send_data = f'AT+MQTTCFG="ssl",{connect_id},{ssl_enable}'
    else:
        send_data = f'AT+MQTTCFG="ssl",{connect_id}'
    res_ssl_enable = 0 if ssl_enable == "" else ssl_enable
    res_ssl_id = 0 if ssl_id == "" else ssl_id
    mqttcfg_ssl = {
        'command': 'AT+MQTTCFG',
        'send_data': send_data,
        'search_data': f'AT+MQTTCFG="ssl",{connect_id}',
        'ssl_enable_range': [0, 1],  # 0: 普通TCP, 1: SSL TCP
        'ssl_id_range': [0, 5],  # 参考SSL手册，此处为示例
        'not_supported_ssl': ['MN316A', 'MN326A', 'MN318', 'MN319', 'ML307H-GU'],
        'default_values': {
            'connect_id': 0,
            'ssl_enable': 0,
            'ssl_id': 0
        },
        'connect_id_range': {
            'default': [0, 5],
            'MN316A/MN326A/MN319': [0, 2]
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MQTTCFG: "ssl",{res_ssl_enable},{res_ssl_id}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mqttcfg_ssl


def set_mqttcfg_keepalive(connect_id=0, keepalive_time=120):
    mqttcfg_keepalive = {
        'command': 'AT+MQTTCFG',
        'send_data': f'AT+MQTTCFG="keepalive",{connect_id},{keepalive_time}',
        'search_data': f'AT+MQTTCFG="keepalive",{connect_id}',
        'keepalive_range': [0, 65535],  # 0或60~65535
        'special_range': {
            '0': '标识不断开连接',
            '60-65535': '保洁时间'
        },
        'default_values': {
            'connect_id': 0,
            'keepalive_time': 120
        },
        'connect_id_range': {
            'default': [0, 5],
            'MN316A/MN326A/MN319': [0, 2]
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MQTTCFG: "keepalive",{keepalive_time}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mqttcfg_keepalive


def set_mqttcfg_clean(connect_id=0, clean_session=0):
    mqttcfg_clean = {
        'command': 'AT+MQTTCFG',
        'send_data': f'AT+MQTTCFG="clean",{connect_id},{clean_session}',
        'search_data': f'AT+MQTTCFG="clean",{connect_id}',
        'clean_session_range': [0, 1],  # 0: 恢复会话, 1: 新建会话
        'default_values': {
            'connect_id': 0,
            'clean_session': 0
        },
        'connect_id_range': {
            'default': [0, 5],
            'MN316A/MN326A/MN319': [0, 2]
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MQTTCFG: "clean",{clean_session}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mqttcfg_clean


def set_mqttcfg_retrans(connect_id=0, retrans_interval=20, retry_times=0):
    if retry_times != "" and retrans_interval != "":
        send_data = f'AT+MQTTCFG="retrans",{connect_id},{retrans_interval},{retry_times}'
    elif retrans_interval == "":
        send_data = f'AT+MQTTCFG="retrans",{connect_id},,{retry_times}'
    elif retry_times == "":
        send_data = f'AT+MQTTCFG="retrans",{connect_id},{retrans_interval}'
    else:
        send_data = f'AT+MQTTCFG="retrans",{connect_id}'
    res_retrans_interval = 20 if retrans_interval == "" else retrans_interval
    res_retry_times = 0 if retry_times == "" else retry_times
    mqttcfg_retrans = {
        'command': 'AT+MQTTCFG',
        'send_data': send_data,
        'search_data': f'AT+MQTTCFG="retrans",{connect_id}',
        'retrans_interval_range': [20, 60],
        'retry_times_range': [0, 3],
        'default_values': {
            'connect_id': 0,
            'retrans_interval': 20,
            'retry_times': 0
        },
        'connect_id_range': {
            'default': [0, 5],
            'MN316A/MN326A/MN319': [0, 2]
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MQTTCFG: "retrans",{res_retrans_interval},{res_retry_times}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mqttcfg_retrans


def set_mqttcfg_willoption(connect_id=0, will_flag=0, will_qos=0, will_retain=0):
    # 将所有参数转换为字符串，空值处理
    params = [
        connect_id,
        will_flag if will_flag != "" else None,
        will_qos if will_qos != "" else None,
        will_retain if will_retain != "" else None
    ]

    # 构建AT命令参数部分
    param_strs = []
    for param in params[1:]:  # 从第二个参数开始（will_flag）
        if param is not None:
            param_strs.append(str(param))
        else:
            param_strs.append("")  # 保留逗号位置

    # 生成AT命令
    send_data = f'AT+MQTTCFG="willoption",{connect_id}'
    if param_strs:
        send_data += "," + ",".join(param_strs)

    # 处理参数为空时的默认值
    res_will_flag = 0 if will_flag == "" else will_flag
    res_will_qos = 0 if will_qos == "" else will_qos
    res_will_retain = 0 if will_retain == "" else will_retain

    mqttcfg_willoption = {
        'command': 'AT+MQTTCFG',
        'send_data': send_data,
        'search_data': f'AT+MQTTCFG="willoption",{connect_id}',
        'will_flag_range': [0, 1],
        'will_qos_range': (0, 1, 2),
        'will_retain_range': [0, 1],
        'will_qos_range_all': {
            '0': '最多发送一次',
            '1': '最少发送一次',
            '2': '只发送一次'
        },
        'default_values': {
            'connect_id': 0,
            'will_flag': 0,
            'will_qos': 0,
            'will_retain': 0
        },
        'connect_id_range': {
            'default': [0, 5],
            'MN316A/MN326A/MN319': [0, 2],
            'ML302A/ML305A/ML307A/ML302S/ML307S/ML305U/ML307R/ML307C/ML305M/ML307G/MR880A/ML307H-DU/ML307M/ML307N/ML307X/ML307Y': [
                0, 5]
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MQTTCFG: "willoption",{res_will_flag},{res_will_qos},{res_will_retain}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mqttcfg_willoption


def set_mqttcfg_willpayload(connect_id=0, will_topic="", will_msg=""):
    if will_topic != "" and will_msg != "":
        send_data = f'AT+MQTTCFG="willpayload",{connect_id},"{will_topic}","{will_msg}"'
        urc_check = rf'\+MQTTCFG: "willpayload","{will_topic}","{will_msg}"'
    elif will_topic == "" and will_msg != "":
        send_data = f'AT+MQTTCFG="willpayload",{connect_id},,"{will_msg}"'
        urc_check = rf'\+MQTTCFG: "willpayload",,"{will_msg}"'
    elif will_topic != "" and will_msg == "":
        send_data = f'AT+MQTTCFG="willpayload",{connect_id},"{will_topic}"'
        urc_check = rf'\+MQTTCFG: "willpayload","{will_topic}",'
    else:
        send_data = f'AT+MQTTCFG="willpayload",{connect_id},"{will_topic}","{will_msg}"'
        urc_check = rf'\+MQTTCFG: "willpayload","{will_topic}","{will_msg}"'
    if will_msg == '""':
        send_data = f'AT+MQTTCFG="willpayload",{connect_id},"{will_topic}",""'
        urc_check = rf'\+MQTTCFG: "willpayload","{will_topic}",'
    # 处理参数为空时的默认值（用于search_result匹配）
    res_will_topic = "" if will_topic == "" else will_topic
    res_will_msg = "" if will_msg == "" else will_msg
    mqttcfg_willpayload = {
        'command': 'AT+MQTTCFG',
        'send_data': send_data,
        'search_data': f'AT+MQTTCFG="willpayload",{connect_id}',
        'will_topic_max': 256,
        'will_msg_max': 256,
        'default_values': {
            'connect_id': 0,
            'will_topic': "",
            'will_msg': ""
        },
        'connect_id_range': {
            'default': [0, 5],
            'MN316A/MN326A/MN319': [0, 2]
        },
        'result': [r'OK'],
        'search_result': [r'OK', urc_check],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mqttcfg_willpayload


def set_mqttcfg_pingreq(connect_id=0, ping_interval=120):
    mqttcfg_pingreq = {
        'command': 'AT+MQTTCFG',
        'send_data': f'AT+MQTTCFG="pingreq",{connect_id},{ping_interval}',
        'search_data': f'AT+MQTTCFG="pingreq",{connect_id}',
        'ping_interval_range': [60, 86400],
        'default_values': {
            'connect_id': 0,
            'ping_interval': 120
        },
        'connect_id_range': {
            'default': [0, 5],
            'MN316A/MN326A/MN319': [0, 2]
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MQTTCFG: "pingreq",{ping_interval}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mqttcfg_pingreq


def set_mqttcfg_pingresp(connect_id=0, pingack=0):
    mqttcfg_pingresp = {
        'command': 'AT+MQTTCFG',
        'send_data': f'AT+MQTTCFG="pingresp",{connect_id},{pingack}',
        'search_data': f'AT+MQTTCFG="pingresp",{connect_id}',
        'pingack_range': [0, 1],  # 0: 不显示, 1: 显示
        'default_values': {
            'connect_id': 0,
            'pingack': 0
        },
        'connect_id_range': {
            'default': [0, 5],
            'MN316A/MN326A/MN319': [0, 2]
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MQTTCFG: "pingresp",{pingack}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mqttcfg_pingresp


def set_mqttcfg_encoding(connect_id=0, input_format=0, output_format=0):
    # 处理空字符串参数的情况
    if input_format == "" and output_format == "":
        # 两者都为空时，只发送 input_format 部分（实际上这种情况可能需要特殊处理）
        send_data = f'AT+MQTTCFG="encoding",{connect_id},,'
    elif input_format == "":
        # input_format 为空，output_format 不为空
        send_data = f'AT+MQTTCFG="encoding",{connect_id},,{output_format}'
    elif output_format == "":
        # output_format 为空，input_format 不为空
        send_data = f'AT+MQTTCFG="encoding",{connect_id},{input_format},'
    else:
        # 两者都不为空
        send_data = f'AT+MQTTCFG="encoding",{connect_id},{input_format},{output_format}'
    res_input_format = 0 if input_format == "" else input_format
    res_output_format = 0 if output_format == "" else output_format
    mqttcfg_encoding = {
        'command': 'AT+MQTTCFG',
        'send_data':  send_data,    #f'AT+MQTTCFG="encoding",{connect_id},{input_format},{output_format}',
        'search_data': f'AT+MQTTCFG="encoding",{connect_id}',
        'input_format_range': (0, 1, 2),  # 0: ASCII, 1: HEX, 2: 转义字符串
        'output_format_range': (0, 1),  # 0: 原始字符串, 1: HEX
        'default_values': {
            'connect_id': 0,
            'input_format': 0,
            'output_format': 0
        },
        'connect_id_range': {
            'default': [0, 5],
            'MN316A/MN326A/MN319': [0, 2]
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MQTTCFG: "encoding",{res_input_format},{res_output_format}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mqttcfg_encoding


def set_mqttcfg_cached(connect_id=0, cached_mode=0):
    mqttcfg_cached = {
        'command': 'AT+MQTTCFG',
        'send_data': f'AT+MQTTCFG="cached",{connect_id},{cached_mode}',
        'search_data': f'AT+MQTTCFG="cached",{connect_id}',
        'cached_mode_range': [0, 1],  # 0: URC上报, 1: 缓存模式
        'not_supported_cached': ['MN316', 'MN316A', 'MN326A', 'MN318', 'MN319', 'MN326'],
        'default_values': {
            'connect_id': 0,
            'cached_mode': 0
        },
        'connect_id_range': {
            'default': [0, 5],
            'MN316A/MN326A/MN319': [0, 2]
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MQTTCFG: "cached",{cached_mode}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mqttcfg_cached


def set_mqttcfg_reconn(connect_id=0, reconn_times=3, reconn_interval=20, mode=0):
    # 将所有参数转换为字符串，空值处理
    params = [
        connect_id,
        reconn_times if reconn_times != "" else None,
        reconn_interval if reconn_interval != "" else None,
        mode if mode != "" else None
    ]

    # 构建AT命令参数部分
    param_strs = []
    for param in params[1:]:  # 从第二个参数开始（reconn_times）
        if param is not None:
            param_strs.append(str(param))
        else:
            param_strs.append("")  # 保留逗号位置

    # 生成AT命令
    send_data = f'AT+MQTTCFG="reconn",{connect_id}'
    if param_strs:
        send_data += "," + ",".join(param_strs)

    # 处理参数为空时的默认值
    res_reconn_times = 3 if reconn_times == "" else reconn_times
    res_reconn_interval = 20 if reconn_interval == "" else reconn_interval
    res_mode = 0 if mode == "" else mode

    mqttcfg_reconn = {
        'command': 'AT+MQTTCFG',
        'send_data': send_data,
        'search_data': f'AT+MQTTCFG="reconn",{connect_id}',
        'reconn_times_range': [0, 3],
        'reconn_interval_range': [20, 60],
        'mode_range': [0, 1],  # 0: 固定间隔, 1: 递增间隔
        'not_supported_mode': {
            'MR880A': [1]  # MR880A不支持mode=1
        },
        'default_values': {
            'connect_id': 0,
            'reconn_times': 3,
            'reconn_interval': 20,
            'mode': 0
        },
        'connect_id_range': {
            'default': [0, 5],
            'MN316A/MN326A/MN319': [0, 2]
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MQTTCFG: "reconn",{res_reconn_times},{res_reconn_interval},{res_mode}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mqttcfg_reconn


def set_mqttconn(connect_id=0, host='8.137.154.246', port=1883, clientid="", username="", password=""):
    if username and password:
        send_data = f'AT+MQTTCONN={connect_id},"{host}",{port},"{clientid}","{username}","{password}"'
    elif username and not password:
        send_data = f'AT+MQTTCONN={connect_id},"{host}",{port},"{clientid}","{username}"'
    elif password and not username:
        send_data = f'AT+MQTTCONN={connect_id},"{host}",{port},"{clientid}",,"{password}"'
    else:
        send_data = f'AT+MQTTCONN={connect_id},"{host}",{port},"{clientid}"'

    mqttconn = {
        'command': 'AT+MQTTCONN',
        'send_data': send_data,
        'host_name_type': ['域名', 'IP'],
        'host_max_len': 128,
        'clientid_max_len': 128,
        'username_max_len': 128,
        'password_max_len': 256,
        'port_range': [0, 65535],
        'connect_id_range': {
            'default': [0, 5],
            'MN316A/MN326A/MN319': [0, 2]
        },
        'default_values': {
            'port': 1883,
            'username': "",
            'password': ""
        },
        'recommendation': {
            'MN319': '建立MQTT连接时，建议使用指令AT+MLPMCFG锁定睡眠，否则进入深睡眠后连接将断开'
        },
        'result': [r'OK', rf'\+MQTTURC: "conn",{connect_id},0'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mqttconn


def set_mqttsub(connect_id=0, topics=[], qoss=[]):
    max_len = max(len(topics), len(qoss))
    result_parts = []
    search_parts = []
    qoss_str = []
    for i in range(max_len):
        topic = f'"{topics[i]}"' if i < len(topics) else ""
        qos = qoss[i] if i < len(qoss) else ""
        result_parts.append(str(topic))
        result_parts.append(str(qos))
        if topic != "" and qos != "":
            search_parts.append(str(topic))
            search_parts.append(str(qos))
            qoss_str.append(str(qos))

    sub_parts = ",".join(result_parts)
    search_parts = ",".join(search_parts)
    escaped_sub_parts = re.escape(search_parts)

    qoss_str = ','.join(qoss_str)
    mqttsub = {
        'command': 'AT+MQTTSUB',
        'send_data': f'AT+MQTTSUB={connect_id},{sub_parts}',
        'search_data': f'AT+MQTTSUB={connect_id}',
        'max_topics': 3,
        'topic_max': {
            'default': 256,
            'ML302A/ML305A/ML307A/ML302S/ML307S/ML307R/ML307C/ML305M/ML307G/ML307H/MR880A/ML307X/ML307Y/ML307M/ML307N': 256,
            'MN316A': 128
        },
        'qos_range': (0, 1, 2),
        'qos_range_all': {
            '0': '最多发送一次',
            '1': '最少发送一次',
            '2': '只发送一次'
        },
        'connect_id_range': {
            'default': [0, 5],
            'MN316A/MN326A/MN319': [0, 2]
        },
        'special_notes': {
            'MN319': 'AT指令参数的最大长度为1560字节',
            'MN316A/MN326A': '建议订阅的主题长度不超过3000字节',
            'ML307G': '同时订阅多个主题时，成功后分开响应，URC信息分开上报'
        },
        'result': [r'OK', rf'\+MQTTSUB: {connect_id},\d+',rf'\+MQTTURC: "suback",{connect_id},\d+,{qoss_str}'],
        'search_result': [r'OK', rf'\+MQTTSUB: {escaped_sub_parts}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mqttsub

def set_mqttunsub(connect_id=0, topics=[]):
    topic_str = ','.join([f'"{t}"' for t in topics])
    mqttunsub = {
        'command': 'AT+MQTTUNSUB',
        'send_data': f'AT+MQTTUNSUB={connect_id},{topic_str}',
        'max_topics': 3,
        'topic_max': {
            'default': 256,
            'ML302A/ML305A/ML307A/ML302S/ML307S/ML307R/ML307C/ML305M/ML307G/MR880A/ML307H/ML307M/ML307N': 256
        },
        'connect_id_range': {
            'default': [0, 5],
            'MN316A/MN326A/MN319': [0, 2]
        },
        'special_notes': {
            'MN319': 'AT指令参数的最大长度为1560字节',
            'ML307G': '同时取消订阅多个主题时，取消成功后分开响应，URC信息分开上报'
        },
        'result': [r'OK',rf'\+MQTTURC: "unsuback",{connect_id},\d+'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mqttunsub


def set_mqttpub(connect_id=0, topic="topic1", qos=0, retain=0, dup=0, msg_len=0, message=""):
    send_data = f'AT+MQTTPUB={connect_id},"{topic}",{qos},{retain},{dup},{msg_len},"{message}"'
    urc_check = rf'\+MQTTURC: "publish",{connect_id},\d+,"{re.escape(topic)}",\d+,\d+'
    mqttpub = {
        'command': 'AT+MQTTPUB',
        'send_data': send_data,
        'pub_type': ['data', 'transparent'],
        'qos_range': (0, 1, 2),
        'retain_range': [0, 1],
        'dup_range': [0, 1],
        'connect_id_range': {
            'default': [0, 5],
            'MN316A/MN326A/MN319': [0, 2]
        },
        'topic_max': {
            "128": ["MN316A"],
            "256": ["ML302A", "ML305A", "ML307A", "ML302S", "ML307S", "ML307R", "ML307C", "ML305M", "ML307G", "MR880A", "ML307M", "ML307N", "ML307H"]
        },
        'msg_max': {
            "range_0_1024": ["ML302A", "ML305A", "ML307A", "ML302S", "ML307S", "ML307F", "ML307C", "ML305M", "ML307G", "ML307M", "ML307N", "ML307H"],
            "range_0_2048": ["MR880A", "ML307X", "ML307Y"],
            "range_0_8192": ["MR880A"],  # 数据模式下
            "range_0_4000": ["ML307X", "ML307Y"]  # 数据模式下
        },
        'not_supported_data_mode': ["MN316", "MN316-S", "MN316A", "MN326A", "MN318", "MN319", "MN326"],
        'special_notes': {
            'MN319': 'AT指令参数的最大长度为1560字节',
            'ML307X/ML307Y': '在数据模式下，输入数据达到指定长度或超过10s时自动发送数据',
            'MR880A': '在数据模式下，输入数据达到指定长度或超过10s后自动发送数据，<msg_len>设置为0时，输入Ctrl+z也将发送数据'
        },
        'default_values': {
            'qos': 0,
            'retain': 0,
            'dup': 0,
            'msg_len': 0,
            'message': ""
        },
        'result': [r'OK', rf'\+MQTTPUB: {connect_id},\d+,\d+',urc_check],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    if qos == 1:
        mqttpub['result'].append(rf'\+MQTTURC: "puback",{connect_id},\d+,0')
    elif qos == 2:
        mqttpub['result'].append(rf'\+MQTTURC: "pubrec",{connect_id},\d+,0')
        mqttpub['result'].append(rf'\+MQTTURC: "pubcomp",{connect_id},\d+,0')
    return mqttpub


def set_mqttstate(connect_id=0):
    mqttstate = {
        'command': 'AT+MQTTSTATE',
        'send_data': f'AT+MQTTSTATE={connect_id}',
        'connect_id_range': {
            'default': [0, 5],
            'MN316A/MN326A/MN319': [0, 2]
        },
        'result': [r'OK', r'\+MQTTSTATE: [1-4]'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mqttstate


def set_mqttdisc(connect_id=0):
    mqttdisc = {
        'command': 'AT+MQTTDISC',
        'send_data': f'AT+MQTTDISC={connect_id}',
        'connect_id_range': {
            'default': [0, 5],
            'MN316A/MN326A/MN319': [0, 2]
        },
        'result': [r'OK', rf'\+MQTTURC: "conn",{connect_id},2'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mqttdisc


def set_mqttread(connect_id, count=1):
    mqttread = {
        'command': 'AT+MQTTREAD',
        'send_data': f'AT+MQTTREAD={connect_id},{count}', #数据发送指令
        'search_data': f'AT+MQTTREAD={connect_id}', #查询指令
        'connect_id_range': {
            'default': [0, 5],
            'MN316A/MN326A/MN319': [0, 2]
        },
        'not_supported': ["NB-loT模组"],  # NB-loT模组暂不支持该命令
        'cache_limit': {
            'NB-loT': '4KB',
            '4G/5G': '8KB'
        },
        'result': [r'OK', r'\+MQTTREAD:'], #发送指令对应的结果校验
        'search_result': [r'OK', rf'\+MQTTREAD: {connect_id},\d+,\d+'],#查询指令对应的结果校验
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+'] #异常用例对应的结果校验
    }
    return mqttread