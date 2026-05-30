import re

def set_cgdcont_data(cid_id=1, pdp_type='IPV4V6', apn='cmnet.mnc002.mcc460.gprs'):
    cgdcont_data = {'command': 'AT+CGDCONT',
                    'send_data': f'AT+CGDCONT={cid_id},{pdp_type},{apn}',
                    'result': [rf'OK'],
                    'err_result':[r'\+CME ERROR: [0-9A-Za-z]+']}
    return cgdcont_data

def set_mipcall_data(op=1, cid=1):
    mipcall_data = {'command': 'AT+MIPCALL',
                    'send_data': f'AT+MIPCALL={op},{cid}',
                    'result': [rf'OK'],
                    'err_result':[r'\+CME ERROR: [0-9A-Za-z]+']}
    return mipcall_data

def set_mhttpcfg_header(httpid=0, header="", header_len=0):
    """
    AT+MHTTPCFG="header" 通用报头设置
    """
    mhttpcfg_header = {
        'command': 'AT+MHTTPCFG',
        # 'send_data': f'AT+MHTTPCFG="header",{httpid},"{header}"' if header else f'AT+MHTTPCFG="header",{httpid}',
        'send_data': f'AT+MHTTPCFG="header",{httpid},"{header}"',
        'search_data': f'AT+MHTTPCFG="header",{httpid}',
        'search_result': [r'OK', rf'\+MHTTPCFG: "header",{httpid},{len(header)+2},{header}'] if header else [r'OK', rf'\+MHTTPCFG: "header",{httpid},\d+,[^"]*'],
        # 'search_result': [r'OK',rf'\+MHTTPCFG: "header",{httpid},{len(header)},(\"{re.escape(header)}\"|{re.escape(header)})'] if header else [r'OK', rf'\+MHTTPCFG: "header",{httpid},\d+,[^"]*'],
        'httpid_range': {
            'default': [0, 3],
            'MN319/MN316A/MN326A': [0, 1]
        },
        'header_len_range': {
            'default': [1, 1024],

        },
        'default_values': {
            'httpid': 0,
            'header': ""
        },
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mhttpcfg_header

def set_mhttpcfg_chunked(httpid=0, chunked_mode=0):
    """
    AT+MHTTPCFG="chunked" 传输模式设置
    """
    mhttpcfg_chunked = {
        'command': 'AT+MHTTPCFG',
        'send_data': f'AT+MHTTPCFG="chunked",{httpid},{chunked_mode}',
        'search_data': f'AT+MHTTPCFG="chunked",{httpid}',
        'search_result': [r'OK', rf'\+MHTTPCFG: "chunked",{httpid},{chunked_mode}'],
        'httpid_range': {
            'default': [0, 3],
            'MN319/MN316A/MN326A': [0, 1]
        },
        'chunked_mode_range': (0, 1),
        'chunked_mode_desc': {
            '0': 'content_length模式',
            '1': 'chunked模式'
        },
        'default_values': {
            'httpid': 0,
            'chunked_mode': 0
        },
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mhttpcfg_chunked


def set_mhttpcfg_cached(httpid=0, cached=0, cache_length=4096):
    """
    AT+MHTTPCFG="cached" 缓存模式设置
    """
    # 修复：更精确地判断cache_length是否为空值
    if cache_length is not None and cache_length != "" and str(cache_length).lower() != "nan" :
        cache_length = int(float(cache_length))  # 转换为整数,取值时4096会变成4096.0
        send_data = f'AT+MHTTPCFG="cached",{httpid},{cached},{cache_length}'
        if cached == 1:
           search_result = [r'OK', rf'\+MHTTPCFG: "cached",{httpid},{cached},{cache_length}']
        else:
            search_result = [r'OK', rf'\+MHTTPCFG: "cached",{httpid},{cached}']

    else:
        send_data = f'AT+MHTTPCFG="cached",{httpid},{cached}'
        search_result = [r'OK', rf'\+MHTTPCFG: "cached",{httpid},{cached}']
    # search_result = [r'OK', rf'\+MHTTPCFG: "cached",{httpid},{cached},{cache_length}']
    mhttpcfg_cached = {
        'command': 'AT+MHTTPCFG',
        'send_data': send_data,
        'search_data': f'AT+MHTTPCFG="cached",{httpid}',
        'search_result': search_result,
        'httpid_range': {
            'default': [0, 3],
            'MN319/MN316A/MN326A': [0, 1]
        },
        'cached_range': (0, 1),
        'cached_desc': {
            '0': '非缓存模式',
            '1': '缓存模式'
        },
        'cache_length_range': {
            'default': [1, 8192],
            'MN316A/MN326A': [1, 4096]
        },
        'default_values': {
            'httpid': 0,
            'cached': 0,
            'cache_length': 4096
        },
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mhttpcfg_cached


def set_mhttpcfg_timeout(httpid=0, conn_timeout=60, rsp_timeout=0, input_timeout=10):
    """
    AT+MHTTPCFG="timeout" 超时时间设置
    """
    # 构建参数列表，按照AT命令语法处理参数缺省
    # httpid总是存在的
    params = [f'"timeout"', str(httpid)]

    # 检查参数是否需要包含在命令中，从最后一个参数往前检查
    # 如果input_timeout不是空值或None，所有参数都要包含
    if input_timeout != "" and input_timeout is not None and input_timeout != "warning":
        params.extend([str(conn_timeout), str(rsp_timeout), str(input_timeout)])
    elif rsp_timeout != "" and rsp_timeout is not None:
        # 如果rsp_timeout不是空值或None，但input_timeout是空值或None
        params.extend([str(conn_timeout), str(rsp_timeout)])
    elif conn_timeout != "" and conn_timeout is not None:
        # 如果conn_timeout不是空值或None，但rsp_timeout和input_timeout都是空值或None
        params.append(str(conn_timeout))
    # 如果所有参数都是默认值或空值，则只包含必要的参数

    send_data = f'AT+MHTTPCFG={",".join(params)}'

    # 构建查询结果，需要根据实际发送的参数来确定
    conn_timeout_1 = conn_timeout
    if conn_timeout == "":
        conn_timeout_1 = 60
    rsp_timeout_1 = rsp_timeout
    if rsp_timeout == "":
        rsp_timeout_1 = 0
    input_timeout_1 = input_timeout
    if input_timeout == "":
        input_timeout_1 = 10


    mhttpcfg_timeout = {
        'command': 'AT+MHTTPCFG',
        'send_data': send_data,
        'search_data': f'AT+MHTTPCFG="timeout",{httpid}',
        'search_result': [r'OK', rf'\+MHTTPCFG: "timeout",{httpid},{conn_timeout_1},{rsp_timeout_1},{input_timeout_1}'] if input_timeout != "warning"  else [r'OK', rf'\+MHTTPCFG: "timeout",{httpid},{conn_timeout_1},{rsp_timeout_1}'],
        'httpid_range': {
            'default': [0, 3],
            'MN319/MN316A/MN326A': [0, 1]
        },
        'conn_timeout_range': [0, 180],
        'rsp_timeout_range': [0, 60],
        'input_timeout_range': {
            'default': [0, 180],
            'ML302A/ML307A/ML305A/ML307C/ML305M/ML307R/ML307G/ML307M/ML307H/ML307N/ML307X/ML307Y': [1, 120]
        },
        'not_supported_input_timeout': ['MN318', 'MN316', 'MN319', 'MN326', 'MN316A', 'MN326A'],
        'default_values': {
            'httpid': 0,
            'conn_timeout': 60,
            'rsp_timeout': 0,
            'input_timeout': 10
        },
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mhttpcfg_timeout



def set_mhttpcfg_encoding(httpid=0, input_format=0, output_format=0):
    """
    AT+MHTTPCFG="encoding" 输入输出编码设置
    """
    input_format_1 = input_format
    if input_format == "":
        input_format_1 = 0
    mhttpcfg_encoding = {
        'command': 'AT+MHTTPCFG',
        'send_data': f'AT+MHTTPCFG="encoding",{httpid},{input_format},{output_format}',
        'search_data': f'AT+MHTTPCFG="encoding",{httpid}',
        'search_result': [r'OK', rf'\+MHTTPCFG: "encoding",{httpid},{input_format_1},{output_format}'],
        'httpid_range': {
            'default': [0, 3],
            'MN319/MN316A/MN326A': [0, 1]
        },
        'input_format_range': (0, 1, 2),
        'input_format_desc': {
            '0': 'ASCII字符串（原始数据）',
            '1': 'HEX字符串',
            '2': '带转义的字符串'
        },
        'output_format_range': (0, 1),
        'output_format_desc': {
            '0': 'ASCII字符串（原始数据）',
            '1': 'HEX字符串'
        },
        'not_supported_output_format': ['MR880A'],
        'default_values': {
            'httpid': 0,
            'input_format': 0,
            'output_format': 0
        },
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mhttpcfg_encoding

def set_mhttpcfg_ssl(httpid=0, ssl_enable=0, ssl_id=""):
    """
    AT+MHTTPCFG="ssl" SSL模式设置
    """
    mhttpcfg_ssl = {
        'command': 'AT+MHTTPCFG',
        'send_data': f'AT+MHTTPCFG="ssl",{httpid},{ssl_enable},{ssl_id}' if ssl_id else f'AT+MHTTPCFG="ssl",{httpid},{ssl_enable}',
        'search_data': f'AT+MHTTPCFG="ssl",{httpid}',
        'search_result': [r'OK', rf'\+MHTTPCFG: "ssl",{httpid},{ssl_enable},{ssl_id}' if ssl_id else rf'\+MHTTPCFG: "ssl",{httpid},{ssl_enable}'],
        'httpid_range': {
            'default': [0, 3],
            'MN319/MN316A/MN326A': [0, 1]
        },
        'ssl_enable_range': (0, 1),
        'ssl_enable_desc': {
            '0': '不使用SSL（普通连接，HTTP）',
            '1': '使用SSL（安全连接，HTTPS）'
        },
        'ssl_id_range': {
            'default': [0, 5],

        },
        'not_supported_ssl': ['MN318', 'ML307H-GU', 'MN319', 'MN316A', 'MN326A'],
        'default_values': {
            'httpid': 0,
            'ssl_enable': 0,
            'ssl_id': ""
        },
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mhttpcfg_ssl

def set_mhttpcfg_cid(httpid=0, cid=""):
    """
    AT+MHTTPCFG="cid" PDP上下文设置
    """
    mhttpcfg_cid = {
        'command': 'AT+MHTTPCFG',
        'send_data': f'AT+MHTTPCFG="cid",{httpid},{cid}' if cid != "" else f'AT+MHTTPCFG="cid",{httpid}',
        'search_data': f'AT+MHTTPCFG="cid",{httpid}',
        'search_result': [r'OK', rf'\+MHTTPCFG: "cid",{httpid},{cid}' if cid != "" else rf'\+MHTTPCFG: "cid",{httpid}'],
        'httpid_range': {
            'default': [0, 3],
            'MN319/MN316A/MN326A': [0, 1]
        },
        'cid_range': {
            'default': [1, 15],
            'ML302S/ML307S': [1, 1],   #待定
            'ML305U': [1, 7],
            'MR880A': [7, 7]
        },
        'not_supported_cid': ['MN316', 'MN319', 'MN326', 'MN316A', 'MN326A'],
        'cid_type': ['ipv4', 'ipv6'],
        'default_values': {
            'httpid': 0,
            'cid': ""
        },
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mhttpcfg_cid



def set_mhttpcfg_fragment(httpid=0, frag_size=None, interval=None):
    """
    AT+MHTTPCFG="fragment" 数据输出流控设置
    """
    re_frag_size = 0 if frag_size == '' else frag_size
    re_interval = 0 if interval == '' else interval

    mhttpcfg_fragment = {
        'command': 'AT+MHTTPCFG',
        'send_data': f'AT+MHTTPCFG="fragment",{httpid},{frag_size},{interval}',
        'search_data': f'AT+MHTTPCFG="fragment",{httpid}',
        'search_result': [r'OK', rf'\+MHTTPCFG: "fragment",{httpid},{re_frag_size},{re_interval}'],
        'httpid_range': {
            'default': [0, 3],
            'MN319/MN316A/MN326A': [0, 1]
        },
        'frag_size_range': [0, 1024],
        'interval_range': [0, 2000],
        'default_values': {
            'httpid': 0,
            'frag_size': 0,
            'interval': 0
        },
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mhttpcfg_fragment



def set_mhttpcfg_urlencode(httpid=0, urlencode_mode=0):
    """
    AT+MHTTPCFG="urlencode" URL编码设置
    """
    mhttpcfg_urlencode = {
        'command': 'AT+MHTTPCFG',
        'send_data': f'AT+MHTTPCFG="urlencode",{httpid},{urlencode_mode}',
        'search_data': f'AT+MHTTPCFG="urlencode",{httpid}',
        'search_result': [r'OK', rf'\+MHTTPCFG: "urlencode",{httpid},{urlencode_mode}'],
        'httpid_range': {
            'default': [0, 3],
            'MN319/MN316A/MN326A': [0, 1]
        },
        'urlencode_mode_range': (0, 1),
        'urlencode_mode_desc': {
            '0': '不编码',
            '1': '编码（不对字母数字以及__!->{//?@&=+$#进行编码）'
        },
        'default_values': {
            'httpid': 0,
            'urlencode_mode': 0
        },
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mhttpcfg_urlencode

def set_mhttpcreate(host=""):
    """
    AT+MHTTPCREATE 创建HTTP实例
    """
    mhttpcreate = {
        'command': 'AT+MHTTPCREATE',
        # 'send_data': f'AT+MHTTPCREATE="{host}"' if host else 'AT+MHTTPCREATE',
        'send_data': f'AT+MHTTPCREATE="{host}"',
        'search_data': '',  # 创建命令没有查询功能
        'search_result': [],
        'host_type': ['域名', 'IP'],
        'host_format': 'http://domain.com 或 http://domain.com:80 或 http://192.168.1.1',
        'httpid_range': {
            'default': [0, 3],
            'MN319/MN316A/MN326A': [0, 1]
        },
        'default_values': {
            'host': ""
        },
        'result': [r'OK', rf'\+MHTTPCREATE: [0-3]'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mhttpcreate


def set_mhttpheader(httpid=0, eof=0, length=0, header=""):
    """
        AT+MHTTPHEADER 设置HTTP特定报头
        AT+MHTTPHEADER=<httpid>,<eof>[,<length>[,<header>]]
        """
    # 构建参数列表，按照AT命令语法处理参数缺省
    # httpid和eof总是存在的
    params = [str(httpid), str(eof)]

    # 检查length是否需要包含
    # 如果length为空或为缺省值，但header不为空，则需要添加空的length占位符
    if length != "" and length is not None:
        # length不为空，添加length
        params.append(str(length))
        # 如果header也不为空，则添加header
        if header != "" and header is not None:
            params.append(f'"{header}"')
    elif header != "" and header is not None:
        # length为空但header不为空，需要添加空的length占位符
        params.append("")  # 添加空的length占位符
        params.append(f'"{header}"')

    send_data = f'AT+MHTTPHEADER={",".join(params)}'

    mhttpheader = {
        'command': 'AT+MHTTPHEADER',
        'send_data': send_data,
        'search_data': f'AT+MHTTPHEADER={httpid}',
        'search_result': [r'OK', rf'\+MHTTPHEADER: {httpid},{len(header) + 2},{re.escape(header)}'],
        'httpid_range': {
            'default': [0, 3],
            'MN319/MN316A/MN326A': [0, 1]
        },
        'eof_range': (0, 1, 2),
        'eof_desc': {
            '0': 'header输入结束标记',
            '1': '后续还有header数据输入',
            '2': '清空已有header内容'
        },
        'length_range': {
            'default': [0, 4096],
            'ML302A/ML305A/ML307A/ML307C/ML307R/ML307G': '命令模式[0,1024],数据模式[0,4096]',
        },
        'header_max_length': {
            'default': 1560,
            'MN319': 1560,
            'ML307X/ML307Y': 8192
        },
        'not_supported_data_mode': ['MN318', 'MN316', 'MN319', 'MN326', 'MN316A', 'MN326A'],
        'quote_restriction': '字符串参数内部不能包含引号，如需引号需使用数据模式',
        'default_values': {
            'httpid': 0,
            'eof': 0,
            'length': 0,
            'header': ""
        },
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mhttpheader





def set_mhttpcontent(httpid=0, eof=0, length=0, data=""):
    """
    AT+MHTTPCONTENT 设置HTTP CONTENT数据
    AT+MHTTPCONTENT=<httpid>,<eof>[,<length>[,<data>]]
    """
    # 构建参数列表，按照AT命令语法处理参数缺省
    # httpid和eof总是存在的
    params = [str(httpid), str(eof)]

    # 检查length是否需要包含
    # 如果length为空或为缺省值，但data不为空，则需要添加空的length占位符
    if length != "" and length is not None:
        # length不为空，添加length
        params.append(str(length))
        # 如果data也不为空，则添加data
        if data != "" and data is not None:
            params.append(f'{data}')
    elif data != "" and data is not None:
        # length为空但data不为空，需要添加空的length占位符
        params.append("")  # 添加空的length占位符
        params.append(f'{data}')

    send_data = f'AT+MHTTPCONTENT={",".join(params)}'

    mhttpcontent = {
        'command': 'AT+MHTTPCONTENT',
        'send_data': send_data,
        'search_data': f'AT+MHTTPCONTENT={httpid}',
        'search_result': [r'OK', rf'\+MHTTPCONTENT: {httpid},{len(data)-2},{data[1:-1]}'] if eof != 2 else [r'OK'],
        'httpid_range': {
            'default': [0, 3],
            'MN319/MN316A/MN326A': [0, 1]
        },
        'eof_range': (0, 1, 2),
        'eof_desc': {
            '0': 'content输入结束标记',
            '1': '后续还有content数据输入',
            '2': '清空已有content内容（只对非Chunked模式有效）'
        },
        'length_range': {
            'default': [0, 4096],
            'ML307G': '总长度3×4096字节'
        },
        'data_max_length': {
            'default': 1560,
            'ML307X/ML307Y': 8192
        },
        'not_supported_data_mode': ['MN318', 'MN316', 'MN319', 'MN326', 'MN316A', 'MN326A'],
        'quote_restriction': '字符串参数内部不能包含引号，如需引号需使用数据模式',
        'default_values': {
            'httpid': 0,
            'eof': 0,
            'length': 0,
            'data': ""
        },
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mhttpcontent
def set_mhttprequest(httpid=0, method=1, length=0, path="", local_path=""):
    """
    AT+MHTTPREQUEST 发送HTTP请求
    AT+MHTTPREQUEST=<httpid>,<method>[,<length>[,<path>[,<local_path>]]]
    """
    # 构建参数列表，按照AT命令语法处理参数缺省
    # httpid和method总是存在的
    params = [str(httpid), str(method)]

    # 检查是否需要添加后面的参数
    # 从最后一个参数开始向前检查，如果都是空值则不添加
    if local_path != "" and local_path is not None:
        # local_path不为空，所有参数都需要包含
        params.extend([str(length), f'"{path}"', f'"{local_path}"'])
    elif path != "" and path is not None:
        # path不为空但local_path为空，添加length和path
        params.extend([str(length), f'"{path}"'])
    elif length != "" and length is not None and (int(length) != 0 or str(length) != "0"):
        # length不为0（或非空），但path和local_path都为空，只添加length
        params.append(str(length))
    # 如果length为0（默认值）且path和local_path都为空，则不添加这些参数

    send_data = f'AT+MHTTPREQUEST={",".join(params)}'


    mhttprequest = {
        'command': 'AT+MHTTPREQUEST',
        'send_data': send_data,
        # 'send_data': f'AT+MHTTPREQUEST={httpid},{method},{length},"{path}"' if path and not local_path else f'AT+MHTTPREQUEST={httpid},{method},{length},"{path}","{local_path}"' if local_path else f'AT+MHTTPREQUEST={httpid},{method},{length}',
        'search_data': '',  # 发送请求命令没有查询功能
        'search_result': [],
        'httpid_range': {
            'default': [0, 3],
            'MN319/MN316A/MN326A': [0, 1]
        },
        'method_range': (1, 2, 3, 4, 5),
        'method_desc': {
            '1': 'GET',
            '2': 'POST',
            '3': 'PUT',
            '4': 'DELETE',
            '5': 'HEAD'
        },
        'length_range': {
            'default': [0, 4096],
        },
        'path_max_length': {
            'default': 1560,
        },
        'local_path_handling': {
            'ML302S/ML307S/ML302A/ML305A/ML307A/ML307G/ML307R/ML307C': '第一位为/则存储用户路径，否则存储/etc/http_file/',
            'ML305U/ML305M/ML307X/ML307Y': '仅含/则存储用户路径，含\\或无斜杠则存储/etc/http_file/',
            'ML307M/ML307H/ML307N': '不支持local_path参数'
        },
        'not_supported_data_mode': ['MN318', 'MN316', 'MN319', 'MN326', 'MN316A', 'MN326A'],
        'redirect_ssl_note': 'HTTP重定向到HTTPS时，若未使能SSL则默认使能SSL并采用默认配置',
        'default_values': {
            'httpid': 0,
            'method': 1,
            'length': 0,
            'path': "",
            'local_path': ""
        },
        'result': [r'OK', rf'\+MHTTPURC: "header",{httpid},\d+,\d+', rf'\+MHTTPURC: "content",{httpid},\d+,\d+,\d+'],
        'cache_result': [r'OK', rf'\+MHTTPURC: "recv",{httpid},\d+,\d+,\d+'],   #人为补充
        'chunk_result': [r'OK', rf'\+MHTTPURC: "ind",{httpid}'],   #人为补充
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mhttprequest


def set_mhttpread(httpid=0, type=0, read_len=0):
    """
    AT+MHTTPREAD 读取HTTP数据
    """
    mhttpread = {
        'command': 'AT+MHTTPREAD',
        'send_data': f'AT+MHTTPREAD={httpid},{type},{read_len}',
        'search_data': f'AT+MHTTPREAD={httpid},{type}',
        'search_result': [r'OK', rf'\+MHTTPREAD: {httpid},{type},0'] if read_len == 0 else [r'OK', rf'\+MHTTPREAD: {httpid},{type},\d+'],
        'httpid_range': {
            'default': [0, 3],
            'MN319/MN316A/MN326A': [0, 1]
        },
        'type_range': (0, 1),
        'type_desc': {
            '0': 'header数据',
            '1': 'content数据'
        },
        'read_len_range': [0, 65535],
        'read_len_desc': {
            '0': '读取全部缓存数据'
        },
        'cache_space_note': 'ML307G/ML307N：内容大于缓存空间则报缓存空间不足',
        'default_values': {
            'httpid': 0,
            'type': 0,
            'read_len': 0
        },
        'result': [r'OK', rf'\+MHTTPREAD: \d+,\d+,\d+,\d+,\s*\S+'],  #不允许内容为空
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mhttpread

def set_mhttpdel(httpid=0):
    """
    AT+MHTTPDEL 删除HTTP实例
    """
    mhttpdel = {
        'command': 'AT+MHTTPDEL',
        'send_data': f'AT+MHTTPDEL={httpid}',
        'search_data': '',  # 删除命令没有查询功能
        'search_result': [],
        'httpid_range': {
            'default': [0, 3],
            'MN319/MN316A/MN326A': [0, 1]
        },
        'default_values': {
            'httpid': 0
        },
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mhttpdel

def set_mhttpterm(httpid=""):
    """
    AT+MHTTPTERM 终止HTTP传输
    """
    mhttpterm = {
        'command': 'AT+MHTTPTERM',
        'send_data': f'AT+MHTTPTERM={httpid}' if httpid else 'AT+MHTTPTERM',
        'search_data': '',  # 终止命令没有查询功能
        'search_result': [],
        'httpid_range': {
            'default': [0, 3],
            'MN319/MN316A/MN326A': [0, 1]
        },
        'command_type_desc': {
            'exec': 'AT+MHTTPTERM（终止所有连接）',
            'set': 'AT+MHTTPTERM=<httpid>（终止指定连接）'
        },
        'default_values': {
            'httpid': ""
        },
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mhttpterm



def set_mhttpdlfile(url="", local_path="", progind="", range="", eof="", ssl_id=""):
    """
    AT+MHTTPDLFILE HTTP下载文件
    AT+MHTTPDLFILE=<url>,<local_path>[,<progind>[,<range>[,<eof>[,<ssl_id>]]]]
    """
    # 构建参数列表，按照AT命令语法处理参数缺省
    # url和local_path总是存在的

    # 确定最多有多少个参数需要包含在命令中
    # 从最后一个参数往前检查，如果为空则不包含
    params = [f'{url}', f'"{local_path}"']

    # 检查是否有任何可选参数需要包含
    # 从最后一个参数往前检查，如果为空则不添加
    if ssl_id != "":
        # 如果ssl_id不为空，所有参数都要包含
        params.extend([
            str(progind) if progind != "" else "",
            f'"{range}"' if range != "" else "",
            str(eof) if eof != "" else "",
            str(ssl_id)
        ])
    elif eof != "":
        # 如果eof不为空，但ssl_id为空
        params.extend([
            str(progind) if progind != "" else "",
            f'"{range}"' if range != "" else "",
            str(eof)
        ])
    elif range != "":
        # 如果range不为空，但eof和ssl_id都为空
        params.extend([
            str(progind) if progind != "" else "",
            f'"{range}"'
        ])
    elif progind != "":
        # 如果progind不为空，但range、eof和ssl_id都为空
        params.append(str(progind))

    send_data = f'AT+MHTTPDLFILE={",".join(params)}'

    mhttpdlfile = {
        'command': 'AT+MHTTPDLFILE',
        'send_data': send_data,
        'search_data': '',  # 下载命令没有查询功能
        'search_result': [],
        'url_format': 'http://example.com/abc.txt 或 http://example.com:8080/abc.txt',
        'url_protocol_default': {
            'ML307G': '默认https'
        },
        'local_path_handling': {
            'ML302S/ML307S/ML302A/ML305A/ML307A/ML307G/ML307R/ML307C': '第一位为/则存储用户路径，否则存储/etc/http_file/',
            'ML305U/ML305M/ML307X/ML307Y': '仅含/则存储用户路径，含\\或无斜杠则存储/etc/http_file/'
        },
        'progind_range': [0, 65535],
        'progind_desc': {
            '0': '不上报中间进度，只上报最后结果'
        },
        'range_format': 'bytes=500-900',
        'eof_range': (0, 1),
        'eof_desc': {
            '0': '覆盖方式写入',
            '1': '追加方式写入（断点续传）'
        },
        'ssl_id_range': {
            'default': [0, 5],
        },
        'not_supported_models': ['MN318', 'MN316', 'MN319', 'MN326', 'MN316A', 'MN326A', 'ML307M', 'ML307H', 'ML307N'],
        'default_values': {
            'url': "",
            'local_path': "",
            'progind': 0,
            'range': "",
            'eof': 0,
            'ssl_id': ""
        },
        'result': [r'OK', r'\+MHTTPURC: "header",\d+,\d+,\d+', r'\+MHTTPDLFILE: \d+,\d+,\d+'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mhttpdlfile
