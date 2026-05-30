def set_mgnsscfg_nmea_mask(mask=0):
    """
    AT+MGNSSCFG="nmea/mask" NMEA输出配置
    AT+MGNSSCFG="nmea/mask"[,<mask>]
    mask: 0-63，bit位控制对应NMEA语句输出
    bit0: GGA信息, bit1: GSV信息, bit2: GSA信息, bit3: RMC信息, bit4: VTG信息, bit5: GLL信息
    """
    if mask == "":
        send_data = f'AT+MGNSSCFG="nmea/mask"'
    else:
        send_data = f'AT+MGNSSCFG="nmea/mask",{mask}'

    mgnsscfg_nmea_mask = {
        'command': 'AT+MGNSSCFG',
        'send_data': send_data,
        'search_data': 'AT+MGNSSCFG="nmea/mask"',
        'search_result': [r'OK', rf'\+MGNSSCFG: "nmea/mask",{mask}'],
        'mask_desc': 'NMEA输出掩码：bit0-GGA,bit1-GSV,bit2-GSA,bit3-RMC,bit4-VTG,bit5-GLL',
        'mask_range': (0, 63),
        'mask_default': 0,
        'not_supported_models': [],
        'notes': [
            '参数支持NV存储',
            '设置63表示开启所有NMEA语句输出'
        ],
        'default_values': {
            'mask': 0
        },
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9]+']
    }
    return mgnsscfg_nmea_mask


def set_mgnsscfg_nmea_cycle(cycle=1):
    """
    AT+MGNSSCFG="nmea/cycle" NMEA输出周期设置
    AT+MGNSSCFG="nmea/cycle"[,<cycle>]
    cycle: NMEA输出周期，单位秒，范围1-60
    """
    if cycle == "":
        send_data = f'AT+MGNSSCFG="nmea/cycle"'
    else:
        send_data = f'AT+MGNSSCFG="nmea/cycle",{cycle}'

    mgnsscfg_nmea_cycle = {
        'command': 'AT+MGNSSCFG',
        'send_data': send_data,
        'search_data': 'AT+MGNSSCFG="nmea/cycle"',
        'search_result': [r'OK', rf'\+MGNSSCFG: "nmea/cycle",{cycle}'],
        'cycle_desc': 'NMEA输出周期，单位秒',
        'cycle_range': (1, 60),
        'cycle_default': 1,
        'not_supported_models': [],
        'notes': [
            '参数支持NV存储',
            '设置周期越短，数据更新越快，功耗越高'
        ],
        'default_values': {
            'cycle': 1
        },
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9]+']
    }
    return mgnsscfg_nmea_cycle


def set_mgnsscfg_nmea_port(port=2):
    """
    AT+MGNSSCFG="nmea/port" NMEA数据输出接口设置
    AT+MGNSSCFG="nmea/port"[,<port>]
    port: 0-USB AT口输出，1-USB GPS口输出，2-UART0口输出
    """
    if port == "":
        send_data = f'AT+MGNSSCFG="nmea/port"'
    else:
        send_data = f'AT+MGNSSCFG="nmea/port",{port}'

    mgnsscfg_nmea_port = {
        'command': 'AT+MGNSSCFG',
        'send_data': send_data,
        'search_data': 'AT+MGNSSCFG="nmea/port"',
        'search_result': [r'OK', rf'\+MGNSSCFG: "nmea/port",{port}'],
        'port_desc': 'NMEA输出接口：0-USB AT口，1-USB GPS口，2-UART0口',
        'port_range': [0, 1, 2],
        'port_default': 2,
        'not_supported_models': {
            'ML302A/ML307A': '不支持此参数配置',
            'ML307C': '暂不支持port=1',
            'ML307N': '仅支持port=2'
        },
        'notes': [
            '参数支持NV存储',
            '不同型号对port值支持情况不同'
        ],
        'default_values': {
            'port': 2
        },
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9]+']
    }
    return mgnsscfg_nmea_port


def set_mgnsscfg_agnss_url(url=""):
    """
    AT+MGNSSCFG="agnss/url" AGNSS辅助定位服务器URL设置
    AT+MGNSSCFG="agnss/url"[,<url>]
    url: AGNSS辅助定位服务器地址，格式"hostname:port"，最大64字节
    """
    if url == "":
        send_data = f'AT+MGNSSCFG="agnss/url"'
    else:
        send_data = f'AT+MGNSSCFG="agnss/url","{url}"'

    mgnsscfg_agnss_url = {
        'command': 'AT+MGNSSCFG',
        'send_data': send_data,
        'search_data': 'AT+MGNSSCFG="agnss/url"',
        'search_result': [r'OK', rf'\+MGNSSCFG: "nmea/url",{url}'],
        'url_desc': 'AGNSS辅助定位服务器地址，hostname:port格式',
        'url_max_length': 64,
        'not_supported_models': {
            'ML302A/ML307A/ML307C': '默认已配置服务器，不支持配置',
            'ML307N': '不支持AGNSS功能'
        },
        'notes': [
            '参数支持NV存储',
            '格式示例：cmiot-api1.rx-networks.cn:80'
        ],
        'default_values': {
            'url': ''
        },
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9]+']
    }
    return mgnsscfg_agnss_url


def set_mgnsscfg_agnss_interval(interval=0):
    """
    AT+MGNSSCFG="agnss/interval" AGNSS辅助数据自动更新间隔设置
    AT+MGNSSCFG="agnss/interval"[,<interval>]
    interval: 0-禁止自动更新，30-240-自动更新间隔（分钟）
    """
    if interval == "":
        send_data = f'AT+MGNSSCFG="agnss/interval"'
    else:
        send_data = f'AT+MGNSSCFG="agnss/interval",{interval}'

    mgnsscfg_agnss_interval = {
        'command': 'AT+MGNSSCFG',
        'send_data': send_data,
        'search_data': 'AT+MGNSSCFG="agnss/interval"',
        'search_result': [r'OK', rf'\+MGNSSCFG: "agnss/interval",{interval}'],
        'interval_desc': 'AGNSS自动更新间隔：0-禁止，30-240分钟',
        'interval_range': (0, 240),
        'interval_valid_range': [0] + list(range(30, 241)),
        'interval_default': 0,
        'not_supported_models': {
            'ML307N': '不支持AGNSS功能'
        },
        'notes': [
            '参数支持NV存储',
            '辅助数据有效时间为120分钟',
            '设置为0表示手动更新'
        ],
        'default_values': {
            'interval': 0
        },
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9]+']
    }
    return mgnsscfg_agnss_interval


def set_mgnsscfg_dgnss_url(url=""):
    """
    AT+MGNSSCFG="dgnss/url" DGNSS差分定位服务器URL设置
    AT+MGNSSCFG="dgnss/url"[,<url>]
    url: DGNSS差分定位服务器地址，格式"hostname:port"，最大64字节
    """
    if url == "":
        send_data = f'AT+MGNSSCFG="dgnss/url"'
    else:
        send_data = f'AT+MGNSSCFG="dgnss/url","{url}"'

    mgnsscfg_dgnss_url = {
        'command': 'AT+MGNSSCFG',
        'send_data': send_data,
        'search_data': 'AT+MGNSSCFG="dgnss/url"',
        'search_result': [r'\+MGNSSCFG: "dgnss/url",.+'],
        'url_desc': 'DGNSS差分定位服务器地址，hostname:port格式',
        'url_max_length': 64,
        'not_supported_models': {
            'ML302A/ML307A/ML307C/ML307N': '不支持DGNSS功能'
        },
        'notes': [
            '参数支持NV存储',
            '格式示例：cmiot-api1.rx-networks.cn:90'
        ],
        'default_values': {
            'url': ''
        },
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9]+']
    }
    return mgnsscfg_dgnss_url


def set_mgnsscfg_dgnss_user(user=""):
    """
    AT+MGNSSCFG="dgnss/user" DGNSS差分定位用户名设置
    AT+MGNSSCFG="dgnss/user"[,<user>]
    user: DGNSS差分定位用户名，最大64字节
    """
    if user == "":
        send_data = f'AT+MGNSSCFG="dgnss/user"'
    else:
        send_data = f'AT+MGNSSCFG="dgnss/user","{user}"'

    mgnsscfg_dgnss_user = {
        'command': 'AT+MGNSSCFG',
        'send_data': send_data,
        'search_data': 'AT+MGNSSCFG="dgnss/user"',
        'search_result': [r'\+MGNSSCFG: "dgnss/user",.+'],
        'user_desc': 'DGNSS差分定位用户名',
        'user_max_length': 64,
        'not_supported_models': {
            'ML302A/ML307A/ML307C/ML307N': '不支持DGNSS功能'
        },
        'notes': [
            '参数支持NV存储',
            '需与服务器配置的用户名一致'
        ],
        'default_values': {
            'user': ''
        },
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9]+']
    }
    return mgnsscfg_dgnss_user


def set_mgnsscfg_dgnss_pwd(pwd=""):
    """
    AT+MGNSSCFG="dgnss/pwd" DGNSS差分定位密码设置
    AT+MGNSSCFG="dgnss/pwd"[,<pwd>]
    pwd: DGNSS差分定位密码，最大64字节
    """
    if pwd == "":
        send_data = f'AT+MGNSSCFG="dgnss/pwd"'
    else:
        send_data = f'AT+MGNSSCFG="dgnss/pwd","{pwd}"'

    mgnsscfg_dgnss_pwd = {
        'command': 'AT+MGNSSCFG',
        'send_data': send_data,
        'search_data': 'AT+MGNSSCFG="dgnss/pwd"',
        'search_result': [r'\+MGNSSCFG: "dgnss/pwd",.+'],
        'pwd_desc': 'DGNSS差分定位密码',
        'pwd_max_length': 64,
        'not_supported_models': {
            'ML302A/ML307A/ML307C/ML307N': '不支持DGNSS功能'
        },
        'notes': [
            '参数支持NV存储',
            '需与服务器配置的密码一致'
        ],
        'default_values': {
            'pwd': ''
        },
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9]+']
    }
    return mgnsscfg_dgnss_pwd


def set_mgnsscfg_dgnss_mount(mount=""):
    """
    AT+MGNSSCFG="dgnss/mount" DGNSS差分定位挂载点设置
    AT+MGNSSCFG="dgnss/mount"[,<mount>]
    mount: DGNSS差分定位挂载点，最大64字节
    """
    if mount == "":
        send_data = f'AT+MGNSSCFG="dgnss/mount"'
    else:
        send_data = f'AT+MGNSSCFG="dgnss/mount","{mount}"'

    mgnsscfg_dgnss_mount = {
        'command': 'AT+MGNSSCFG',
        'send_data': send_data,
        'search_data': 'AT+MGNSSCFG="dgnss/mount"',
        'search_result': [r'\+MGNSSCFG: "dgnss/mount",.+'],
        'mount_desc': 'DGNSS差分定位挂载点',
        'mount_max_length': 64,
        'not_supported_models': {
            'ML302A/ML307A/ML307C/ML307N': '不支持DGNSS功能'
        },
        'notes': [
            '参数支持NV存储',
            '示例：RTCM32GGA'
        ],
        'default_values': {
            'mount': ''
        },
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9]+']
    }
    return mgnsscfg_dgnss_mount


def set_mgnsscfg_constellation_mask(mask=0):
    """
    AT+MGNSSCFG="constellation/mask" GNSS搜星模式掩码设置
    AT+MGNSSCFG="constellation/mask"[,<mask>]
    mask: 搜星模式掩码，bit0:GPS, bit1:BDS, bit2:QZSS, bit3:GLONASS, bit4:Galileo
    """
    if mask == "":
        send_data = f'AT+MGNSSCFG="constellation/mask"'
    else:
        send_data = f'AT+MGNSSCFG="constellation/mask",{mask}'

    mgnsscfg_constellation_mask = {
        'command': 'AT+MGNSSCFG',
        'send_data': send_data,
        'search_data': 'AT+MGNSSCFG="constellation/mask"',
        'search_result': [r'\+MGNSSCFG: "constellation/mask",\d+'],
        'mask_desc': '搜星模式掩码：bit0-GPS,bit1-BDS,bit2-QZSS,bit3-GLONASS,bit4-Galileo',
        'mask_range': (0, 31),
        'mask_default': 0,
        'not_supported_models': {},
        'notes': [
            'ML307N使用此配置切换搜星后需使用AT+MGNSSRST=0冷重启GNSS',
            '示例：mask=3表示GPS+BDS双模搜星'
        ],
        'default_values': {
            'mask': 0
        },
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9]+']
    }
    return mgnsscfg_constellation_mask


def set_mgnss(ctrl=1):
    """
    AT+MGNSS 开启/关闭GNSS
    AT+MGNSS=<ctrl>
    ctrl: 0-关闭GNSS，1-开启GNSS（连续定位），2-开启GNSS（单次定位）
    """
    send_data = f'AT+MGNSS={ctrl}'

    mgnss = {
        'command': 'AT+MGNSS',
        'send_data': send_data,
        'search_data': 'AT+MGNSS?',
        'search_result': [r'OK', rf'\+MGNSS: {ctrl}'],
        'ctrl_desc': 'GNSS控制：0-关闭，1-开启连续定位，2-开启单次定位',
        'ctrl_range': [0, 1, 2],
        'ctrl_default': 1,
        'result_urc': [
            r'\+MGNSSURC: "state",\d+',
            r'\+MGNSSLOC: .+'
        ],
        'not_supported_models': [],
        'notes': [
            '开启GNSS后会自动输出NMEA信息',
            '单次定位模式下仅支持自动上报位置信息'
        ],
        'default_values': {
            'ctrl': 1
        },
        'result': [r'OK',rf'\+MGNSSURC: "state",[01]'],
        'err_result': [r'\+CME ERROR: [0-9]+']
    }
    return mgnss


def set_mgnssnmea(type=""):
    """
    AT+MGNSSNMEA 获取NMEA信息
    AT+MGNSSNMEA=<type>
    type: "GGA", "GSV", "GSA", "RMC", "VTG", "GLL"
    """
    if type == "":
        send_data = f'AT+MGNSSNMEA=?'
    else:
        send_data = f'AT+MGNSSNMEA="{type}"'

    mgnssnmea = {
        'command': 'AT+MGNSSNMEA',
        'send_data': send_data,
        'search_data': 'AT+MGNSSNMEA?',
        'search_result': [r'OK', r'\+MGNSSNMEA:', r'\$[A-Z]+GGA', r'\$[A-Z]+GSV', r'\$[A-Z]+GSA', r'\$[A-Z]+RMC',
                          r'\$[A-Z]+VTG', r'\$[A-Z]+GLL'],
        'type_desc': {
            'GGA': '定位信息',
            'GSV': '可见卫星信息',
            'GSA': '有效卫星信息',
            'RMC': '推荐定位信息',
            'VTG': '航迹向与速度',
            'GLL': '地理位置信息'
        },
        'type_list': ['GGA', 'GSV', 'GSA', 'RMC', 'VTG', 'GLL'],
        'not_supported_models': [],
        'notes': [
            '获取当前最新的 NMEA 信息',
            '坐标系为 WGS84'
        ],
        'default_values': {
            'type': ''
        },
        'result': [rf'\+MGNSSNMEA: \$[A-Z]+.{type}', r'OK'],
        'err_result': [r'\+CME ERROR: [0-9]+']
    }

    return mgnssnmea


def set_mgnssloc(auto_report=0):
    """
    AT+MGNSSLOC 获取位置定位信息
    AT+MGNSSLOC=<auto_report>
    auto_report: 0-不自动上报，1-自动上报
    """
    if auto_report == "?":
         send_data = f'AT+MGNSSLOC'
    else:
        send_data = f'AT+MGNSSLOC={auto_report}'

    mgnssloc = {
        'command': 'AT+MGNSSLOC',
        'send_data': send_data,
        'search_data': 'AT+MGNSSLOC?',
        'search_result': [rf'\+MGNSSLOC: {auto_report}','OK'],
        'auto_report_desc': '自动上报控制：0-不自动上报，1-自动上报',
        'auto_report_range': [0, 1],
        'auto_report_default': 0,
        'result_urc': [r'\+MGNSSLOC: .+'],
        'location_fields': {
            'UTC': 'UTC时间(hhmmss.sss)',
            'latitude': '纬度(ddmm.mmmmN/S)',
            'longitude': '经度(dddmm.mmmmE/W)',
            'hdop': '水平精度因子(x.x)',
            'altitude': '海拔高度(x.x米)',
            'fix': '定位类型(1-未定位,2-2D,3-3D)',
            'cog': '运动角度(ddd.dd度)',
            'spkm': '水平速度(x.x Km/h)',
            'spkn': '水平速度(x.x Knots)',
            'date': '当前日期(ddmmyy)',
            'nsat': '参与定位卫星数量',
            'dtype': '差分标识(0-无效,1-单点,2-差分)'
        },
        'not_supported_models': [],
        'notes': [
            '设置为1时，定位成功后自动上报位置信息',
            '单次定位模式下仅支持自动上报'
        ],
        'default_values': {
            'auto_report': 0
        },
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9]+']
    }
    return mgnssloc


def set_mgnssrst(rst_mode=0):
    """
    AT+MGNSSRST 软重启GNSS
    AT+MGNSSRST=<rst_mode>
    rst_mode: 0-冷启动，1-温启动，2-热启动
    """
    if rst_mode == "?":
        send_data = f'AT+MGNSSRST=?'
    else:
       send_data = f'AT+MGNSSRST={rst_mode}'

    mgnssrst = {
        'command': 'AT+MGNSSRST',
        'send_data': send_data,
        'search_data': 'AT+MGNSSRST?',
        'search_result': [rf'\+MGNSSRST: {rst_mode}', 'OK'],
        'rst_mode_desc': '重启模式：0-冷启动，1-温启动，2-热启动',
        'rst_mode_range': [0, 1, 2],
        'rst_mode_default': 0,
        'not_supported_models': {
            'ML307N': '不支持温启动和热启动'
        },
        'notes': [
            '冷启动：清除所有历史数据',
            '温启动：保留星历数据',
            '热启动：保留所有历史数据'
        ],
        'default_values': {
            'rst_mode': 0
        },
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9]+']
    }
    return mgnssrst

def set_magnssrefloc(ref_latitude=0, ref_longitude=0, mode=2):
    """
    AT+MAGNSSREFLOC 参考坐标设置
    AT+MAGNSSREFLOC=<ref_latitude>,<ref_longitude>[,<mode>]
    mode: 0-单次有效，1-持续有效，2-允许 UE 自动更新
    """
    params = [str(ref_latitude), str(ref_longitude)]
    if mode != "":
        params.append(str(mode))

    send_data = f'AT+MAGNSSREFLOC={",".join(params)}'
    mode1 = mode if mode else 2
    # 处理经纬度参数：如果是数字则格式化为 8 位小数，否则保持原样用于错误测试
    try:
        lat_formatted = f'{float(ref_latitude):.8f}'
        lon_formatted = f'{float(ref_longitude):.8f}'
        search_pattern = rf'\+MAGNSSREFLOC: {lat_formatted},{lon_formatted},{mode1}'
    except (ValueError, TypeError):
        # 对于无效参数，使用正则表达式匹配任意值
        search_pattern = rf'\+MAGNSSREFLOC: .+'

    magnssrefloc = {
        'command': 'AT+MAGNSSREFLOC',
        'send_data': send_data,
        'search_data': 'AT+MAGNSSREFLOC?',
        'search_result': [search_pattern, 'OK'],

        'ref_latitude_desc': '参考纬度 (-90 至 90 度)',
        'ref_latitude_range': (-90, 90),
        'ref_longitude_desc': '参考经度 (-180 至 180 度)',
        'ref_longitude_range': (-180, 180),
        'mode_desc': '模式：0-单次有效，1-持续有效，2-允许 UE 自动更新',
        'mode_range': [0, 1, 2],
        'mode_default': 2,
        'not_supported_models': {
            'ML302A/ML307A/ML307C/ML307N': '仅支持mode参数为 2'
        },
        'notes': [
            '用于辅助定位时缩短首次定位时间',
            '小数点后超过 8 位会导致精度丢失'
        ],
        'default_values': {
            'ref_latitude': 0,
            'ref_longitude': 0,
            'mode': 2
        },
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9]+']
    }
    return magnssrefloc



def set_magnssdata():
    """
    AT+MAGNSSDATA 下载/查询AGNSS辅助定位数据
    AT+MAGNSSDATA
    """
    magnssdata = {
        'command': 'AT+MAGNSSDATA',
        'send_data': 'AT+MAGNSSDATA',
        'search_data': 'AT+MAGNSSDATA=?',
        'search_result': [r'\+MAGNSSDATA:'],
        'result_urc': [r'\+MAGNSSDATA: \d+,\d+,\d+'],
        'state_desc': {
            0: '辅助数据无效',
            1: '辅助数据有效',
            2: '无法判断数据有效性（UE时间未同步）',
            255: '辅助数据为空'
        },
        'not_supported_models': {
            'ML307N': '不支持AGNSS'
        },
        'notes': [
            '执行命令触发更新AGNSS辅助数据',
            '更新完成后自动上报+MAGNSSDATA URC信息',
            '数据大小不能作为下载流量的参考依据'
        ],
        'result': [r'OK', r'\+MAGNSSDATA:'],
        'err_result': [r'\+CME ERROR: [0-9]+']
    }
    return magnssdata


def set_magnssen(enable=0):
    """
    AT+MAGNSSEN 开启/关闭辅助定位功能
    AT+MAGNSSEN=<enable>
    enable: 0-关闭AGNSS，1-开启AGNSS
    """
    send_data = f'AT+MAGNSSEN={enable}'

    magnssen = {
        'command': 'AT+MAGNSSEN',
        'send_data': send_data,
        'search_data': 'AT+MAGNSSEN?',
        'search_result': [rf'\+MAGNSSEN: {enable}', 'OK'],
        'enable_desc': 'AGNSS控制：0-关闭，1-开启',
        'enable_range': [0, 1],
        'enable_default': 0,
        'not_supported_models': {
            'ML307N': '不支持AGNSS'
        },
        'notes': [
            '需在GNSS开启之前使能辅助定位',
            '开启后可以大幅缩短首次定位时间'
        ],
        'default_values': {
            'enable': 0
        },
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9]+']
    }
    return magnssen


def set_mdgnssen(enable=0, cycle=""):
    """
    AT+MDGNSSEN 开启/关闭差分定位功能
    AT+MDGNSSEN=<enable>[,<cycle>]
    enable: 0-关闭DGNSS，1-开启DGNSS
    cycle: 本地定位数据上报间隔(1-30秒)
    """
    params = [str(enable)]
    if cycle != "":
        params.append(str(cycle))

    send_data = f'AT+MDGNSSEN={",".join(params)}'

    mdgnssen = {
        'command': 'AT+MDGNSSEN',
        'send_data': send_data,
        'search_data': 'AT+MDGNSSEN=?',
        'search_result': [r'\+MDGNSSEN: \(0-1\),\(1-30\)'],
        'enable_desc': 'DGNSS控制：0-关闭，1-开启',
        'enable_range': [0, 1],
        'enable_default': 0,
        'cycle_desc': '本地定位数据上报间隔(1-30秒)',
        'cycle_range': (1, 30),
        'not_supported_models': {
            'ML302A/ML307A/ML307C/ML307N': '不支持差分定位功能'
        },
        'notes': [
            '开启后提升定位精度',
            '定位过程中会持续消耗数据流量',
            '可从NMEA/GGA数据中判断是否处于差分定位模式'
        ],
        'default_values': {
            'enable': 0,
            'cycle': ''
        },
        'result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9]+']
    }
    return mdgnssen


def set_mgnssurc():
    """
    +MGNSSURC 异步信息上报（URC）
    GNSS发生异步错误时自动上报
    """
    mgnssurc = {
        'command': '+MGNSSURC',
        'is_urc': True,
        'result_urc': [
            r'\+MGNSSURC: "error","\d+"',
            r'\+MGNSSURC: "state","\d+"'
        ],
        'error_codes': {
            1: 'GNSS状态异常',
            2: 'GNSS存储错误',
            3: 'GNSS启动错误',
            4: 'AGNSS辅助数据无效',
            5: 'AGNSS服务器连接异常',
            6: 'AGNSS辅助数据获取异常',
            7: 'DGNSS服务器连接异常',
            8: 'DGNSS服务器鉴权异常',
            9: 'DGNSS差分数据获取异常'
        },
        'state_codes': {
            0: 'GNSS已关闭',
            1: 'GNSS已开启'
        },
        'not_supported_models': [],
        'notes': [
            '异步错误信息自动上报',
            '无需主动发送命令'
        ]
    }
    return mgnssurc


def get_gnss_error_codes():
    """
    GNSS命令相关的错误码
    """
    error_codes = {
        'command': 'GNSS_ERROR_CODES',
        'error_codes': {
            950: '未知错误',
            951: 'GNSS参数错误',
            952: 'GNSS已开启',
            953: 'GNSS未开启',
            954: 'GNSS状态忙',
            955: 'AGNSS状态忙',
            956: 'DGNSS状态忙',
            957: 'GNSS设备错误',
            958: 'GNSS操作内存失败',
            959: 'GNSS请求失败',
            960: 'AGNSS已开启',
            961: 'AGNSS未开启',
            962: 'DGNSS已开启',
            963: 'DGNSS未开启'
        },
        'notes': [
            '错误码范围：950-963',
            '用于解析+CME ERROR响应'
        ]
    }
    return error_codes