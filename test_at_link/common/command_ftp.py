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

def set_mftpcfg_datatype(connect_id=0, data_trans_type=0):
    """
    配置FTP数据传输类型
    """
    mftpcfg_data_type = {
        'command': 'AT+MFTPCFG',
        'send_data': f'AT+MFTPCFG={connect_id},"data_type",{data_trans_type}',
        'search_data': f'AT+MFTPCFG={connect_id},"data_type"',
        'data_trans_type_range': {
            'default': [0, 1]
        },
        'data_trans_type_values': {
            0: 'Binary',
            1: 'ASCII'
        },
        'default_values': {
            'connect_id': 0,
            'data_trans_type': 0
        },
        'connect_id_range': {
            'default': [0, 5]
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MFTPCFG: {connect_id},"data_type",{data_trans_type}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mftpcfg_data_type


def set_mftpcfg_transmode(connect_id=0, trans_mode=1):
    """
    配置FTP传输模式
    """
    mftpcfg_transmode = {
        'command': 'AT+MFTPCFG',
        'send_data': f'AT+MFTPCFG={connect_id},"transmode",{trans_mode}',
        'search_data': f'AT+MFTPCFG={connect_id},"transmode"',
        'trans_mode_range': {
            'default': [0, 1]
        },
        'trans_mode_values': {
            0: '主动模式',
            1: '被动模式'
        },
        'special_notes': {
            'ML302A/ML305A/ML307A/ML305U/ML307R/MR880A/ML307N/ML307X/ML307C': '只支持被动模式'
        },
        'default_values': {
            'connect_id': 0,
            'trans_mode': 1
        },
        'connect_id_range': {
            'default': [0, 5]
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MFTPCFG: {connect_id},"transmode",{trans_mode}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mftpcfg_transmode


def set_mftpcfg_rsptimeout(connect_id=0, timeout=10):
    """
    配置FTP命令超时响应时间
    """
    mftpcfg_rsptimeout = {
        'command': 'AT+MFTPCFG',
        'send_data': f'AT+MFTPCFG={connect_id},"rsptimeout",{timeout}',
        'search_data': f'AT+MFTPCFG={connect_id},"rsptimeout"',
        'timeout_range': {
            'default': [2, 30]
        },
        'default_values': {
            'connect_id': 0,
            'timeout': 10
        },
        'connect_id_range': {
            'default': [0, 5]
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MFTPCFG: {connect_id},"rsptimeout",{timeout}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mftpcfg_rsptimeout


def set_mftpcfg_ssl(connect_id=0, ssl_mode=0, ssl_id=0):
    """
    配置FTP SSL相关配置
    """
    mftpcfg_ssl = {
        'command': 'AT+MFTPCFG',
        'send_data': f'AT+MFTPCFG={connect_id},"ssl",{ssl_mode},{ssl_id}',
        'search_data': f'AT+MFTPCFG={connect_id},"ssl"',
        'ssl_mode_range': {
            'default': [0, 2]
        },
        'ssl_mode_values': {
            0: '通用FTP',
            1: '隐式FTPS',
            2: '显式FTPS'
        },
        'ssl_id_range': {
            'default': [0, 5]
        },
        'special_notes': {
            'ML302A/ML305A/ML307A/ML305U/ML307R/MR880A/ML307N/ML307X/ML307C': '只支持通用FTP'
        },
        'default_values': {
            'connect_id': 0,
            'ssl_mode': 0,
            'ssl_id': 0
        },
        'connect_id_range': {
            'default': [0, 5]
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MFTPCFG: {connect_id},"ssl",{ssl_mode},{ssl_id}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mftpcfg_ssl


def set_mftpcfg_localfs(connect_id=0, fs_trans_type=0):
    """
    配置FTP文件传输方式
    """
    mftpcfg_local_fs = {
        'command': 'AT+MFTPCFG',
        'send_data': f'AT+MFTPCFG={connect_id},"local_fs",{fs_trans_type}',
        'search_data': f'AT+MFTPCFG={connect_id},"local_fs"',
        'fs_trans_type_range': {
            'default': [0, 1]
        },
        'fs_trans_type_values': {
            0: '通过串口输入输出方式传输',
            1: '通过本地文件系统方式传输'
        },
        'default_values': {
            'connect_id': 0,
            'fs_trans_type': 0
        },
        'connect_id_range': {
            'default': [0, 5]
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MFTPCFG: {connect_id},"local_fs",{fs_trans_type}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mftpcfg_local_fs


def set_mftpcfg_cid(connect_id=0, pdp_cid=1):
    """
    配置FTP的PDP索引id
    """
    mftpcfg_cid = {
        'command': 'AT+MFTPCFG',
        'send_data': f'AT+MFTPCFG={connect_id},"cid",{pdp_cid}',
        'search_data': f'AT+MFTPCFG={connect_id},"cid"',
        'pdp_cid_range': {
            'default': [1, 15],
            'ML305U': [1, 7],
            'MR880A/ML307N': []  # 不支持该参数配置
        },
        'not_supported_cid': ['MR880A', 'ML307N'],
        'special_notes': {
            'ML307X': '指定时需保证<pdp_cid>已激活',
            'MR880A/ML307N': '不支持cid配置'
        },
        'default_values': {
            'connect_id': 0,
            'pdp_cid': 1
        },
        'connect_id_range': {
            'default': [0, 5]
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MFTPCFG: {connect_id},"cid",{pdp_cid}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mftpcfg_cid


def set_mftpconn(connect_id=0, ip_hostname="", username="", password="", port=21):
    """
    建立FTP连接
    """
    send_data = f'AT+MFTPCONN={connect_id},"{ip_hostname}"'
    if username and password:
        send_data = f'AT+MFTPCONN={connect_id},"{ip_hostname}","{username}","{password}",{port}'
    elif username:
        send_data = f'AT+MFTPCONN={connect_id},"{ip_hostname}","{username}",,{port}'
    elif password:
        send_data = f'AT+MFTPCONN={connect_id},"{ip_hostname}",,"{password}",{port}'
    if port is None:
        send_data = f'AT+MFTPCONN={connect_id},"{ip_hostname}","{username}","{password}"'

    mftpconn = {
        'command': 'AT+MFTPCONN',
        'send_data': send_data,
        'ip_hostname_max_len': 255,
        'username_max_len': 255,
        'password_max_len': 255,
        'port_range': [0, 65535],
        'default_values': {
            'connect_id': 0,
            'ip_hostname': "",
            'username': "",
            'password': "",
            'port': 21
        },
        'connect_id_range': {
            'default': [0, 5]
        },
        'result': [r'OK', rf'\+MFTPCONN: {connect_id},0'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mftpconn


def set_mftpdisc(connect_id=0):
    """
    断开FTP连接
    """
    mftpdisc = {
        'command': 'AT+MFTPDISC',
        'send_data': f'AT+MFTPDISC={connect_id}',
        'connect_id_range': {
            'default': [0, 5]
        },
        'default_values': {
            'connect_id': 0
        },
        'result': [r'OK', rf'\+MFTPDISC: {connect_id},0', rf'\+MFTPURC: {connect_id},"conn",0'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mftpdisc


def set_mftpcwd(connect_id=0, path="/"):
    """
    切换当前工作路径
    """
    mftpcwd = {
        'command': 'AT+MFTPCWD',
        'send_data': f'AT+MFTPCWD={connect_id},"{path}"',
        'path_max_len': 255,
        'default_values': {
            'connect_id': 0,
            'path': "/"
        },
        'connect_id_range': {
            'default': [0, 5]
        },
        'result': [r'OK', rf'\+MFTPCWD: {connect_id},0'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mftpcwd


def set_mftppwd(connect_id=0):
    """
    获取当前工作路径
    """
    mftppwd = {
        'command': 'AT+MFTPPWD',
        'send_data': f'AT+MFTPPWD={connect_id}',
        'connect_id_range': {
            'default': [0, 5]
        },
        'default_values': {
            'connect_id': 0
        },
        'result': [r'OK', rf'\+MFTPPWD: {connect_id},0,"{re.escape("/")}"'],
        'search_result': [r'OK', rf'\+MFTPPWD: {connect_id},0,".*"'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mftppwd


def set_mftpmkd(connect_id=0, dir_name=""):
    """
    新建目录
    """
    mftpmkd = {
        'command': 'AT+MFTPMKD',
        'send_data': f'AT+MFTPMKD={connect_id},"{dir_name}"',
        'dir_name_max_len': 255,
        'default_values': {
            'connect_id': 0,
            'dir_name': ""
        },
        'connect_id_range': {
            'default': [0, 5]
        },
        'result': [r'OK', rf'\+MFTPMKD: {connect_id},0'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mftpmkd


def set_mftplist(connect_id=0, dir_name_file_name=""):
    """
    列出指定目录或文件信息
    """
    mftplist = {
        'command': 'AT+MFTPLIST',
        'send_data': f'AT+MFTPLIST={connect_id},"{dir_name_file_name}"',
        'dir_name_file_name_max_len': 255,
        'default_values': {
            'connect_id': 0,
            'dir_name_file_name': ""
        },
        'connect_id_range': {
            'default': [0, 5]
        },
        'result': [r'OK', rf'\+MFTPLIST: {connect_id},0'],
        'search_result': [r'OK', rf'\+MFTPLIST: {connect_id},0,".*"'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mftplist


def set_mftpdel(connect_id=0, dir_name_file_name=""):
    """
    删除指定目录或文件
    """
    mftpdel = {
        'command': 'AT+MFTPDEL',
        'send_data': f'AT+MFTPDEL={connect_id},"{dir_name_file_name}"',
        'dir_name_file_name_max_len': 255,
        'default_values': {
            'connect_id': 0,
            'dir_name_file_name': ""
        },
        'connect_id_range': {
            'default': [0, 5]
        },
        'result': [r'OK', rf'\+MFTPDEL: {connect_id},0'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mftpdel


def set_mftprn(connect_id=0, old_name="", new_name=""):
    """
    对目录或文件重命名
    """
    mftprn = {
        'command': 'AT+MFTPRN',
        'send_data': f'AT+MFTPRN={connect_id},"{old_name}","{new_name}"',
        'old_name_max_len': 255,
        'new_name_max_len': 255,
        'default_values': {
            'connect_id': 0,
            'old_name': "",
            'new_name': ""
        },
        'connect_id_range': {
            'default': [0, 5]
        },
        'result': [r'OK', rf'\+MFTPRN: {connect_id},0'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mftprn


def set_mftpretr(connect_id=0, file_name="", local_file_name="", offset=0, length=0):
    """
    从服务器获取文件
    """
    send_data = f'AT+MFTPRETR={connect_id},"{file_name}"'
    if local_file_name :
        if offset is not None and length is not None:
            send_data = f'AT+MFTPRETR={connect_id},"{file_name}","{local_file_name}",{offset},{length}'
        else:
            send_data = f'AT+MFTPRETR={connect_id},"{file_name}","{local_file_name}"'
    elif offset is not None and length is not None:
        send_data = f'AT+MFTPRETR={connect_id},"{file_name}",,{offset},{length}'

    mftpretr = {
        'command': 'AT+MFTPRETR',
        'send_data': send_data,
        'file_name_max_len': 255,
        'local_file_name_max_len': 255,
        'default_values': {
            'connect_id': 0,
            'file_name': "",
            'local_file_name': "",
            'offset': 0,
            'length': 0
        },
        'connect_id_range': {
            'default': [0, 5]
        },
        'result': [r'OK', rf'\+MFTPRETR: {connect_id},0'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mftpretr


def set_mftpappe(connect_id=0, file_name="", eof=1, length=0, data="", local_file_name=None):
    """
    向服务器上传文件（追加方式）
    """
    # 特殊处理local_file_name
    print(f'接受到参数：{file_name}, {local_file_name}, {eof}, {length}, {data}')
    result = [r'OK']
    if local_file_name is not None:
        send_data = f'AT+MFTPAPPE={connect_id},"{file_name}","{local_file_name}"'

    else:
        # 构建参数列表
        params = [str(connect_id), f'"{file_name}"']
        # 根据参数提供情况逐步添加可选参数
        if eof is not None:
            params.append(str(eof))

            if length is not None:
                params.append(str(length))
                urc_expect = rf'\+MFTPAPPE: {connect_id},0,{length}'
                result.append(urc_expect)
                if data is not None:
                    params.append(f'"{data}"')
        send_data = f'AT+MFTPAPPE={",".join(params)}'


    mftpappe = {
        'command': 'AT+MFTPAPPE',
        'send_data': send_data,
        'file_name_max_len': 255,
        'local_file_name_max_len': 255,
        'eof_range': [0, 1],
        'length_range': [1, 4096],
        'data_max_len': 4096,
        'default_values': {
            'connect_id': 0,
            'file_name': "",
            'eof': 1,
            'length': 0,
            'data': "",
            'local_file_name': ""
        },
        'connect_id_range': {
            'default': [0, 5]
        },
        'result': result,
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mftpappe


def set_mftpstor(connect_id=0, file_name="", eof=1, length=0, data="", local_file_name=""):
    """
    向服务器覆盖写入文件
    """
    send_data = f'AT+MFTPSTOR={connect_id},"{file_name}"'
    if local_file_name:
        send_data = f'AT+MFTPSTOR={connect_id},"{file_name}","{local_file_name}"'
    elif eof == 1 and length == 0 and not data:
        send_data = f'AT+MFTPSTOR={connect_id},"{file_name}",{eof}'
    elif eof == 1 and length > 0 and not data:
        send_data = f'AT+MFTPSTOR={connect_id},"{file_name}",{eof},{length}'
    elif eof == 1 and length > 0 and data:
        send_data = f'AT+MFTPSTOR={connect_id},"{file_name}",{eof},{length},"{data}"'

    mftpstor = {
        'command': 'AT+MFTPSTOR',
        'send_data': send_data,
        'file_name_max_len': 255,
        'local_file_name_max_len': 255,
        'eof_range': [0, 1],
        'length_range': [1, 4096],
        'data_max_len': 4096,
        'default_values': {
            'connect_id': 0,
            'file_name': "",
            'eof': 1,
            'length': 0,
            'data': "",
            'local_file_name': ""
        },
        'connect_id_range': {
            'default': [0, 5]
        },
        'result': [r'OK', rf'\+MFTPSTOR: {connect_id},0'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mftpstor


def set_mftpstate(connect_id=0):
    """
    查询FTP状态
    """
    mftpstate = {
        'command': 'AT+MFTPSTATE',
        'send_data': f'AT+MFTPSTATE={connect_id}',
        'connect_id_range': {
            'default': [0, 5]
        },
        'default_values': {
            'connect_id': 0
        },
        'state_values': {
            0: 'FTP连接处于未建立状态',
            1: 'FTP连接处于已建立状态',
            2: '正在进行FTP文件下载',
            3: '正在进行FTP文件上传'
        },
        'result': [r'OK', rf'\+MFTPSTATE: {connect_id},[0-3]'],
        'search_result': [r'OK', rf'\+MFTPSTATE: {connect_id},[0-3]'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mftpstate