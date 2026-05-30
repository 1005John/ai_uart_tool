import re


def set_mlpmcfg(cmd, psind_enable=None, sleepind_report=None, sleep_mode=None, permanent=None, delay_sleep=None,
                enable=None):
    """
    AT+MLPMCFG - 低功耗管理配置
    """
    # 根据不同的cmd构建发送数据
    if cmd == "psind":
        if psind_enable is None:
            send_data = 'AT+MLPMCFG="psind"'
        else:
            send_data = f'AT+MLPMCFG="psind",{psind_enable}'
    elif cmd == "sleepind":
        if sleepind_report is None:
            send_data = 'AT+MLPMCFG="sleepind"'
        else:
            send_data = f'AT+MLPMCFG="sleepind",{sleepind_report}'
    elif cmd == "sleepmode":
        if sleep_mode is None:
            send_data = 'AT+MLPMCFG="sleepmode"'
        elif permanent is None:
            send_data = f'AT+MLPMCFG="sleepmode",{sleep_mode}'
        else:
            send_data = f'AT+MLPMCFG="sleepmode",{sleep_mode},{permanent}'
    elif cmd == "delaysleep":
        if delay_sleep is None:
            send_data = 'AT+MLPMCFG="delaysleep"'
        else:
            send_data = f'AT+MLPMCFG="delaysleep",{delay_sleep}'
    elif cmd == "dtr":
        if enable is None:
            send_data = 'AT+MLPMCFG="dtr"'
        else:
            send_data = f'AT+MLPMCFG="dtr",{enable}'
    else:
        send_data = f'AT+MLPMCFG="{cmd}"'

    mlpmcfg_config = {
        'command': 'AT+MLPMCFG',
        'send_data': send_data,
        'search_data': 'AT+MLPMCFG=?',
        'cmd_range': ("psind", "sleepind", "sleepmode", "delaysleep", "dtr"),

        # 修正后的型号支持范围
        'supported_projects': {
            'psind': {
                'supported': [
                    'M5310-E', 'MN328', 'MN318',  # NB-IoT系列
                    'ML307B'  # 4G系列
                ],
                'not_supported': [
                    'MN316', 'MN316-S', 'MN316A', 'MN326A', 'MN326',  # NB-IoT不支持
                    'ML302S', 'ML307S', 'ML302A', 'ML307A', 'ML307R', 'ML307C',
                    'ML305A', 'ML307G', 'ML307H',  # 4G系列不支持
                    'ML305U', 'ML305M', 'ML307M', 'ML307N'  # 仅支持sleepmode
                ]
            },
            'sleepind': {
                'supported': [
                    'MN316', 'MN316-S', 'MN316A', 'MN326A', 'MN326',  # NB-IoT
                    'ML302S', 'ML307S', 'ML302A', 'ML307A', 'ML307R', 'ML307C',
                    'ML305A', 'ML307G', 'ML307H', 'ML307B',  # 4G系列
                    'ML307X', 'ML307Y'  # 特殊4G系列
                ],
                'not_supported': [
                    'M5310-E', 'MN328', 'MN318',  # NB-IoT不支持
                    'ML305U', 'ML305M', 'ML307M', 'ML307N'  # 仅支持sleepmode
                ]
            },
            'sleepmode': {
                'supported': ['ALL'],  # 所有型号都支持
                'not_supported': []
            },
            'delaysleep': {
                'supported': [
                    'MN316', 'MN316-S', 'MN316A', 'MN326A', 'MN326',  # NB-IoT
                    'ML302S', 'ML307S', 'ML302A', 'ML307A', 'ML307R', 'ML307C',
                    'ML305A', 'ML307G', 'ML307H', 'ML307B',  # 4G系列
                    'ML307X', 'ML307Y'  # 特殊4G系列
                ],
                'not_supported': [
                    'M5310-E', 'MN328', 'MN318',  # NB-IoT不支持
                    'ML305U', 'ML305M', 'ML307M', 'ML307N'  # 仅支持sleepmode
                ]
            },
            'dtr': {
                'supported': ['ML307X', 'ML307Y'],  # 仅特殊4G系列支持
                'not_supported': ['ALL_OTHERS']  # 其他所有型号不支持
            }
        },

        'psind_enable_range': (0, 1),

        # 修正后的sleepind_report范围
        'sleepind_report_range': {
            'default': [0, 3],
            'MN316/MN316-S/MN316A/MN326A/MN327/MN319/MN319-A/MN326': [0, 2],
            'ML302S/ML307S/ML302A/ML307A/ML307R/ML307C/ML305A/ML307G/ML307H/ML307B': [0, 2],
            'ML307X/ML307Y': [0, 1]
        },

        # 修正后的sleep_mode范围
        'sleep_mode_range': {
            'default': [0, 2],
            'M5310-E/MN327/MN328/MN318': [0, 2],
            'MN319/MN319-A': [1, 2],
            'ML302S/ML307S/ML302A/ML307A/ML307R/ML307C/ML305A/ML305U/ML305M/ML307G/ML307H/ML307M/ML307N/ML307B': [0, 2],
            'ML307X/ML307Y': [0, 1]
        },

        'permanent_range': (0, 1),

        # 修正后的delay_sleep范围
        'delay_sleep_range': {
            'default': [0, 300],
            'MN316/MN316-S/MN319/MN319-A/MN316A/MN326A/MN327/MN326': [1, 255],
            'ML307X/ML307Y': [0, 255]
        },

        'enable_range': (0, 1),

        'default_values': {
            'cmd': "psind",
            'psind_enable': None,
            'sleepind_report': None,
            'sleep_mode': None,
            'permanent': None,
            'delay_sleep': None,
            'enable': None
        },

        'result': [r'OK'],
        'search_result': [r'OK', rf'\+MLPMCFG: "{re.escape(cmd)}",.+'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+'],

        'urc_results': {
            'sleepind': [r'\+MLPMENTER: \d+', r'\+MLPMEXIT: \d+'],
            'psind': [r'\+MLPMPSTA: \d+']
        },

        # 修正后的特殊备注
        'special_notes': {
            'MF308C/MR880A/MF572E': '不支持该命令',
            'ML551Z': '不支持该命令',
            'ML307N': '允许系统进入睡眠时，AT串口使用波特率大于115200场景下，不支持AT命令唤醒系统',
            'ML307H': '延迟休眠仅通过串口唤醒有效，并且需要小于等于115200波特率下才能够唤醒',
            'ML307X/ML307Y': '解锁睡眠锁定的命令，无延迟进入睡眠时间，条件满足会立即进入睡眠',
            'ML307B': 'permanent配置为1时，需要执行AT+MREBOOT才能保存成功',
            'MN319/MN319-A': '仅支持permanent=1，且参数不可省略'
        }
    }
    return mlpmcfg_config



