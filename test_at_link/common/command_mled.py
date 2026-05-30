def set_mled(led_mode, enable=None):
    """
    AT+MLED - 开关指示灯功能
    """
    if enable is None:
        send_data = f'AT+MLED={led_mode}'
    else:
        send_data = f'AT+MLED={led_mode},{enable}'

    mled = {
        'command': 'AT+MLED',
        'send_data': send_data,
        'search_data': 'AT+MLED=?',
        'led_mode_range': {
            'default': [0, 1],
            'M5310-E/MN318/MN328/MF308C/MR880A': [0, 0]
        },
        'enable_range': (0, 1),
        'default_values': {
            'led_mode': 0,
            'enable': 0
        },
        'special_notes': {
            'ML307S/ML551Z': '暂不支持该命令',
            'MF572E': '暂不支持该命令',
            'MN316-S-DLVS': '不支持运行状态指示灯'
        },
        'result': [r'OK'],
        'search_result': [r'OK', r'\+MLED: .*'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }
    return mled