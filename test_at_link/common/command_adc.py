import re


def set_madc(channel=0):
    """
    AT+MADC - 读取ADC电压值（设置指令）
    参数说明：
    channel: ADC通道编号，整型，默认值0
    """

    madc = {
        'command': 'AT+MADC',
        'send_data': f'AT+MADC={channel}',
        'search_data': f'AT+MADC={channel}',
        'channel_range': {
            'default': [0, 1],
            'MN316/MN316-S/MN328/MN327/MN316A/MN326A/MN319/MN319-A/MN326/ML307A/ML307M/MF308C': [0, 0],
            'ML305A/ML305U/ML305M/ML307N/ML307R/ML307C/ML307X/ML307Y/MR880A': [0, 1],
            'MF572E': [1, 1]  # MF572E不支持ADC0
        },
        'not_supported_models': ['ML302S', 'ML307S', 'ML551Z'],
        'not_supported_default_param': ['ML302A', 'ML305A', 'ML307A', 'ML307R', 'ML307C', 'ML307G', 'ML307H', 'MF572E'],
        'channel_type': 'ADC通道编号',
        'default_values': {
            'channel': 0
        },
        'voltage_range': {
            'description': '测量范围取决于VBAT和硬件设计，通常为0~min(VBAT, 3.3V)',
            'unit': 'mV'
        },
        'special_notes': {
            'MN319/MN319-A': 'ADC输入范围为0~min(VBAT, 3.3V)，VBAT≥3.3V时测量范围0~3300mV，VBAT<3.3V时测量范围0~VBAT(mV)',
            'ML302A': '唯一支持ADC3的型号（属于medium类别）',
            'MF572E': '不支持ADC0，必须指定有效通道',
            'general': '电压读数受电源噪声、参考电压稳定性、外部电路分压等因素影响，建议多次采样取平均'
        },
        'result': [r'OK', rf'\+MADC: \d+'],
        'search_result': [r'OK', rf'\+MADC: \d+'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return madc


def query_madc_support():
    """
    AT+MADC=? - 测试指令（查询支持的ADC通道范围）
    """

    madc_query = {
        'command': 'AT+MADC=?',
        'send_data': 'AT+MADC=?',
        'result': [r'\+MADC: \([0-9\-]+\)', r'OK'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+'],
        'response_format': '返回支持的通道范围，如：(0-1)'
    }
    return madc_query


def get_madc_read_method(channel=0):
    """
    生成ADC读取的业务方法（类似mqtt_subtopic的业务逻辑）
    校验程度：返回结果校验OK和电压值
    """

    madc_method = {
        'command': 'AT+MADC',
        'send_data': f'AT+MADC={channel}',
        'expected_patterns': [
            r'OK',
            rf'\+MADC: \d+'
        ],
        'checklist': {
            'success_checks': [r'OK', rf'\+MADC: \d+'],
            'error_checks': [r'\+CME ERROR: [0-9A-Za-z]+']
        },
        'validation_rules': {
            'voltage_format': r'\d+',  # 电压值为数字
            'voltage_range_check': '根据VBAT电压范围验证读数合理性'
        },
        'business_logic': '读取指定ADC通道的电压值，返回数值用于后续处理'
    }
    return madc_method


def create_madc_test_sequence(channels=[0]):
    """
    创建ADC测试序列方法（批量测试多个通道）
    """

    test_sequence = {
        'test_cases': [],
        'validation_strategy': '逐个通道测试，验证返回的电压值格式和范围',
        'expected_results': {
            'format': 'OK +MADC: <voltage>',
            'voltage_pattern': r'\d+'
        }
    }

    for channel in channels:
        test_case = {
            'channel': channel,
            'send_data': f'AT+MADC={channel}',
            'expected_response': [r'OK', rf'\+MADC: \d+'],
            'error_response': [r'\+CME ERROR: [0-9A-Za-z]+'],
            'validation': f'验证通道{channel}的ADC读数格式正确'
        }
        test_sequence['test_cases'].append(test_case)

    return test_sequence