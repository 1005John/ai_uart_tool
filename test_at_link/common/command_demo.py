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

def set_mqttcfg_encoding(connect_id=0, input_format=0, output_format=0):
    mqttcfg_encoding = {
        'command': 'AT+MQTTCFG',
        'send_data': f'AT+MQTTCFG="encoding",{connect_id},{input_format},{output_format}',
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
        'search_result': [r'OK', rf'\+MQTTCFG: "encoding",{input_format},{output_format}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mqttcfg_encoding


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

    for i in range(max_len):
        topic = topics[i] if i < len(topics) else ""
        qos = qoss[i] if i < len(qoss) else ""
        result_parts.append(str(topic))
        result_parts.append(str(qos))

    sub_parts = ",".join(result_parts)

    qoss_str = ','.join([str(x) for x in qoss])
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
        'search_result': [r'OK', rf'\+MQTTSUB:{sub_parts}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mqttsub
def set_mqttpub(connect_id=0, topic="topic1", qos=0, retain=0, dup=0, msg_len=0, message=""):
    send_data = f'AT+MQTTPUB={connect_id},"{topic}",{qos},{retain},{dup},{msg_len},"{message}"'
    urc_check = rf'\+MQTTURC: "publish",{connect_id},\d+,"{topic}",\d+,\d+'
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
