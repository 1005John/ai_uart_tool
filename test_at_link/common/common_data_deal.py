import yaml
import os
import random
import string
import math
import re
import pandas as pd
import numpy as np
import ast
import math
import json
import pytest
def _should_include_project(projects_list, target_project):
    """
    判断目标项目是否应该被包含

    :param projects_list: 项目列表
    :param target_project: 目标项目
    :return: 是否应该包含该项目
    """
    # print(f'当前的项目列表是{projects_list}，类型是{type(projects_list)}')
    # print(f'当前查找的项目列表{target_project}，类型是{type(target_project)}')
    if not isinstance(projects_list, list)  or projects_list is None:
        # print(1111111111111)
        return False

    for project_entry in projects_list:
        # print(f'当前项目是{project_entry}，类型是{type(project_entry)}')
        # print(f'查找的项目是{target_project[0]}，查找的子项目是{target_project[1]}')
        if project_entry == "ALL":
            # print("当前项目是ALL")
            return True
        elif project_entry.startswith("ALL|"):
            # 处理 ALL|排除项目 格式
            excluded_projects = project_entry.split("|")[1].split("/")
            # print(f'排除项目列表是{excluded_projects}，类型是{type(excluded_projects)}')
            # 如果目标项目不在排除列表中，则包含
            if target_project[0] in excluded_projects or target_project[1] in excluded_projects:
                return False
                # 处理普通项目名称
            else:
                return True
        elif target_project[0] == project_entry or target_project[1] == project_entry:

            return True

    # return False

def _evaluate_using_split(s: str) -> str:
    """
    使用简单分割的方法，针对特定格式
    只处理格式严格的 '"x"*n' 或 "'x'*n"
    """
    s = s.strip()

    # 检查是否是单引号或双引号格式
    if (s.startswith('"') and s.count('"') == 2) or (s.startswith("'") and s.count("'") == 2):
        if '*' in s:
            # 分割引号内的内容和数字
            quote_char = s[0]

            # 找到第二个引号的位置
            second_quote = s.find(quote_char, 1)
            if second_quote == -1:
                return s

            # 找到*的位置
            asterisk_pos = s.find('*', second_quote)
            if asterisk_pos == -1:
                return s

            # 提取各部分
            string_content = s[1:second_quote]
            num_part = s[asterisk_pos + 1:].strip()

            # 验证数字部分
            if num_part.isdigit():
                # 验证整个字符串格式是否完全匹配
                expected = f'{quote_char}{string_content}{quote_char}*{num_part}'
                if s == expected:
                    return string_content * int(num_part)

    return s
def _safe_convert_to_list(value):
    """
    安全地将字符串转换为列表，并处理列表内字符串表达式
    支持处理如 ["a"*256, "test/topic"] 这样的混合列表
    """
    if isinstance(value, str):
        # 处理空列表
        if value.strip() == '[]':
            return []

        # 检查是否是列表格式的字符串
        if value.startswith('[') and value.endswith(']'):
            try:
                # 首先尝试普通的 literal_eval（对于纯字面值列表）
                parsed_list = ast.literal_eval(value)
                if isinstance(parsed_list, list):
                    # 对列表中的每个字符串元素检查并处理表达式
                    res_list = _evaluate_list_expressions(parsed_list)
                    return res_list
            except (ValueError, SyntaxError):
                # 如果 literal_eval 失败，说明可能包含表达式
                # 手动解析列表内容
                return _parse_list_with_expressions(value)
        # 处理单个字符串表达式（非列表格式）
        else:
            return _evaluate_using_split(value)
    return value
def _evaluate_list_expressions(lst):
    """执行字符串表达式（如 'a'*256）"""
    result = []
    for item in lst:
        try:
            # 尝试解析表达式
            evaluated = ast.literal_eval(f"'{item}'")
            result.append(evaluated)
        except:
            try:
                evaluated = ast.literal_eval(f'"{item}"')
                result.append(evaluated)
            except:
                result.append(item)
    return result


def _parse_list_with_expressions(list_str):
    """
    手动解析包含表达式的列表字符串
    例如：["a"*256, "test/topic", "b"*10]
    """
    # 去掉外层的方括号
    inner_str = list_str[1:-1].strip()

    if not inner_str:
        return []

    # 手动分割列表元素
    items = []
    current_item = ""
    quote_char = None  # 当前引号字符，None 表示不在引号内
    bracket_depth = 0  # 括号深度，用于处理嵌套结构

    i = 0
    while i < len(inner_str):
        char = inner_str[i]

        if char in ('"', "'") and (i == 0 or inner_str[i - 1] != '\\'):
            # 遇到非转义的引号
            if quote_char is None:
                quote_char = char  # 进入引号
            elif quote_char == char:
                quote_char = None  # 退出引号

        elif char == '[' and quote_char is None:
            bracket_depth += 1
        elif char == ']' and quote_char is None:
            bracket_depth -= 1

        elif char == ',' and quote_char is None and bracket_depth == 0:
            # 遇到分隔符，且不在引号内，也不是嵌套列表内
            items.append(current_item.strip())
            current_item = ""
            i += 1
            # 跳过可能的空格
            while i < len(inner_str) and inner_str[i].isspace():
                i += 1
            continue

        current_item += char
        i += 1

    # 添加最后一个元素
    if current_item:
        items.append(current_item.strip())

    # 处理每个元素
    processed_items = []
    for item in items:
        # 去掉可能的引号
        if (item.startswith('"') and item.endswith('"')) or \
                (item.startswith("'") and item.endswith("'")):
            # 对于带引号的字符串，去掉引号并处理表达式
            processed_item = _evaluate_using_split(item)
        else:
            # 对于不带引号的项，尝试作为表达式处理
            processed_item = _evaluate_using_split(item)

        processed_items.append(processed_item)

    return processed_items


def _should_include_function(function_list, target_function):
    """
    判断目标功能是否应该被包含

    :param function_list: 功能列表
    :param target_function: 目标功能
    :return: 是否应该包含该功能
    """
    if not isinstance(function_list, list):
        return False

    # 如果目标功能在列表中，则包含
    if target_function in function_list:
        return True

    return False


def _should_include_level(level_list, target_levels):
    """
    判断目标级别是否应该被包含

    :param level_list: 级别（可以是字符串或列表）
    :param target_levels: 目标级别列表
    :return: 是否应该包含该级别
    """
    if not isinstance(target_levels, list):
        return False

    # 如果 level_list 是字符串，转换为单元素列表
    if isinstance(level_list, str):
        level_list = [level_list]

    # 如果 level_list 不是列表，返回 False
    if not isinstance(level_list, list):
        return False

    # 如果目标级别在列表中，则包含
    for target_level in target_levels:
        if target_level in level_list:
            return True

    return False


def read_test_cases(file_path, sheet_name=None, test_group=None, projects=[], function=None, case_level=None):
    """
    根据 sheet 名称和 test_group 读取对应的测试用例数据
    如果不传入 sheet_name，则读取所有 sheet 的数据
    如果不传入 test_group，则读取所有测试用例

    :param file_path: Excel 文件路径
    :param sheet_name: 工作表名称（可选），如果不提供则返回所有工作表的数据
    :param test_group: 测试组名称（可选），如果不提供则返回所有测试用例
    :param project: 项目名称（可选），如果不提供则返回所有项目的测试用例
    :return: 包含对应测试用例的列表
    """
    all_records = []

    if sheet_name is None:
        # 获取所有 sheet 名称
        excel_file = pd.ExcelFile(file_path, engine='openpyxl')
        sheet_names = excel_file.sheet_names
    else:
        # 只处理指定的 sheet
        sheet_names = [sheet_name]

    # 遍历所有需要处理的 sheet
    for sheet in sheet_names:
        # 读取指定 sheet，跳过空列
        df = pd.read_excel(
            file_path,
            sheet_name=sheet,
            engine='openpyxl'
        )

        # 删除列名以 "Unnamed:" 开头的列
        df = df.loc[:, ~df.columns.str.startswith('Unnamed:')]

        # 如果提供了 test_group，则筛选对应的数据
        if test_group is not None:
            filtered_df = df[df['test_group'] == test_group].copy()
        else:
            # 如果没有提供 test_group，返回所有数据
            filtered_df = df.copy()

        # 合并数据处理循环
        for col in filtered_df.columns:
            # 检查列中是否包含类似列表的字符串
            if filtered_df[col].dtype == object:  # 只处理对象类型（字符串）
                filtered_df[col] = filtered_df[col].apply(
                    lambda x: _safe_convert_to_list(x) if pd.notna(x) else x
                )
            # 适配 pandas 3.0.0+ 的字符串类型
            elif filtered_df[col].dtype == 'string' or (
                    hasattr(pd, 'StringDtype') and isinstance(filtered_df[col].dtype, pd.StringDtype)):
                filtered_df[col] = filtered_df[col].apply(
                    lambda x: _safe_convert_to_list(x) if pd.notna(x) else x
                )
                # 转换为 object 类型以确保后续处理
                filtered_df[col] = filtered_df[col].astype(object)

            # 将浮点数转换为整数（如果它们是整数值）
            elif filtered_df[col].dtype == float:
                # 检查是否所有非空值都是整数
                non_null_series = filtered_df[col].dropna()
                if len(non_null_series) > 0 and all(x.is_integer() for x in non_null_series if isinstance(x, float)):
                    filtered_df[col] = filtered_df[col].apply(
                        lambda x: int(x) if pd.notna(x) and isinstance(x, float) else x
                    )

        # 如果提供了 projects 参数，则进一步筛选包含该项目的测试用例
        if projects and 'projects' in filtered_df.columns:
            # print(f'当前项目的列表内容为：{filtered_df["projects"]}')

            def safe_include_project(x):
                """
                安全地判断项目是否应该包含，适配不同 pandas 版本
                """
                # 处理 None 和 NaN
                if x is None:
                    return False

                # 对于 pandas 的 NA 值
                try:
                    if pd.isna(x):
                        return False
                except (ValueError, TypeError):
                    # pd.isna() 无法处理某些类型（如非空列表）
                    pass

                # 处理空列表
                if isinstance(x, list) and len(x) == 0:
                    return False

                # 处理字符串类型的项目字段（可能来自 pandas 3.0.0+ 的字符串类型）
                if isinstance(x, str):
                    # 尝试解析为列表
                    if x.startswith('[') and x.endswith(']'):
                        try:
                            x = ast.literal_eval(x)
                        except (ValueError, SyntaxError):
                            # 如果解析失败，保持原值
                            x = [x]
                    else:
                        x = [x]

                # 检查是否为其他可迭代类型
                if not isinstance(x, list):
                    try:
                        # 尝试转换为列表
                        if hasattr(x, '__iter__') and not isinstance(x, str):
                            x = list(x)
                        else:
                            x = [x]
                    except TypeError:
                        # 如果不能转换为列表，返回False
                        return False

                # 确保所有元素都是字符串
                processed_list = []
                for item in x:
                    if isinstance(item, str):
                        processed_list.append(item)
                    else:
                        # 尝试转换为字符串
                        try:
                            processed_list.append(str(item))
                        except:
                            continue

                # 调用原始判断函数
                try:
                    return bool(_should_include_project(processed_list, projects))
                except Exception:
                    # 如果判断过程中出现任何异常，返回 False
                    return False

            filtered_df = filtered_df[filtered_df['projects'].apply(safe_include_project)]

        # 如果提供了 function 参数，则进一步筛选包含该功能的测试用例
        if function is not None and 'function' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['function'].apply(
                lambda x: _should_include_function(x, function)
            )]

        # 如果提供了 case_level 参数，则进一步筛选包含该级别的测试用例
        if case_level is not None and 'case_level' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['case_level'].apply(
                lambda x: _should_include_level(x, case_level)
            )]

        # 将记录添加到总列表中
        all_records.extend(filtered_df.to_dict('records'))

    # 重置索引
    final_df = pd.DataFrame(all_records).reset_index(drop=True)

    test_cases = []
    for i, record in enumerate(final_df.to_dict('records')):
        # 使用 name 字段作为 ID，如果没有则使用索引
        test_id = record.get('name')
        test_cases.append(pytest.param(record, id=test_id))

    return test_cases
# def read_test_cases1(file_path, sheet_name=None, test_group=None, projects=[],function=None, case_level=None):
#     """
#     根据 sheet 名称和 test_group 读取对应的测试用例数据
#     如果不传入 sheet_name，则读取所有 sheet 的数据
#     如果不传入 test_group，则读取所有测试用例
#
#     :param file_path: Excel 文件路径
#     :param sheet_name: 工作表名称（可选），如果不提供则返回所有工作表的数据
#     :param test_group: 测试组名称（可选），如果不提供则返回所有测试用例
#     :param project: 项目名称（可选），如果不提供则返回所有项目的测试用例
#     :return: 包含对应测试用例的列表
#     """
#     all_records = []
#
#     if sheet_name is None:
#         # 获取所有 sheet 名称
#         excel_file = pd.ExcelFile(file_path, engine='openpyxl')
#         sheet_names = excel_file.sheet_names
#     else:
#         # 只处理指定的 sheet
#         sheet_names = [sheet_name]
#
#     # 遍历所有需要处理的 sheet
#     for sheet in sheet_names:
#         # 读取指定 sheet，跳过空列
#         df = pd.read_excel(
#             file_path,
#             sheet_name=sheet,
#             engine='openpyxl'
#         )
#
#         # 删除列名以 "Unnamed:" 开头的列
#         df = df.loc[:, ~df.columns.str.startswith('Unnamed:')]
#
#         # 如果提供了 test_group，则筛选对应的数据
#         if test_group is not None:
#             filtered_df = df[df['test_group'] == test_group].copy()
#         else:
#             # 如果没有提供 test_group，返回所有数据
#             filtered_df = df.copy()
#
#         # 合并数据处理循环
#         for col in filtered_df.columns:
#             # 检查列中是否包含类似列表的字符串
#             if filtered_df[col].dtype == object:  # 只处理对象类型（字符串）
#                 filtered_df[col] = filtered_df[col].apply(
#                     lambda x: _safe_convert_to_list(x) if pd.notna(x) else x
#                 )
#
#                 # 将浮点数转换为整数（如果它们是整数值）
#             elif filtered_df[col].dtype == float:
#                 # 检查是否所有非空值都是整数
#                 non_null_series = filtered_df[col].dropna()
#                 if len(non_null_series) > 0 and all(x.is_integer() for x in non_null_series if isinstance(x, float)):
#                     filtered_df[col] = filtered_df[col].apply(
#                         lambda x: int(x) if pd.notna(x) and isinstance(x, float) else x
#                     )
#
#         # for project in projects:
#             # 如果提供了 project 参数，则进一步筛选包含该项目的测试用例
#         # project = projects[0]
#         # 修改这部分代码
#             # 如果提供了 project 参数，则进一步筛选包含该项目的测试用例
#         if projects and 'projects' in filtered_df.columns:
#             print(f'当前项目的列表内容为：{filtered_df["projects"]}')
#             def safe_include_project(x):
#                 """
#                 安全地判断项目是否应该包含
#                 """
#                 # 处理 None 和 NaN
#                 if x is None:
#                     return False
#
#                 # 对于列表或其他类型，尝试 pd.isna()
#                 try:
#                     if pd.isna(x):
#                         return False
#                 except (ValueError, TypeError):
#                     # pd.isna() 无法处理某些类型（如非空列表）
#                     pass
#
#                 # 处理空列表
#                 if isinstance(x, list) and len(x) == 0:
#                     return False
#
#                 # 处理字符串类型的项目字段（新版本pandas可能会将数组存储为字符串）
#                 if isinstance(x, str):
#                     # 尝试解析为列表
#                     if x.startswith('[') and x.endswith(']'):
#                         try:
#                             x = ast.literal_eval(x)
#                         except (ValueError, SyntaxError):
#                             # 如果解析失败，保持原值
#                             x = [x]
#                     else:
#                         x = [x]
#
#                 # 检查是否为其他可迭代类型
#                 if not isinstance(x, list):
#                     try:
#                         x = list(x)
#                     except TypeError:
#                         # 如果不能转换为列表，返回False
#                         return False
#
#                 # 调用原始判断函数
#                 try:
#                     return bool(_should_include_project(x, projects))
#                 except Exception:
#                     # 如果判断过程中出现任何异常，返回 False
#                     return False
#
#             filtered_df = filtered_df[filtered_df['projects'].apply(safe_include_project)]
#
#
#         # 如果提供了 function 参数，则进一步筛选包含该功能的测试用例
#         if function is not None and 'function' in filtered_df.columns:
#             filtered_df = filtered_df[filtered_df['function'].apply(
#                 lambda x: _should_include_function(x, function)
#             )]
#
#         # 如果提供了 case_level 参数，则进一步筛选包含该级别的测试用例
#         if case_level is not None and 'case_level' in filtered_df.columns:
#             filtered_df = filtered_df[filtered_df['case_level'].apply(
#                 lambda x: _should_include_level(x, case_level)
#             )]
#
#         # 将记录添加到总列表中
#         all_records.extend(filtered_df.to_dict('records'))
#
#     # 重置索引
#     final_df = pd.DataFrame(all_records).reset_index(drop=True)
#
#     test_cases = []
#     for i, record in enumerate(final_df.to_dict('records')):
#         # 使用 name 字段作为 ID，如果没有则使用索引
#         test_id = record.get('name')
#         test_cases.append(pytest.param(record, id=test_id))
#
#     return test_cases

def load_test_config(config_file):
    """加载测试配置文件"""
    current_file = os.path.abspath(__file__)
    project_root = os.path.dirname(os.path.dirname(current_file))
    config_path = os.path.join(project_root, 'test_data_configs', config_file)
    # print(config_path)
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def get_pdp_test_params_dict():
    """获取 PDP 测试参数（字典形式）"""
    config = load_test_config('mqtt_test_configs.yaml')
    pdp_configs = config['mqtt_test_cid_cases']['case_datas']
    return pdp_configs

def get_version_test_params_dict():
    """获取版本测试参数（字典形式）"""
    config = load_test_config('mqtt_test_configs.yaml')
    version_configs = config['version_test_cases']['case_datas']
    return version_configs

def get_yaml_data(yaml_file_name,func_name):
    """获取yaml文件中的测试数据"""
    config = load_test_config(yaml_file_name)
    case_datas = config[func_name]['case_datas']
    return case_datas

def generate_lowercase_str(length=10):
    """生成指定长度的随机小写字母字符串

    Args:
        length (int): 字符串长度，默认为10

    Returns:
        str: 随机小写字母字符串
    """
    return ''.join(random.choices(string.ascii_lowercase, k=length))
def generate_random_string(length=10):
    """生成指定长度的随机字符串（包含字母和数字）

    Args:
        length (int): 字符串长度，默认为10

    Returns:
        str: 随机字符串（包含字母和数字）
    """
    # 定义包含字母和数字的字符集
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))


def generate_escaped_string(length=13):
    escape_sequences = [
        ('\n', 2, '\\n'),  # 换行，长度2
        ('\t', 2, '\\t'),  # 制表符，长度2
        ('\r', 2, '\\r'),  # 回车，长度2
        ('\\', 2, '\\\\'),  # 反斜杠，长度2
        ('\'', 2, '\\\''),  # 单引号，长度2
        # ('\"', 2, '\\\"'),  # 双引号，长度2
        ('\0', 3, '\\0'),  # 空字符，长度3
        ('\b', 2, '\\b'),  # 退格，长度2
        ('\f', 2, '\\f'),  # 换页，长度2
        ('\x41', 4, '\\x41'),  # 十六进制字符 A，长度4
        ('\x31', 4, '\\x31'),  # 十六进制字符 1，长度4
        ('\a', 2, '\\a'),  # 响铃，长度2
        ('\v', 2, '\\v')  # 垂直制表符，长度2
    ]
#\\n\\t\\r\\\\\\'\\0\\b\\f\\x41\\x31
    min_required_length = sum(seq[1] for seq in escape_sequences)

    if length < min_required_length:
        raise ValueError(f"长度必须大于等于{min_required_length}，当前长度={length}")

    result_chars = []  # 存储实际字符
    escape_reprs = []  # 存储对应的转义表示
    current_length = 0  # 当前已使用的长度
    # 1. 确保每个转义字符至少出现一次
    for char, char_length, escape_repr in escape_sequences:
        result_chars.append(char)
        escape_reprs.append(escape_repr)
        current_length += char_length

    # 2. 添加剩余的随机字符
    remaining = length - current_length
    while remaining > 0:
        # 从转义字符列表中随机选择一个
        char, char_length, escape_repr = random.choice(escape_sequences)

        # 只有当剩余长度足够时才添加
        if char_length <= remaining:
            result_chars.append(char)
            escape_reprs.append(escape_repr)
            remaining -= char_length
        else:
            # 如果找不到合适长度的字符，退出循环避免无限循环
            break
    # for _ in range(remaining):
    #     # 从转义字符列表中随机选择一个
    #     char, length, escape_repr = random.choice(escape_sequences)
    #     result_chars.append(char)
    #     escape_reprs.append(escape_repr)

    # 3. 打乱顺序（可选，使分布更随机）
    # combined = list(zip(result_chars, escape_reprs))
    # random.shuffle(combined)
    # result_chars, escape_reprs = zip(*combined)

    # 4. 组合成字符串
    # result_string = ''.join(result_chars)
    revice_escape_reprs = ''.join(escape_reprs)
    # 如果需要精确控制长度，可以截断或补充到指定长度
    if len(revice_escape_reprs) > length:
        revice_escape_reprs = revice_escape_reprs[:length]
    elif len(revice_escape_reprs) < length:
        # 补充字符到指定长度
        additional_chars = ''.join(random.choices(['\\n', '\\t', '\\r'], k=length - len(revice_escape_reprs)))
        revice_escape_reprs += additional_chars
    # send_escape_reprs = revice_escape_reprs.replace('\\', '\\\\')
    data = {'send_escape_reprs': revice_escape_reprs}
    return data

def string_to_hex(input_string):
    """将字符串转换为十六进制表示
    """
    # 将字符串编码为bytes，然后转换为十六进制
    hex_string = input_string.encode('utf-8').hex()
    return hex_string.upper()


def hex_to_string(hex_string):
    """
    将十六进制字符串转换为字符串
    """
    try:
        # 将十六进制字符串转换为字节序列
        bytes_data = bytes.fromhex(hex_string)

        # 尝试 UTF-8 解码
        try:
            return bytes_data.decode('utf-8')
        except UnicodeDecodeError:
            # UTF-8失败则尝试 Latin-1
            try:
                return bytes_data.decode('latin-1')
            except UnicodeDecodeError:
                # 最后回退到原始字节表示
                return str(bytes_data)
    except Exception as e:
        return f"解码错误: {e}"

def generate_hex_string(length):
    """生成指定长度的十六进制字符串
    """
    # 生成length长度的随机十六进制字符串
    hex_chars = '0123456789ABCDEF'
    return ''.join(random.choices(hex_chars, k=length*2))



def generate_mqttsend_data(input_format,msg_len,send_message):
    if type(msg_len) is int and msg_len > 1460:
        if input_format == 0:
            return generate_random_string(msg_len)
        elif input_format == 1:
            return generate_hex_string(msg_len)
        elif input_format == 2:
            return send_message
    else:
        return send_message

def deal_check_send_message(send_message,input_format,output_format):
    # revice_length, revice_publish_data = deal_pubish_urc(log_data)
    if input_format == output_format:
        return send_message
    elif input_format == 0 and output_format == 1:
        return string_to_hex(send_message)
    elif input_format == 1 and output_format == 0:
        return hex_to_string(send_message)
    elif input_format == 2 and output_format == 0:
        send_message = send_message.encode().decode('unicode_escape')
        return send_message
    elif input_format == 2 and output_format == 1:
        return string_to_hex(send_message.encode().decode('unicode_escape'))
def replace_nan_in_dict(data_dict,replace_value= None):
    """处理单层字典"""
    result = {}
    for key, value in data_dict.items():
        if isinstance(value, float) and math.isnan(value):
            result[key] = replace_value
        else:
            result[key] = value
    return result

def replace_dict(data_dict, old_value='""', replace_value=None):
    result = {}
    for key, value in data_dict.items():
        if isinstance(value, float) and math.isnan(value):
            result[key] = replace_value
        elif value == old_value:
            result[key] = ""
        else:
            result[key] = value
    return result
if __name__ == '__main__':
    print("测试函数")

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    excel_path = os.path.join(project_root, "test_data_configs", "mftp_test_configs.xlsx")
    print(excel_path)
    res= read_test_cases(excel_path, sheet_name="AT+MFTP_default", projects=["ML307C","ML307C-GC-CN"],case_level=['P1'])
    print(len(res))

    # 正确访问 pytest.param 包装的数据
    for param_item in res:
        # 如果 param_item 是 pytest.param 对象，需要提取其中的值
        if hasattr(param_item, 'values'):
            test_config = param_item.values[0]
        else:
            test_config = param_item

        print(test_config)

        # send_at = f'AT+MQTTSUB={test_config["willtopic"]},{test_config["topics"][0]}'
        # send_at1 = f'AT+MQTTSUB="{test_config["willtopic"]}","{test_config["topics"][0]}"'
        # print(11111111111)
        # print(send_at)
        # print(send_at1)

    #     for i in set_data:
    #         print(11111111111)
    #         print(i)
    # print(res)
    # print(result)
    # print(11111111111111111111)
    # print(repr(hex_to_str))
    # print(hex_to_str)
    # print(hex_to_str == urc_hex_str)
    # reviced_length, revice_publish_data = deal_pubish_urc(log_data)
    # print(revice_publish_data)
    # print(reviced_length)
    # print(len(res['send_escape_reprs']))
    # deal_res0 = deal_check_send_message(res['send_escape_reprs'], 2, 0)
    # deal_res1 = deal_check_send_message(res['send_escape_reprs'], 2, 1)
    # print(deal_res0)
    # print(deal_res1)
    #assert '746573745c5c6e5c5c5c5c3132335c5c742324' in '746573745c6e5c5c3132335c742324'
    #746573745c6e5c5c3132335c742324
    # res = deal_check_send_message('test\\\\n\\\\\\\\123\\\\t#$', 2, 1)
    # print(res)
