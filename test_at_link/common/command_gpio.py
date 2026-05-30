import re


def set_mgpio(pin=34, ctrl=0, mode=0):
    """
    AT+MGPIO - 控制GPIO
    用于配置GPIO模式和输出电平，读取GPIO状态
    """

    # 构建发送数据
    if ctrl == 0:
        # 读取模式
        send_data = f'AT+MGPIO={pin},{ctrl}'
        search_data = f'AT+MGPIO={pin}'
    elif ctrl == 3:
        # 高阻态模式，不设置mode参数
        send_data = f'AT+MGPIO={pin},{ctrl}'
        search_data = f'AT+MGPIO={pin}'
    else:
        # 输出模式，设置mode参数
        send_data = f'AT+MGPIO={pin},{ctrl},{mode}'
        search_data = f'AT+MGPIO={pin}'

    mgpio = {
        'command': 'AT+MGPIO',
        'send_data': send_data,
        'search_data': search_data,
        'pin_range': {
            'default': [0, 49],
            'MN316/MN316-S': [16, 17],
            'MN316A/MN326A/M5311-E': [34, 35],
            'MN319/MN319-A':[7,34,35],
            'M5310-E': [9, 14, 17, 20, 22],
            'MN318': [11, 16, 18, 19, 33, 34, 35, 39, 40, 41, 42],
            'ML302S': [2, 7, 31, 35, 42, 43, 44, 45, 46],
            'ML302A': [0,1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
            'ML307A/ML307R-DC/ML307R-DL/ML307M-DL/ML307M-DH': [0, 3],
            'ML307C': [0, 2],
            'ML307M-DA': [0, 1, 3],
            'ML307R-BC/ML307R-BL': [0, 1, 2, 3, 4],
            'ML305U': [0,1,2,3,4,5,6,7,8,9,10, 11, 12, 13, 14, 15],
            'ML305M': [1, 2, 7, 8, 9, 10],
            'ML307G-DL/ML307N': [0, 3],
            'ML307G-BL': [0, 1],
            'ML307H-GU/ML307H-GC': [0, 1, 2],
            'ML307H-DU/ML307H-MU/ML307H-DC/ML307X/ML307Y': [0,1,2, 3],
            'MF308C': [153,154,155, 156],
            'MR880A': [23],
            'MF572E': [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23, 24]
        },
        'ctrl_range': {
            'default': [0, 3],
            'MR880A': [1, 2],
            'MN316/MN316-S/MN316A/MN326A/M5311-E/MN319/MN319-A/ML302S/ML302A/ML307A/ML307R/ML307C/ML305M/ML307G/ML307H/ML307X/ML307Y/ML307M/ML307N/MF308C/MF572E': [
                0, 2]  # 不支持高阻态
        },
        'mode_range': {
            'default': [0, 2],
            'MN316-S': {'16': [0, 1], '17': [0, 2]},  # Pin 16不支持上拉，Pin 17不支持下拉
            'MN316': {'34': [0, 1], '35': [0, 2]},  # Pin 34不支持上拉，Pin 35不支持下拉
            'M5311-E/MR880A/MF572E': []  # 不支持mode参数配置
        },
        'ctrl_description': {
            0: '读取输入',
            1: '输出低电平',
            2: '输出高电平',
            3: '高阻态'
        },
        'mode_description': {
            0: '浮空',
            1: '下拉',
            2: '上拉'
        },
        'not_supported_products': {
            'ML307S/ML305A/ML551Z': '不支持该命令',
            'MN327/MN328/MN326': '不支持该命令'
        },
        'default_values': {
            'pin': 34,
            'ctrl': 0,
            'mode': 0
        },
        'special_notes': {
            'MN316-S': 'MN316-S-DLVS支持Pin 16和Pin 17；Pin 16默认下拉输入，Pin 17默认上拉输入',
            'MN316': 'Pin 34默认下拉输入，Pin 35默认上拉输入',
            'MN316A/MN326A': '默认均为下拉输入',
            'M5310-E': '默认为上拉输入',
            'MN318': '默认为上拉输入',
            'MN319/MN319-A': '默认下拉输入'
        },
        'result': [r'OK'],
        'search_result': [r'OK'],
        'err_result': [r'\+CME ERROR: [0-9A-Za-z]+']
    }

    # 根据ctrl值构建不同的响应模式
    if ctrl == 0:
        # 读取模式：+MGPIO: pin,value
        mgpio['result'].append(rf'\+MGPIO: {pin},[01]')
        mgpio['search_result'].append(rf'\+MGPIO: {pin},[01]')
    elif ctrl == 3:
        # 高阻态模式：OK
        mgpio['search_result'].append(rf'\+MGPIO: {pin},{ctrl}')
    else:
        # 设置模式：+MGPIO: pin,ctrl,mode 或 OK
        mgpio['search_result'].append(rf'\+MGPIO: {pin},{ctrl},{mode}')

    return mgpio

def gpio_control(self, pin=34, ctrl=0, mode=0):
        """
        GPIO控制方法 - 参考mqtt_subtopic的业务逻辑
        校验程度：返回的都校验 OK 和对应的响应
        """
        # 获取GPIO配置数据
        gpio_data = set_mgpio(pin, ctrl, mode)

        # 发送AT指令
        self.serial_manager.send_at_command(gpio_data['send_data'])

        # 等待响应，根据不同的ctrl模式构建检查列表
        if ctrl == 0:
            # 读取模式：检查OK和读取结果
            gpio_res = self.serial_manager.wait_for_regex(
                pattern=gpio_data['result'],
                checklist=self.right_error_check + [rf'\+MGPIO: {pin},[01]']
            )
        elif ctrl == 3:
            # 高阻态模式：只检查OK
            gpio_res = self.serial_manager.wait_for_regex(
                pattern=gpio_data['result'],
                checklist=self.right_error_check
            )
        else:
            # 设置模式：检查OK和设置确认
            gpio_res = self.serial_manager.wait_for_regex(
                pattern=gpio_data['result'],
                checklist=self.right_error_check + [rf'\+MGPIO: {pin},{ctrl},{mode}']
            )

        return gpio_res

def gpio_read_level(self, pin=34):
        """
        专门用于读取GPIO电平值的方法
        """
        return self.gpio_control(pin=pin, ctrl=0)

def gpio_set_output_high(self, pin=34, mode=0):
        """
        设置GPIO输出高电平
        """
        return self.gpio_control(pin=pin, ctrl=2, mode=mode)

def gpio_set_output_low(self, pin=34, mode=0):
        """
        设置GPIO输出低电平
        """
        return self.gpio_control(pin=pin, ctrl=1, mode=mode)

def gpio_set_high_z(self, pin=34):
        """
        设置GPIO为高阻态
        """
        return self.gpio_control(pin=pin, ctrl=3)

def gpio_query_config(self, pin=34):
        """
        查询GPIO配置
        """
        gpio_data = set_mgpio(pin=pin)

        # 发送查询指令
        self.serial_manager.send_at_command(gpio_data['search_data'])

        # 等待查询响应
        query_res = self.serial_manager.wait_for_regex(
            pattern=gpio_data['search_result'],
            checklist=self.right_error_check + [rf'\+MGPIO: {pin},\d+,\d+']
        )

        return query_res