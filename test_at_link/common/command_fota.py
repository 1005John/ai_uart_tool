import re
# 新增模块升级有关配置以及代码

def set_mfwcfg_url(url=None):
    """
    AT+MFWCFG URL配置函数
    配置HTTP/FTP服务器或本地文件系统URL
    """
    if url is None:
        # 查询模式
        send_data = 'AT+MFWCFG="url"'
        # search_result = [r'OK', r'\+MFWCFG: "url",".*"']
        search_result = [r'OK', r'\+MFWCFG: "url",.*']  # 移除引号匹配
    else:
        # 配置模式
        send_data = f'AT+MFWCFG="url","{url}"'
        search_result = [r'OK', rf'\+MFWCFG: "url","{re.escape(url)}"']



    mfwcfg_url = {
        'command': 'AT+MFWCFG',
        'send_data': send_data,
        'search_data': 'AT+MFWCFG="url"',
        'url_max_len': 256,
        'url_protocols': ['http', 'https', 'file'],
        'special_notes': {
            'ML307C-DL-CN/ML307C-DL-EM': ['FILE', 'FTP'],
            'ML307C-DC-CN/ML307C-GC-CN/ML307C-DC-EM': ['FTP'],
        },
        'default_values': {
            'url': ""
        },
        'result': [r'OK'],
        'search_result': search_result,
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mfwcfg_url





def set_mfwcfg_auth(user="", passwd=""):
    """
    AT+MFWCFG 下载鉴权配置函数
    配置服务器登录用户名和密码
    """
    # 清理输入参数中的引号
    clean_user = user.strip('"\'') if user else ""
    clean_passwd = passwd.strip('"\'') if passwd else ""

    # 判断是否为查询模式：当user和passwd都为空时
    is_query_mode = not clean_user and not clean_passwd

    if is_query_mode:
        # 查询模式
        send_data = 'AT+MFWCFG="auth"'
        search_result = [r'OK', r'\+MFWCFG: "auth",[^,]*,[^,]*']
    else:
        # 配置模式 - 确保参数不包含多余的引号
        send_data = f'AT+MFWCFG="auth","{clean_user}","{clean_passwd}"'
        search_result = [r'OK', rf'\+MFWCFG: "auth","{re.escape(clean_user)}","{re.escape(clean_passwd)}"']

    mfwcfg_auth = {
        'command': 'AT+MFWCFG',
        'send_data': send_data,
        'search_data': 'AT+MFWCFG="auth"',
        'user_max_len': 48,
        'passwd_max_len': 48,
        'default_values': {
            'user': "",
            'passwd': ""
        },
        'result': [r'OK'],
        'search_result': search_result,
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mfwcfg_auth




def set_mfwcfg_timeout(timeout=None):
    """
    AT+MFWCFG 服务器超时时间配置函数
    """
    if timeout is None:
        # 查询模式
        send_data = 'AT+MFWCFG="timeout"'
        search_result = [r'OK', r'\+MFWCFG: "timeout",\d+']
    else:
        # 配置模式
        send_data = f'AT+MFWCFG="timeout",{timeout}'
        search_result = [r'OK', rf'\+MFWCFG: "timeout",{timeout}']

    mfwcfg_timeout = {
        'command': 'AT+MFWCFG',
        'send_data': send_data,
        'search_data': 'AT+MFWCFG="timeout"',
        'timeout_range': {
            'default': [30, 180]
        },
        'special_notes': {
            'ML307C-DL-CN/ML307C-DL-EM': '不支持配置服务器超时时间功能',
        },
        'default_values': {
            'timeout': 60
        },
        'result': [r'OK'],
        'search_result': search_result,
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mfwcfg_timeout



def set_mfwcfg_mode(mode=None):
    """
    AT+MFWCFG 升级包类型配置函数
    """
    if mode is None:
        # 查询模式
        send_data = 'AT+MFWCFG="mode"'
        search_result = [r'OK', r'\+MFWCFG: "mode",\d+']
    else:
        # 配置模式
        send_data = f'AT+MFWCFG="mode",{mode}'
        search_result = [r'OK', rf'\+MFWCFG: "mode",{mode}']

    # ... 其他配置
    mfwcfg_mode = {
        'command': 'AT+MFWCFG',
        'send_data': send_data,  # 使用上面定义的 send_data
        'search_data': 'AT+MFWCFG="mode"',
        'mode_range': (0, 1),
        'mode_description': {
            '0': '差分',
            '1': '全量'
        },
        'special_notes': {
            'ML307C': '不支持升级模式配置'
        },
        'default_values': {
            'mode': 0
        },
        'result': [r'OK'],
        'search_result': search_result,  # 使用上面定义的 search_result
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mfwcfg_mode




def set_mfwcfg_progind(progbytes=None):
    """
    AT+MFWCFG 升级上报提示配置函数
    """
    if progbytes is None:
        # 查询模式
        send_data = 'AT+MFWCFG="progind"'
        search_result = [r'OK', r'\+MFWCFG: "progind",\d+']  # 使用通配符匹配数字
    else:
        # 配置模式
        send_data = f'AT+MFWCFG="progind",{progbytes}'
        search_result = [r'OK', rf'\+MFWCFG: "progind",{progbytes}']

    # ... 其他配置
    mfwcfg_progind = {
        'command': 'AT+MFWCFG',
        'send_data': send_data,
        'search_data': 'AT+MFWCFG="progind"',
        'progbytes_multiple': 1024,
        'special_notes': {
            'ML307C-DL-CN/ML307C-DL-EM': '不支持升级上报提示配置',
        },
        'default_values': {
            'progbytes': 0
        },
        'result': [r'OK'],
        'search_result': search_result,
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mfwcfg_progind



def set_mfwcfg_ssl(ssl_id=None):
    """
    AT+MFWCFG SSL配置函数
    """
    if ssl_id is None:
        # 查询模式
        send_data = 'AT+MFWCFG="ssl"'
        search_result = [r'OK', r'\+MFWCFG: "ssl",\d+']
    else:
        # 配置模式
        send_data = f'AT+MFWCFG="ssl",{ssl_id}'
        search_result = [r'OK', rf'\+MFWCFG: "ssl",{ssl_id}']

    mfwcfg_ssl = {
        'command': 'AT+MFWCFG',
        'send_data': send_data,  # 使用正确的send_data变量
        'search_data': 'AT+MFWCFG="ssl"',
        'ssl_id_range': {
            'default': [0, 4]
        },
        'special_notes': {
            'ML307C-DL-CN/ML307C-DL-EM': '不支持该功能配置',
        },
        'default_values': {
            'ssl_id': 0
        },
        'result': [r'OK'],
        'search_result': search_result,  # 使用正确的search_result变量
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mfwcfg_ssl



def set_mfwcfg_pkgsize(pkgsize=None):
    """
    AT+MFWCFG HTTP下载包每包大小配置函数
    """
    if pkgsize is not None:
        # 添加参数验证
        if not isinstance(pkgsize, int) or pkgsize < 512 or pkgsize > 3072 or pkgsize % 512 != 0:
            raise ValueError("pkgsize must be multiple of 512, between 512 and 3072")

    if pkgsize is None:
        # 查询模式
        send_data = 'AT+MFWCFG="pkgsize"'
        search_result = [r'OK', r'\+MFWCFG: "pkgsize",\d+']
    else:
        # 配置模式
        send_data = f'AT+MFWCFG="pkgsize",{pkgsize}'
        search_result = [r'OK', rf'\+MFWCFG: "pkgsize",{pkgsize}']

    mfwcfg_pkgsize = {
        'command': 'AT+MFWCFG',
        'send_data': send_data,
        'search_data': 'AT+MFWCFG="pkgsize"',
        'pkgsize_multiple': 512,
        'pkgsize_max': 3072,
        'special_notes': {
            'ML307C': '不支持HTTP方式下载每包大小配置'
        },
        'default_values': {
            'pkgsize': 512
        },
        'result': [r'OK'],  # 成功响应
        'search_result': search_result,
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+', r'\+CME ERROR: \d+']  # 添加更具体的错误匹配
    }
    return mfwcfg_pkgsize




def set_mfwdload_set(offset=0, length=0, data=""):
    """
    AT+MFWDLOAD 设置命令函数
    通过串口写入升级包
    """
    if data:
        send_data = f'AT+MFWDLOAD={offset},{length},"{data}"'
    else:
        send_data = f'AT+MFWDLOAD={offset},{length}'

    mfwdload_set = {
        'command': 'AT+MFWDLOAD',
        'send_data': send_data,
        'offset_range': {
            'default': [0, 0]  # 不支持断点续传，仅支持0
        },
        'len_max': 512,
        'special_notes': {
            'ML307C-DC-CN/ML307C-GC-CN/ML307C-DC-EM': '不支持断点续传功能，offset仅支持0，len为差分包实际总大小，可以大于512'
        },
        'default_values': {
            'offset': 0,
            'length': 0,
            'data': ""
        },
        'result': [r'OK', r'>'] if not data else [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mfwdload_set


def set_mfwdload_execute():
    """
    AT+MFWDLOAD 执行命令函数
    HTTP/FTP下载与指定本地升级文件
    """
    mfwdload_execute = {
        'command': 'AT+MFWDLOAD',
        'send_data': 'AT+MFWDLOAD',
        'state_description': {
            '1': '下载中',
            '2': '下载成功',
            '3': '下载失败'
        },
        'special_notes': {
            'ML307C-DL-CN/ML307C-DL-EM': '不支持该命令',
            'ML307C-DC-CN/ML307C-GC-CN/ML307C-DC-EM': '仅在使用全系统差分升级时支持该命令，使用该命令下载最小系统升级包将报错'
        },
        'result': [r'OK', r'\+MFWDLOAD: \d+,\d+,\d+'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mfwdload_execute


def set_mfwdload_query():
    """
    AT+MFWDLOAD 查询命令函数
    """
    mfwdload_query = {
        'command': 'AT+MFWDLOAD',
        'send_data': 'AT+MFWDLOAD?',
        'special_notes': {
            'ML307C-DL-CN/ML307C-DL-EM': '不支持该命令',
            'ML307C-DC-CN/ML307C-GC-CN/ML307C-DC-EM': '仅在HTTP/FTP下载时查询有效'
        },
        'result': [r'OK', r'\+MFWDLOAD: \d+,\d*,\d+'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mfwdload_query


def set_mfwupgrade():
    """
    AT+MFWUPGRADE 执行升级函数
    """
    mfwupgrade = {
        'command': 'AT+MFWUPGRADE',
        'send_data': 'AT+MFWUPGRADE',
        'state_description': {
            '1': '升级中',
            '2': '升级成功',
            '3': '升级失败'
        },
        'special_notes': {
            'ML307C-DL-CN/ML307C-DL-EM': '需进入特殊模式进行升级，故直接通过MFWUPGRADE命令启动HTTP/FTP下载与升级',
            'ML307C-DC-CN/ML307C-GC-CN/ML307C-DC-EM': '使用全系统差分升级后模组不会多次重启，仅重启一次'
        },
        'result': [r'OK', r'\+MFWUPGRADE: \d+(?:,\d+)?'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mfwupgrade


def set_mfwerase():
    """
    AT+MFWERASE 擦除OTA数据函数
    """
    mfwerase = {
        'command': 'AT+MFWERASE',
        'send_data': 'AT+MFWERASE',
        'special_notes': {
            'ML307C-DL-CN/ML307C-DL-EM': '不支持该命令',
            'ML307C-DC-CN/ML307C-GC-CN/ML307C-DC-EM': '仅在使用全系统差分升级时使用该命令才会生效'
        },
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mfwerase