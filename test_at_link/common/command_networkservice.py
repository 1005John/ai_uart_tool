def set_cops(mode=0, format=2, oper="", act=""):
    """
    AT+COPS Operator Selection
    用于选择运营商

    Args:
        mode: 选择模式 (0:自动, 1:手动, 2:注销, 3:仅设置格式, 4:手动/自动)
        format: 运营商格式 (0:长字母数字, 1:短字母数字, 2:数字)
        oper: 运营商字符串
        act: 接入技术
    """

    # 构建发送数据
    if mode in [1, 4]:  # 手动模式需要oper参数
        if act:
            send_data = f'AT+COPS={mode},{format},"{oper}",{act}'
        else:
            send_data = f'AT+COPS={mode},{format},"{oper}"'
    elif mode == 0:  # 自动模式
        if act:
            send_data = f'AT+COPS={mode},{format},,{act}'
        else:
            send_data = f'AT+COPS={mode}'
    elif mode == 2:  # 注销模式
        send_data = f'AT+COPS={mode}'
    elif mode == 3:  # 仅设置格式
        send_data = f'AT+COPS={mode},{format}'
    else:
        send_data = f'AT+COPS={mode}'

    cops_config = {
        'command': 'AT+COPS',
        'send_data': send_data,
        'search_data': 'AT+COPS?',
        'mode_range': {
            'default': [0, 4],
            'M5310-E/MN318/MN328': [0, 1, 2],
            'MN316/MN316A/MN326A/MN326': [0, 1, 4],
            'ML305M/ML307M/ML307N/ML551Z': [3],
            'ML307B': [0, 1, 2, 3],
            'MF308C': [0, 1, 2, 3],
            'MR880A': [0, 1, 2, 3, 4]
        },
        'format_range': {
            'default': [0, 1, 2],
            'M5310-E/MN316/MN318/MN316A/MN326A/MN326/MN328': [2]
        },
        'act_range': {
            'default': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13],
            'M5310-E/MN316/MN318/MN316A/MN326A/MN326/MN327/MN328/MN319/MN319-A': [9],
            'ML302S/ML307S/ML302A/ML305A/ML307A/ML307R/ML307B/ML307C/ML305U': [0, 2, 3, 4, 5, 6, 7],
            'ML307G/ML307H': [0, 2, 7],
            'ML305M/ML307M/ML307N/ML307X/ML307Y': [7],
            'MF308C': [0, 2, 3, 4, 5, 6, 7],
            'MR880A': [0, 2, 7, 12, 13]
        },
        'oper_max_len': {
            'long_format': 16,
            'short_format': 8
        },
        'stat_range': (0, 1, 2, 3),  # 0:未知, 1:可用, 2:当前, 3:禁止
        'default_values': {
            'mode': 0,
            'format': 2,
            'oper': "",
            'act': ""
        },
        'special_notes': {
            'ML305M/ML307M': '执行测试命令前需要先使用AT+CMCACT=0,1断开终端拨号状态',
            'M5310-E/MN318/MN328': '命令执行需要时间，响应时间不超过10分钟',
            'MN316/MN316A/MN326A/MN326': '异步命令，搜索过程在后台运行，只能在空闲状态下执行',
            'MN319/MN319-A': 'AT+COPS=?响应时间不超过5分钟，设置命令响应时间不超过2分钟',
            'MR880A': '仅在空闲或非驻留状态下可用，激活状态下会报错'
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+COPS: {mode}(?:,{format},"{re.escape(oper)}"(?:,{act})?)?'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return cops_config


def set_creg(n=1):
    """
    AT+CREG Network registration
    用于查询注册状态

    Args:
        n: 网络注册状态码显示控制 (0:禁用, 1:启用基本状态, 2:启用状态和位置信息, 3:启用状态、位置和原因值信息)
    """

    creg_config = {
        'command': 'AT+CREG',
        'send_data': f'AT+CREG={n}',
        'search_data': 'AT+CREG?',
        'n_range': {
            'default': [0, 3],
            'MR880A': [0, 2],
            'ML551Z': [0, 1, 2]
        },
        'stat_range': {
            'default': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'ML307X/ML307Y': [0, 1, 2, 3, 4, 5],
            'MR380R': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
        },
        'act_range': {
            'default': [0, 1, 2, 3, 4, 5, 6, 7, 8],
            'ML302S/ML307S/ML302A/ML305A/ML307A/ML305U': [0, 2, 3, 4, 5, 6, 7],
            'ML307G/ML307H': [0, 2, 7],
            'ML307X/ML307Y/ML307B': [7]
        },
        'default_values': {
            'n': 1
        },
        'special_notes': {
            'ML302A-DCLM/ML302A-GCLM/ML305A-DC/ML305A-DL/ML307A-DCLN/ML307A-GCLN/ML307R/ML307C/ML305U/ML305M/ML307M/ML307N': '不支持此命令',
            'MR380M': '不支持此命令'
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+CREG: {n},\d+(?:,"[0-9A-F]+","[0-9A-F]+",\d+)?(?:,\d+,\d+)?'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return creg_config


def set_cpol(index=1, format=2, oper="", gsm_act=0, gsm_compact_act=0, utran_act=0, e_utran_act=0, ng_ran_act=0):
    """
    AT+CPOL Preferred operator list
    用于编辑用户首选网络列表

    Args:
        index: 运营商在列表中的序号
        format: 运营商格式 (0:长字母数字, 1:短字母数字, 2:数字)
        oper: 运营商字符串
        gsm_act: GSM接入技术选择 (0:未选择, 1:选择)
        gsm_compact_act: GSM Compact接入技术选择
        utran_act: UTRAN接入技术选择
        e_utran_act: E-UTRAN接入技术选择
        ng_ran_act: NG-RAN接入技术选择
    """

    # 构建发送数据
    params = [str(index)]
    if format is not None:
        params.append(str(format))
        if oper:
            params.append(f'"{oper}"')
            if gsm_act is not None:
                params.extend([str(gsm_act), str(gsm_compact_act), str(utran_act), str(e_utran_act), str(ng_ran_act)])

    send_data = f'AT+CPOL={",".join(params)}'

    cpol_config = {
        'command': 'AT+CPOL',
        'send_data': send_data,
        'search_data': 'AT+CPOL?',
        'index_range': {
            'default': [1, 10]  # 假设默认支持10个条目
        },
        'format_range': {
            'default': [0, 2]
        },
        'act_selection_range': (0, 1),  # 0:未选择, 1:选择
        'default_values': {
            'index': 1,
            'format': 2,
            'oper': "",
            'gsm_act': 0,
            'gsm_compact_act': 0,
            'utran_act': 0,
            'e_utran_act': 0,
            'ng_ran_act': 0
        },
        'special_notes': {
            'ML302S/ML307S/ML302A/ML305A/ML307R/ML307B/ML307C/ML307A/ML307G/ML307H/ML307X/ML307Y': '不支持同时选择多个接入技术参数',
            'ML305M/ML307M/ML307N/ML551Z': '写入用户控制的PLMN选择器时需要所有接入技术参数',
            'ML551Z': '请在PDP去激活状态下删除PLMN列表',
            'MR380M': '不支持此命令'
        },
        'result': [r'OK'],
        'search_result': [r'OK',
                          rf'\+CPOL: {index},{format},"{re.escape(oper)}"(?:,{gsm_act},{gsm_compact_act},{utran_act},{e_utran_act}(?:,{ng_ran_act})?)?'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return cpol_config


def set_cpls(list=0):
    """
    AT+CPLS Selection of preferred PLMN list
    用于选择SIM/USIM中的首选PLMN列表

    Args:
        list: 列表类型 (0:用户控制, 1:运营商控制, 2:HPLMN选择器)
    """

    cpls_config = {
        'command': 'AT+CPLS',
        'send_data': f'AT+CPLS={list}',
        'search_data': 'AT+CPLS?',
        'list_range': (0, 1, 2),
        'default_values': {
            'list': 0
        },
        'special_notes': {
            'MN316/MN316A/MN326A/M5310-E/MN328/MN319/MN319-A/MN318/MN326': '不支持此命令',
            'MF308C': '不支持测试命令',
            'ML302S/ML307S/ML307X/ML307Y': '不支持此命令'
        },
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+CPLS: {list}'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return cpls_config


def set_copn():
    """
    AT+COPN Read operator names
    用于读取运营商名称
    """

    copn_config = {
        'command': 'AT+COPN',
        'send_data': 'AT+COPN',
        'search_data': None,  # 执行命令即为查询，无单独的查询命令
        'default_values': {},
        'special_notes': {
            'ML305M/ML307M/ML307N': '不支持此命令',
            'MR880A/MR380M/MR380R': '不支持此命令'
        },
        'result': [r'OK', r'\+COPN: "[0-9]+","[^"]*"'],
        'search_result': None,
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return copn_config


def set_clck(fac="SC", mode=2, passwd="", class_param=""):
    """
    AT+CLCK Facility lock command
    用于锁定、解锁或查询ME或网络设施
    """

    # 构建发送数据
    if mode == 2:  # 查询命令
        send_data = f'AT+CLCK="{fac}",{mode}'
    else:  # 设置命令需要密码
        if class_param:
            send_data = f'AT+CLCK="{fac}",{mode},"{passwd}",{class_param}'
        else:
            send_data = f'AT+CLCK="{fac}",{mode},"{passwd}"'

    clck_config = {
        'command': 'AT+CLCK',
        'send_data': send_data,
        'search_data': f'AT+CLCK="{fac}",2',  # 查询命令格式

        # 参数取值范围
        'fac_range': {
            'default': ["SC"]
        },
        'mode_range': (0, 1, 2),
        'class_range': {
            'default': [1, 7]  # 根据GSM标准，class范围通常是1-7
        },

        # 参数说明
        'fac_types': {
            'SC': 'SIM卡锁定（SIM在ME开机和锁定命令发出时要求密码）'
        },
        'mode_types': {
            0: '解锁',
            1: '锁定',
            2: '查询状态'
        },

        # 默认值
        'default_values': {
            'fac': "SC",
            'mode': 2,
            'passwd': "",
            'class_param': ""
        },

        # 型号支持情况
        'not_supported_models': [
            'ML302A', 'ML305A', 'ML307A', 'ML307R', 'ML307B', 'ML307C',
            'ML302S', 'ML307S', 'ML305U', 'MR880A'
        ],

        # 响应结果匹配
        'result': [r'OK'],
        'search_result': [r'OK', rf'\+CLCK: \d+(?:,\d+)*'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }

    return clck_config



def set_chld(n=0):
    """
    AT+CHLD - Call related supplementary services
    用于控制呼叫相关服务，包括呼叫保持、多方通话、呼叫转移等
    """

    chld_config = {
        'command': 'AT+CHLD',
        'send_data': f'AT+CHLD={n}',
        'search_data': 'AT+CHLD=?',
        'n_range': {
            'default': [0, 1, 2, 3],
            'ML302A/ML305A/ML307A/ML307R/ML307B/ML307C/ML305U/ML305M/ML307M/ML307N/ML307X/ML307Y': [] , # 不支持该命令
            'ML307A-DSLN': [0, 1, 2, 3]
        },
        'n_values': {
            0: '释放所有保持呼叫或设置UDUB',
            1: '释放所有活动呼叫并接受其他保持呼叫',
            2: '保持活动呼叫并接受其他保持呼叫',
            3: '添加保持呼叫到会议'
        },
        'not_supported_models': [
            'ML302A', 'ML305A', 'ML307A', 'ML307R', 'ML307B', 'ML307C', 'ML305U',
            'ML305M', 'ML307M', 'ML307N', 'ML307X', 'ML307Y'
        ],
        'default_values': {
            'n': 0
        },
        'result': [r'OK'],
        'search_result': [r'OK', r'\+CHLD: \(.*\)'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+'],
        'special_notes': {
            'general': '该命令基于HOLD(呼叫保持)、MPTY/CONF(多方通话)和ECT(显式呼叫转移)补充服务',
            'limitation': '在CS域中，呼叫保持、多方通话和显式呼叫转移仅适用于电信业务11',
            'implementation': '可选实现，当+CHLD命令实现时推荐实现'
        }
    }

    return chld_config


def set_clcc():
    """
    AT+CLCC - List current calls of ME
    返回MT的当前呼叫列表
    """

    clcc_config = {
        'command': 'AT+CLCC',
        'send_data': 'AT+CLCC',
        'search_data': 'AT+CLCC=?',
        'default_values': {
            # 该命令无设置参数，只有查询功能
        },
        'response_format': {
            'ccidx': {
                'description': '呼叫标识号',
                'range': [1, 'N'],  # N为最大同时呼叫控制进程数，实现特定
                'type': 'integer'
            },
            'dir': {
                'description': '呼叫方向',
                'values': (0, 1),
                'meaning': {
                    0: '移动台发起呼叫(MO)',
                    1: '移动台终止呼叫(MT)'
                }
            },
            'stat': {
                'description': '呼叫状态',
                'values': (0, 1, 2, 3, 4, 5),
                'meaning': {
                    0: '活跃',
                    1: '保持',
                    2: '拨号中(MO呼叫)',
                    3: '振铃中(MO呼叫)',
                    4: '来电中(MT呼叫)',
                    5: '等待中(MT呼叫)'
                }
            },
            'mode': {
                'description': '承载/电信业务类型',
                'values': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
                'meaning': {
                    0: '语音',
                    1: '数据',
                    2: '传真',
                    3: '语音后接数据，语音模式',
                    4: '交替语音/数据，语音模式',
                    5: '交替语音/传真，语音模式',
                    6: '语音后接数据，数据模式',
                    7: '交替语音/数据，数据模式',
                    8: '交替语音/传真，传真模式',
                    9: '未知'
                },
                'supported_models': {
                    'ML302S/ML307S/ML302A/ML305A/ML307A': [1, 2, 3]
                }
            },
            'mpty': {
                'description': '多方通话标识',
                'values': (0, 1),
                'meaning': {
                    0: '不是多方通话(会议)呼叫的一方',
                    1: '是多方通话(会议)呼叫的一方'
                }
            },
            'number': {
                'description': '电话号码',
                'type': 'string',
                'format': '<type>指定的格式'
            },
            'type': {
                'description': '地址八位组类型',
                'type': 'integer',
                'reference': '3GPP TS 24.008子条款10.5.4.7'
            },
            'alpha': {
                'description': '号码的字母数字表示',
                'type': 'string'
            },
            'priority': {
                'description': 'eMLPP优先级级别',
                'type': 'integer',
                'reference': '3GPP TS 22.067'
            },
            'CLI_validity': {
                'description': 'CLI有效性',
                'values': (0, 1, 2, 3, 4),
                'meaning': {
                    0: 'CLI有效',
                    1: 'CLI已被发起方保留',
                    2: 'CLI由于互通问题或发起网络限制不可用',
                    3: 'CLI由于呼叫方为付费电话类型不可用',
                    4: 'CLI由于其他原因不可用'
                }
            }
        },
        'not_supported_models': [
            'ML302A-DCLM', 'ML302A-GCLM', 'ML305A-DC', 'ML305A-DL',
            'ML307A-DCLN', 'ML307A-GCLN', 'ML307R', 'ML307B', 'ML307C',
            'ML305U', 'ML305M', 'ML307M', 'ML307N', 'ML307H', 'ML307G-DL',
            'ML307X', 'ML307Y', 'MF308C', 'MR880A', 'MR380R', 'MR380M'
        ],
        'result': [
            r'OK',
            r'\+CLCC: \d+,\d+,\d+,\d+,\d+(?:,"[^"]*",\d+(?:,"[^"]*")?(?:,\d+)?(?:,\d+)?)?'
        ],
        'search_result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+'],
        'special_notes': {
            'general': '如果命令成功但没有可用呼叫，则不向TE发送信息响应',
            'implementation': '可选实现，当+CHLD命令实现时推荐实现',
            'replacement': '当支持+CDU并且MT中使用SIP URI时，AT命令+CLCC完全被+CLCCS替换',
            'CLI_handling': '当CLI不可用时，<number>应为空字符串""，<type>值不显著'
        },
        'response_patterns': {
            'single_call': r'\+CLCC: (\d+),(\d+),(\d+),(\d+),(\d+)(?:,"([^"]*)",(\d+)(?:,"([^"]*)")?(?:,(\d+))?(?:,(\d+))?)?',
            'multiple_calls': r'(\+CLCC: \d+,\d+,\d+,\d+,\d+(?:,"[^"]*",\d+(?:,"[^"]*")?(?:,\d+)?(?:,\d+)?)?(?:\r\n\+CLCC: \d+,\d+,\d+,\d+,\d+(?:,"[^"]*",\d+(?:,"[^"]*")?(?:,\d+)?(?:,\d+)?)?)*)'
        }
    }

    return clcc_config