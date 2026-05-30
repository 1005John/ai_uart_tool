import serial
import serial.tools.list_ports
import time
import logging
import re
import struct
import os
from binascii import a2b_hex  # new add
from binascii import b2a_hex
from typing import Optional, List, Callable
from datetime import datetime


class SerialPortManager:
    def __init__(self):
        self.ser = None
        self.is_open = False
        self.content = []
        self.logger = logging.getLogger(__name__)


    def open_serial(self, port, baudrate, timeout=5):
        try:
            self.ser = serial.Serial(port=port,
                baudrate=baudrate,
                timeout=timeout)
            print('Port: %s Baudrate: %s timeout: %s' % (port, baudrate, timeout))
            self.is_open = True
        except serial.SerialException as e:
            print(f"打开串口时发生错误: {e}")
            return False
        except Exception as e:
            print(f"未知错误: {e}")
            return False
    def close_serial(self):
        try:
            if self.is_open and self.ser:
                self.ser.close()
                self.is_open = False
                print("串口关闭成功")
                return True
            else:
                print("串口未打开或已关闭")
                return True
        except Exception as e:
            print(f"关闭串口时发生错误: {e}")
            return False
    def get_default_ip(self, port, baudrate):
        """获取默认的IP地址"""

        serial_manager = SerialPortManager()
        serial_manager.open_serial(port, baudrate)
        try:
            serial_manager.send_at_command('AT+MDNSCFG="ip"')
            ip_default_res = serial_manager.wait_for_keywords_return(keywords='OK')
            if isinstance(ip_default_res, bool):
                ips = ["119.29.29.29","114.114.114.114"]
            else:
                print(ip_default_res)
                pattern = r'"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"'
                ips = re.findall(pattern, ip_default_res)
                print(ips)
                if not ips:
                    ips = ["119.29.29.29", "114.114.114.114"]
            serial_manager.send_at_command('AT+MDNSCFG="ipv6"')
            ip6_default_res = serial_manager.wait_for_keywords_return(keywords='OK')
            if isinstance(ip6_default_res, bool):
                ipv6s = ["2400:3200::1","2001:4860:4860::8888"]
            else:
                print(ip6_default_res)
                pattern = r'"([0-9a-fA-F:]+)"'
                ipv6s = re.findall(pattern, ip6_default_res)
                print(ipv6s)
                if not ipv6s:
                    ipv6s = ["2400:3200::1","2001:4860:4860::8888"]
            return {"ip": ips, "ipv6": ipv6s}
        finally:
            serial_manager.close_serial()

    def get_project(self, port, baudrate):
        """自动设置串口"""
        serial_manager = SerialPortManager()
        serial_manager.open_serial(port, baudrate)
        conn_revice_data = serial_manager.wait_for_response()
        serial_manager.send_at_command("AT+CGMM")
        gmm_revice_data = serial_manager.wait_for_response()
        # 添加调试信息
        print(f"CGMM响应数据: {gmm_revice_data}")

        # 检查是否有有效响应数据
        if not gmm_revice_data:
            print("AT+CGMM命令无响应")
            serial_manager.close_serial()
            raise ValueError('AT+CGMM命令无响应')

        # 按行分割响应内容
        lines = gmm_revice_data.split('\r\n')
        temp_list = []
        for line in lines:
            line = line.strip()
            if not line or 'AT' in line or '\n' in line:
                continue
            temp_list.append(line)
        print(f'处理后的列表: {temp_list}')
        project_line = temp_list[0].strip()
        print(f'当前型号是{project_line}')
        project = project_line[23:]
        print(f'当前匹配到的项目是{project}')
        if project:
            return project
        else:
            print(f"未找到项目名")
            serial_manager.close_serial()
            return None
        # for i in range(len(lines)):
        #     line = lines[i].strip()
        #     # 跳过时间戳部分（假设时间戳以空格或点结束）
        #     if 'AT+GMM' in line:
        #         # 查看下一行是否有型号信息
        #         if i + 1 < len(lines):
        #             next_line = lines[i + 1].strip()
        #             # 提取型号（假设型号在时间戳之后）
        #             # 例如："2026-01-04 15:27:34.565ML307R"
        #             parts = next_line.split()
        #             if len(parts) > 1:
        #                 # 如果有空格分隔，取最后一个部分
        #                 return parts[-1]
        #             else:
        #                 # 如果没有空格，需要去掉时间戳部分
        #                 # 时间戳通常包含日期时间格式，我们找第一个字母的位置
        #                 for j, char in enumerate(next_line):
        #                     if char.isalpha():
        #                         return next_line[j:]

    def calc_crc8(self,data):
        crc = 0
        for b in data:
            crc ^= b
        return crc & 0xFF

    def send_oc_data(self,payload):
        if self.is_open:
            frame = bytearray()

            frame += b'\xAA\x55'
            frame += struct.pack('>H', len(payload))
            frame += payload
            frame += bytes([self.calc_crc8(payload)])
            timestamp_send = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # 毫秒级时间戳
            print(f"[{timestamp_send}] SENT: {frame}")
            self.ser.write(frame)
            # 发送指令并记录时间
            return  True
        else:
            print("串口未打开")
            return False
    def send_at_command(self, command):
        if self.is_open:
            # ser = self.ser
            # command = command.replace(' ', '')
            # 发送指令并记录时间
            timestamp_send = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # 毫秒级时间戳
            print(f"[{timestamp_send}] SENT: {command}")
            self.ser.write((command + '\r\n').encode())
            return  True
        else:
            print("串口未打开")
            return False

    def send_at_command_withresponse(self, command, keyword='>', timeout=5, no_data_threshold=0.5):
        """
        发送AT指令并等待特定关键字响应（改进版，支持大数据传输）
        """
        if not self.is_open:
            print("串口未打开")
            return False

        default_checklist = ["ERROR", "REBOOTING", "+MATREADY"]

        # 发送指令
        timestamp_send = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        print(f"[{timestamp_send}] SENT: {command}")
        self.ser.write((command + '\r\n').encode())

        # 等待响应
        start_time = time.time()
        last_data_time = start_time
        received_any_data = False
        buffer = b''  # 使用字节缓冲区

        while (time.time() - start_time) < timeout:
            if self.ser.in_waiting > 0:
                data = self.ser.read(self.ser.in_waiting)
                buffer += data
                received_any_data = True

                # 尝试解码当前缓冲区数据
                try:
                    decoded_data = buffer.decode('utf-8', errors='ignore')

                    # 按行处理接收的数据
                    lines = decoded_data.split('\r\n')

                    # 检查最后一行是否完整（不以换行符结尾）
                    last_line_complete = decoded_data.endswith('\r\n')

                    for i, line in enumerate(lines):
                        # 如果是最后一行且不完整，暂时不处理
                        if i == len(lines) - 1 and not last_line_complete and line:
                            continue

                        line = line.strip()
                        if not line:
                            continue

                        timestamp_recv = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                        print(f"[{timestamp_recv}] RECV: {line}")

                        # 检查错误关键字
                        for check_item in default_checklist:
                            if check_item in line:
                                print(f"检测到错误关键字: {check_item}")
                                return False

                        # 检查目标关键字
                        if keyword in line:
                            print(f'找到关键字{keyword}返回')
                            return True

                    # 如果最后一行完整，清空缓冲区
                    if last_line_complete:
                        buffer = b''
                    else:
                        # 保留不完整的最后一行数据
                        last_line = lines[-1] if lines else ''
                        buffer = last_line.encode('utf-8') if last_line else b''

                except UnicodeDecodeError:
                    # 解码失败，可能是二进制数据，继续累积
                    pass

                last_data_time = time.time()

            # 检查是否长时间没有收到数据
            elif received_any_data and (time.time() - last_data_time) > no_data_threshold:
                # 处理缓冲区中剩余的数据
                if buffer:
                    try:
                        decoded_data = buffer.decode('utf-8', errors='ignore')
                        if keyword in decoded_data:
                            print(f'在缓冲区中找到关键字{keyword}返回')
                            return True
                    except:
                        pass
                print(f"数据接收完毕，最后接收时间: {last_data_time}")
                return False

            time.sleep(0.01)

        print(f"等待关键字 '{keyword}' 超时")
        return False

    def send_at_command_withkeywords(self, command, keywords=['>'], timeout=5, no_data_threshold=0.5):
        """
        发送AT指令并等待所有指定关键字响应

        Args:
            command (str): 要发送的AT指令
            keywords (list): 需要等待的所有关键字列表，默认为['>']
            timeout (int): 总超时时间(秒)
            no_data_threshold (float): 无数据接收超时时间(秒)

        Returns:
            bool: 找到所有keywords返回True，否则返回False
        """
        if not self.is_open:
            print("串口未打开")
            return False

        default_checklist = ["ERROR", "REBOOTING", "+MATREADY"]

        # 发送指令
        timestamp_send = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        print(f"[{timestamp_send}] SENT: {command}")
        self.ser.write((command + '\r\n').encode())

        # 等待响应
        start_time = time.time()
        last_data_time = start_time
        received_any_data = False
        buffer = b''
        found_keywords = set()  # 记录已找到的关键字
        target_keywords = set(keywords)  # 目标关键字集合

        while (time.time() - start_time) < timeout:
            if self.ser.in_waiting > 0:
                data = self.ser.read(self.ser.in_waiting)
                buffer += data
                received_any_data = True

                # 尝试解码当前缓冲区数据
                try:
                    decoded_data = buffer.decode('utf-8', errors='ignore')

                    # 按行处理接收的数据
                    lines = decoded_data.split('\r\n')

                    # 检查最后一行是否完整
                    last_line_complete = decoded_data.endswith('\r\n')

                    for i, line in enumerate(lines):
                        # 如果是最后一行且不完整，暂时不处理
                        if i == len(lines) - 1 and not last_line_complete and line:
                            continue

                        line = line.strip()
                        if not line:
                            continue

                        timestamp_recv = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                        print(f"[{timestamp_recv}] RECV: {line}")

                        # 检查错误关键字
                        for check_item in default_checklist:
                            if check_item in line:
                                print(f"检测到错误关键字: {check_item}")
                                return False

                        # 检查目标关键字
                        for keyword in keywords:
                            if keyword in line and keyword not in found_keywords:
                                found_keywords.add(keyword)
                                print(f"找到关键字: {keyword} (已找到 {len(found_keywords)}/{len(target_keywords)})")

                        # 检查是否所有关键字都已找到
                        if found_keywords == target_keywords:
                            print(f"所有关键字已找到: {found_keywords}")
                            return True

                    # 如果最后一行完整，清空缓冲区
                    if last_line_complete:
                        buffer = b''
                    else:
                        # 保留不完整的最后一行数据
                        last_line = lines[-1] if lines else ''
                        buffer = last_line.encode('utf-8') if last_line else b''

                except UnicodeDecodeError:
                    pass

                last_data_time = time.time()

            # 检查是否长时间没有收到数据
            elif received_any_data and (time.time() - last_data_time) > no_data_threshold:
                # 处理缓冲区中剩余的数据
                if buffer:
                    try:
                        decoded_data = buffer.decode('utf-8', errors='ignore')
                        for keyword in keywords:
                            if keyword in decoded_data and keyword not in found_keywords:
                                found_keywords.add(keyword)
                        # 检查是否所有关键字都已找到
                        if found_keywords == target_keywords:
                            print(f"所有关键字已找到: {found_keywords}")
                            return True
                    except:
                        pass
                print(f"数据接收完毕，最后接收时间: {last_data_time}")
                print(f"未找到所有关键字，已找到: {found_keywords}，期望: {target_keywords}")
                return False

            time.sleep(0.01)

        print(f"等待关键字 {keywords} 超时，已找到: {found_keywords}")
        return False
    def send_at_command_as_string(self, command):
        if self.is_open:
            # ser = self.ser
            # command = command.replace(' ', '')
            # 发送指令并记录时间
            timestamp_send = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # 毫秒级时间戳
            print(f"[{timestamp_send}] SENT: {command}")
            self.ser.write((command).encode())

        else:
            print("串口未打开")
            return ""
    def send_at_command_in_hex(self, command):  # new add
        if self.ser.is_open:
            print(command)
            s = str(a2b_hex(command), encoding='utf8')
            # 发送指令并记录时间
            timestamp_send = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            print(f"[{timestamp_send}] SENT HEX: {command}")
            self.ser.write((s).encode('utf-8'))
    def send_at_command_with_ctrl_z(self, command, timeout=1):
        """
        发送AT指令并在末尾添加Ctrl+Z字符

        Args:
            command (str): 要发送的AT指令
            timeout (int): 超时时间(秒)

        Returns:
            None
        """
        if self.is_open:
            try:
                command = command.replace(' ', '')
                # 发送指令并记录时间
                timestamp_send = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # 毫秒级时间戳
                print(f"[{timestamp_send}] SENT WITH CTRL+Z: {command}")
                # 发送命令加Ctrl+Z (ASCII码26)
                self.ser.write((command + '\x1A\r\n').encode())
            except Exception as e:
                print(f"发送带Ctrl+Z指令时发生错误: {e}")
        else:
            print("串口未打开")
    def send_at_command_with_hex(self, hex_command, timeout=1):
        """
        发送十六进制格式的AT指令

        Args:
            hex_command (str): 十六进制字符串格式的命令，例如 "41542B43474D493F0D0A"
            timeout (int): 超时时间(秒)
        Returns:
            None
        """
        if self.is_open:
            try:
                # 将十六进制字符串转换为字节数据
                byte_data = bytes.fromhex(hex_command)

                # 发送指令并记录时间
                timestamp_send = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                print(f"[{timestamp_send}] SENT HEX: {hex_command}")
                self.ser.write(byte_data)

            except ValueError as e:
                print(f"十六进制数据格式错误: {e}")
            except Exception as e:
                print(f"发送十六进制指令时发生错误: {e}")
        else:
            print("串口未打开")

    def send_at_command_with_hex_and_ctrl_z(self, hex_command, timeout=1):
        """
        发送十六进制格式的AT指令并在末尾添加Ctrl+Z字符

        Args:
            hex_command (str): 十六进制字符串格式的命令，例如 "41542B43474D493F"
            timeout (int): 超时时间(秒)

        Returns:
            None
        """
        if self.is_open:
            try:
                # 将十六进制字符串转换为字节数据
                byte_data = bytes.fromhex(hex_command)
                # 添加Ctrl+Z字符(0x1A)
                byte_data_with_ctrl_z = byte_data + b'\x1A'

                # 发送指令并记录时间
                timestamp_send = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                print(f"[{timestamp_send}] SENT HEX WITH CTRL+Z: {hex_command}")
                self.ser.write(byte_data_with_ctrl_z)

            except ValueError as e:
                print(f"十六进制数据格式错误: {e}")
            except Exception as e:
                print(f"发送十六进制指令带Ctrl+Z时发生错误: {e}")
        else:
            print("串口未打开")

    def write_from_file(self, file_path, append_crlf=True, chunk_size=512):
        """
        从文件读取内容并写入串口（支持分块写入）

        Args:
            file_path (str): 文件路径
            append_crlf (bool): 是否在每行后添加换行符，默认为True
            chunk_size (int): 每次写入的数据块大小，默认512字节

        Returns:
            bool: 写入成功返回True，失败返回False
        """
        if not self.is_open:
            print("串口未打开")
            return False

        try:
            # 读取文件内容
            with open(file_path, 'rb') as file:  # 使用二进制模式读取
                content = file.read()

            # 记录发送时间
            timestamp_send = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

            # 如果需要添加换行符
            if append_crlf:
                content = content + b'\r\n'

            # 分块写入
            total_bytes = len(content)
            bytes_sent = 0

            print(f"[{timestamp_send}] 开始发送文件: {file_path}, 总大小: {total_bytes} 字节")

            while bytes_sent < total_bytes:
                # 计算当前块的大小
                current_chunk_size = min(chunk_size, total_bytes - bytes_sent)
                chunk = content[bytes_sent:bytes_sent + current_chunk_size]

                # 写入当前块
                self.ser.write(chunk)

                # 等待数据发送完成（可选，根据实际需要调整）
                self.ser.flush()

                # 更新已发送字节数
                bytes_sent += current_chunk_size

                # 打印进度
                print(f"[{timestamp_send}] 已发送: {bytes_sent}/{total_bytes} 字节")

                # 可选：添加短暂延迟，避免发送过快
                # time.sleep(0.01)

            print(f"[{timestamp_send}] 文件发送完成: {file_path}")
            return True

        except FileNotFoundError:
            print(f"文件不存在: {file_path}")
            return False
        except Exception as e:
            print(f"从文件写入串口时发生错误: {e}")
            return False

    def write_tcps_certificate(self, n1, n2, n3):
        ''' tcpr.cer/tcpc.cer/tcpc.key为三个证书名字 调用时如果'''
        if self.ser.is_open:
            self.ser.write((fr'AT+MFDELETE="/"' + '\r\n').encode('utf-8'))
            print(self.ser.readlines())
            self.ser.write((fr'AT+MSSLCERTWR="{n1}",0,3813' + '\r\n').encode('utf-8'))
            print(self.ser.readlines())
            self.ser.write(('-----BEGIN CERTIFICATE-----\nMIIF+zCCBOOgAwIBAgIQBK/+rodDhI/jQds0Y19YHzANBgkqhkiG9w0BAQsFADBu\nMQswCQYDVQQGEwJVUzEVMBMGA1UEChMMRGlnaUNlcnQgSW5jMRkwFwYDVQQLExB3\nd3cuZGlnaWNlcnQuY29tMS0wKwYDVQQDEyRFbmNyeXB0aW9uIEV2ZXJ5d2hlcmUg\nRFYgVExTIENBIC0gRzIwHhcNMjUxMTEyMDAwMDAwWhcNMjYxMTExMjM1OTU5WjAV\nMRMwEQYDVQQDEwp6emZmZGQudG9wMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIB\nCgKCAQEArvYEac6Y+nG3JGIDAG9Y1r+PmhcKgjz5AWKbWXBCMnSdbaCKA+FXAL2v\nryKDvzUWXyKm23a05U/0uYkgUhLLHSAL+knsWWlkNXgXZYgBaTSCVTGAfxbMxo5r\nGnyvcx8zveMq0LNldew5jy4nc90rY9Hnl35f2NP/bhmQp602uthNEd5DZU+dlpPN\neJ3Ja6AwSxSNk4aJ1C1GhlYYLzNS5MzNJHwY8Ok5aEV0jjsN6m5l/TtDGAmxoJps\n/fVD0i8YmmQOlUihd5MwV1ugh7iLXdbwUOEEYepGSyWTBsEvL6aIolZyuAuJYWes\njajtTQP4AFz+IPgi70nc3g5dqjJhzQIDAQABo4IC7DCCAugwHwYDVR0jBBgwFoAU\neN+RkF/u3qz2xXXr1UxVU+8kSrYwHQYDVR0OBBYEFImHhLSHsWNXYJXBWI2rm0sA\nCpTuMCUGA1UdEQQeMByCCnp6ZmZkZC50b3CCDnd3dy56emZmZGQudG9wMD4GA1Ud\nIAQ3MDUwMwYGZ4EMAQIBMCkwJwYIKwYBBQUHAgEWG2h0dHA6Ly93d3cuZGlnaWNl\ncnQuY29tL0NQUzAOBgNVHQ8BAf8EBAMCBaAwHQYDVR0lBBYwFAYIKwYBBQUHAwEG\nCCsGAQUFBwMCMIGABggrBgEFBQcBAQR0MHIwJAYIKwYBBQUHMAGGGGh0dHA6Ly9v\nY3NwLmRpZ2ljZXJ0LmNvbTBKBggrBgEFBQcwAoY+aHR0cDovL2NhY2VydHMuZGln\naWNlcnQuY29tL0VuY3J5cHRpb25FdmVyeXdoZXJlRFZUTFNDQS1HMi5jcnQwDAYD\nVR0TAQH/BAIwADCCAX0GCisGAQQB1nkCBAIEggFtBIIBaQFnAHUA2AlVO5RPev/I\nFhlvlE+Fq7D4/F6HVSYPFdEucrtFSxQAAAGadtmiYwAABAMARjBEAiBwKpmh4q1D\ndP8lBxIXFsp/GKdrNOTE4uas6tRlIdVtwAIgb6a+7852EVGSna+KWQc79KpMoriu\nWlxJC4KddD2dgDoAdgDCMX5XRRmjRe5/ON6ykEHrx8IhWiK/f9W1rXaa2Q5SzQAA\nAZp22aJfAAAEAwBHMEUCIBAX6R4mpPtkZWrGLlljJiudg879lq1jXL+M8/KD7hXJ\nAiEA3b4grpsQGodKMX4j6IaacI6uxtZilpC8UBFSL0i2rlkAdgCUTkOH+uzB74Hz\nGSQmqBhlAcfTXzgCAT9yZ31VNy4Z2AAAAZp22aJ1AAAEAwBHMEUCIQDT8pqewfmV\nSl9NKgnqSuJ20sy6SRW9evtNBhGUpMBVaQIgFFzEcnyARs8OJ3ivvgmB8N/2MV0+\nbexnPtnx9JhH8H8wDQYJKoZIhvcNAQELBQADggEBAJa/c15hffDA4FdJkyAX2ciH\nWb1DuXgJbX8XaD26Oy9WFwAmwgsBAdIrUgCZpiQZKQqRmrA0pN1msVlnwUa3B9qF\nFOmZe6Z2Cvwtm9GeXXvGUnFGZRknryuAzqROOM22cKlDX33OqDNgrOgfPTz2RCol\nribMFXoVRCF+9FUk0aVmcALgRQbBMbneSvSw6EcQBoQWpC4tcdHYxwZ4fNQ7Qh+l\n1VY/vzujQq1r5Tw92jQIYstfdLgKG4lh9ZXq1g9j2ja5WW8uj7JkJIwqrIGt+Ci3\nzAuw18dhaNXK6rOE2PhzaqRYP2l8fZ9NJPJPUKYqtEzkyV6Ti3PzibhkqOT5Cl4=\n-----END CERTIFICATE-----\n-----BEGIN CERTIFICATE-----\nMIIEqjCCA5KgAwIBAgIQDeD/te5iy2EQn2CMnO1e0zANBgkqhkiG9w0BAQsFADBh\nMQswCQYDVQQGEwJVUzEVMBMGA1UEChMMRGlnaUNlcnQgSW5jMRkwFwYDVQQLExB3\nd3cuZGlnaWNlcnQuY29tMSAwHgYDVQQDExdEaWdpQ2VydCBHbG9iYWwgUm9vdCBH\nMjAeFw0xNzExMjcxMjQ2NDBaFw0yNzExMjcxMjQ2NDBaMG4xCzAJBgNVBAYTAlVT\nMRUwEwYDVQQKEwxEaWdpQ2VydCBJbmMxGTAXBgNVBAsTEHd3dy5kaWdpY2VydC5j\nb20xLTArBgNVBAMTJEVuY3J5cHRpb24gRXZlcnl3aGVyZSBEViBUTFMgQ0EgLSBH\nMjCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAO8Uf46i/nr7pkgTDqnE\neSIfCFqvPnUq3aF1tMJ5hh9MnO6Lmt5UdHfBGwC9Si+XjK12cjZgxObsL6Rg1njv\nNhAMJ4JunN0JGGRJGSevbJsA3sc68nbPQzuKp5Jc8vpryp2mts38pSCXorPR+sch\nQisKA7OSQ1MjcFN0d7tbrceWFNbzgL2csJVQeogOBGSe/KZEIZw6gXLKeFe7mupn\nNYJROi2iC11+HuF79iAttMc32Cv6UOxixY/3ZV+LzpLnklFq98XORgwkIJL1HuvP\nha8yvb+W6JislZJL+HLFtidoxmI7Qm3ZyIV66W533DsGFimFJkz3y0GeHWuSVMbI\nlfsCAwEAAaOCAU8wggFLMB0GA1UdDgQWBBR435GQX+7erPbFdevVTFVT7yRKtjAf\nBgNVHSMEGDAWgBROIlQgGJXm427mD/r6uRLtBhePOTAOBgNVHQ8BAf8EBAMCAYYw\nHQYDVR0lBBYwFAYIKwYBBQUHAwEGCCsGAQUFBwMCMBIGA1UdEwEB/wQIMAYBAf8C\nAQAwNAYIKwYBBQUHAQEEKDAmMCQGCCsGAQUFBzABhhhodHRwOi8vb2NzcC5kaWdp\nY2VydC5jb20wQgYDVR0fBDswOTA3oDWgM4YxaHR0cDovL2NybDMuZGlnaWNlcnQu\nY29tL0RpZ2lDZXJ0R2xvYmFsUm9vdEcyLmNybDBMBgNVHSAERTBDMDcGCWCGSAGG\n/WwBAjAqMCgGCCsGAQUFBwIBFhxodHRwczovL3d3dy5kaWdpY2VydC5jb20vQ1BT\nMAgGBmeBDAECATANBgkqhkiG9w0BAQsFAAOCAQEAoBs1eCLKakLtVRPFRjBIJ9LJ\nL0s8ZWum8U8/1TMVkQMBn+CPb5xnCD0GSA6L/V0ZFrMNqBirrr5B241OesECvxIi\n98bZ90h9+q/X5eMyOD35f8YTaEMpdnQCnawIwiHx06/0BfiTj+b/XQih+mqt3ZXe\nxNCJqKexdiB2IWGSKcgahPacWkk/BAQFisKIFYEqHzV974S3FAz/8LIfD58xnsEN\nGfzyIDkH3JrwYZ8caPTf6ZX9M1GrISN8HnWTtdNCH2xEajRa/h9ZBXjUyFKQrGk2\nn2hcLrfZSbynEC/pSw/ET7H5nWwckjmAJ1l9fcnbqkU/pf6uMQmnfl0JQjJNSg==\n-----END CERTIFICATE-----' + '\r\n').encode(
                'utf-8'))
            print(self.ser.readlines())

            self.ser.write((fr'AT+MSSLCERTWR="{n2}",0,3813' + '\r\n').encode('utf-8'))
            print(self.ser.readlines())
            self.ser.write(('-----BEGIN CERTIFICATE-----\nMIIF+zCCBOOgAwIBAgIQBK/+rodDhI/jQds0Y19YHzANBgkqhkiG9w0BAQsFADBu\nMQswCQYDVQQGEwJVUzEVMBMGA1UEChMMRGlnaUNlcnQgSW5jMRkwFwYDVQQLExB3\nd3cuZGlnaWNlcnQuY29tMS0wKwYDVQQDEyRFbmNyeXB0aW9uIEV2ZXJ5d2hlcmUg\nRFYgVExTIENBIC0gRzIwHhcNMjUxMTEyMDAwMDAwWhcNMjYxMTExMjM1OTU5WjAV\nMRMwEQYDVQQDEwp6emZmZGQudG9wMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIB\nCgKCAQEArvYEac6Y+nG3JGIDAG9Y1r+PmhcKgjz5AWKbWXBCMnSdbaCKA+FXAL2v\nryKDvzUWXyKm23a05U/0uYkgUhLLHSAL+knsWWlkNXgXZYgBaTSCVTGAfxbMxo5r\nGnyvcx8zveMq0LNldew5jy4nc90rY9Hnl35f2NP/bhmQp602uthNEd5DZU+dlpPN\neJ3Ja6AwSxSNk4aJ1C1GhlYYLzNS5MzNJHwY8Ok5aEV0jjsN6m5l/TtDGAmxoJps\n/fVD0i8YmmQOlUihd5MwV1ugh7iLXdbwUOEEYepGSyWTBsEvL6aIolZyuAuJYWes\njajtTQP4AFz+IPgi70nc3g5dqjJhzQIDAQABo4IC7DCCAugwHwYDVR0jBBgwFoAU\neN+RkF/u3qz2xXXr1UxVU+8kSrYwHQYDVR0OBBYEFImHhLSHsWNXYJXBWI2rm0sA\nCpTuMCUGA1UdEQQeMByCCnp6ZmZkZC50b3CCDnd3dy56emZmZGQudG9wMD4GA1Ud\nIAQ3MDUwMwYGZ4EMAQIBMCkwJwYIKwYBBQUHAgEWG2h0dHA6Ly93d3cuZGlnaWNl\ncnQuY29tL0NQUzAOBgNVHQ8BAf8EBAMCBaAwHQYDVR0lBBYwFAYIKwYBBQUHAwEG\nCCsGAQUFBwMCMIGABggrBgEFBQcBAQR0MHIwJAYIKwYBBQUHMAGGGGh0dHA6Ly9v\nY3NwLmRpZ2ljZXJ0LmNvbTBKBggrBgEFBQcwAoY+aHR0cDovL2NhY2VydHMuZGln\naWNlcnQuY29tL0VuY3J5cHRpb25FdmVyeXdoZXJlRFZUTFNDQS1HMi5jcnQwDAYD\nVR0TAQH/BAIwADCCAX0GCisGAQQB1nkCBAIEggFtBIIBaQFnAHUA2AlVO5RPev/I\nFhlvlE+Fq7D4/F6HVSYPFdEucrtFSxQAAAGadtmiYwAABAMARjBEAiBwKpmh4q1D\ndP8lBxIXFsp/GKdrNOTE4uas6tRlIdVtwAIgb6a+7852EVGSna+KWQc79KpMoriu\nWlxJC4KddD2dgDoAdgDCMX5XRRmjRe5/ON6ykEHrx8IhWiK/f9W1rXaa2Q5SzQAA\nAZp22aJfAAAEAwBHMEUCIBAX6R4mpPtkZWrGLlljJiudg879lq1jXL+M8/KD7hXJ\nAiEA3b4grpsQGodKMX4j6IaacI6uxtZilpC8UBFSL0i2rlkAdgCUTkOH+uzB74Hz\nGSQmqBhlAcfTXzgCAT9yZ31VNy4Z2AAAAZp22aJ1AAAEAwBHMEUCIQDT8pqewfmV\nSl9NKgnqSuJ20sy6SRW9evtNBhGUpMBVaQIgFFzEcnyARs8OJ3ivvgmB8N/2MV0+\nbexnPtnx9JhH8H8wDQYJKoZIhvcNAQELBQADggEBAJa/c15hffDA4FdJkyAX2ciH\nWb1DuXgJbX8XaD26Oy9WFwAmwgsBAdIrUgCZpiQZKQqRmrA0pN1msVlnwUa3B9qF\nFOmZe6Z2Cvwtm9GeXXvGUnFGZRknryuAzqROOM22cKlDX33OqDNgrOgfPTz2RCol\nribMFXoVRCF+9FUk0aVmcALgRQbBMbneSvSw6EcQBoQWpC4tcdHYxwZ4fNQ7Qh+l\n1VY/vzujQq1r5Tw92jQIYstfdLgKG4lh9ZXq1g9j2ja5WW8uj7JkJIwqrIGt+Ci3\nzAuw18dhaNXK6rOE2PhzaqRYP2l8fZ9NJPJPUKYqtEzkyV6Ti3PzibhkqOT5Cl4=\n-----END CERTIFICATE-----\n-----BEGIN CERTIFICATE-----\nMIIEqjCCA5KgAwIBAgIQDeD/te5iy2EQn2CMnO1e0zANBgkqhkiG9w0BAQsFADBh\nMQswCQYDVQQGEwJVUzEVMBMGA1UEChMMRGlnaUNlcnQgSW5jMRkwFwYDVQQLExB3\nd3cuZGlnaWNlcnQuY29tMSAwHgYDVQQDExdEaWdpQ2VydCBHbG9iYWwgUm9vdCBH\nMjAeFw0xNzExMjcxMjQ2NDBaFw0yNzExMjcxMjQ2NDBaMG4xCzAJBgNVBAYTAlVT\nMRUwEwYDVQQKEwxEaWdpQ2VydCBJbmMxGTAXBgNVBAsTEHd3dy5kaWdpY2VydC5j\nb20xLTArBgNVBAMTJEVuY3J5cHRpb24gRXZlcnl3aGVyZSBEViBUTFMgQ0EgLSBH\nMjCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAO8Uf46i/nr7pkgTDqnE\neSIfCFqvPnUq3aF1tMJ5hh9MnO6Lmt5UdHfBGwC9Si+XjK12cjZgxObsL6Rg1njv\nNhAMJ4JunN0JGGRJGSevbJsA3sc68nbPQzuKp5Jc8vpryp2mts38pSCXorPR+sch\nQisKA7OSQ1MjcFN0d7tbrceWFNbzgL2csJVQeogOBGSe/KZEIZw6gXLKeFe7mupn\nNYJROi2iC11+HuF79iAttMc32Cv6UOxixY/3ZV+LzpLnklFq98XORgwkIJL1HuvP\nha8yvb+W6JislZJL+HLFtidoxmI7Qm3ZyIV66W533DsGFimFJkz3y0GeHWuSVMbI\nlfsCAwEAAaOCAU8wggFLMB0GA1UdDgQWBBR435GQX+7erPbFdevVTFVT7yRKtjAf\nBgNVHSMEGDAWgBROIlQgGJXm427mD/r6uRLtBhePOTAOBgNVHQ8BAf8EBAMCAYYw\nHQYDVR0lBBYwFAYIKwYBBQUHAwEGCCsGAQUFBwMCMBIGA1UdEwEB/wQIMAYBAf8C\nAQAwNAYIKwYBBQUHAQEEKDAmMCQGCCsGAQUFBzABhhhodHRwOi8vb2NzcC5kaWdp\nY2VydC5jb20wQgYDVR0fBDswOTA3oDWgM4YxaHR0cDovL2NybDMuZGlnaWNlcnQu\nY29tL0RpZ2lDZXJ0R2xvYmFsUm9vdEcyLmNybDBMBgNVHSAERTBDMDcGCWCGSAGG\n/WwBAjAqMCgGCCsGAQUFBwIBFhxodHRwczovL3d3dy5kaWdpY2VydC5jb20vQ1BT\nMAgGBmeBDAECATANBgkqhkiG9w0BAQsFAAOCAQEAoBs1eCLKakLtVRPFRjBIJ9LJ\nL0s8ZWum8U8/1TMVkQMBn+CPb5xnCD0GSA6L/V0ZFrMNqBirrr5B241OesECvxIi\n98bZ90h9+q/X5eMyOD35f8YTaEMpdnQCnawIwiHx06/0BfiTj+b/XQih+mqt3ZXe\nxNCJqKexdiB2IWGSKcgahPacWkk/BAQFisKIFYEqHzV974S3FAz/8LIfD58xnsEN\nGfzyIDkH3JrwYZ8caPTf6ZX9M1GrISN8HnWTtdNCH2xEajRa/h9ZBXjUyFKQrGk2\nn2hcLrfZSbynEC/pSw/ET7H5nWwckjmAJ1l9fcnbqkU/pf6uMQmnfl0JQjJNSg==\n-----END CERTIFICATE-----' + '\r\n').encode(
                'utf-8'))
            print(self.ser.readlines())

            self.ser.write((fr'AT+MSSLKEYWR="{n3}",0,1675' + '\r\n').encode('utf-8'))
            print(self.ser.readlines())
            self.ser.write(('-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEArvYEac6Y+nG3JGIDAG9Y1r+PmhcKgjz5AWKbWXBCMnSdbaCK\nA+FXAL2vryKDvzUWXyKm23a05U/0uYkgUhLLHSAL+knsWWlkNXgXZYgBaTSCVTGA\nfxbMxo5rGnyvcx8zveMq0LNldew5jy4nc90rY9Hnl35f2NP/bhmQp602uthNEd5D\nZU+dlpPNeJ3Ja6AwSxSNk4aJ1C1GhlYYLzNS5MzNJHwY8Ok5aEV0jjsN6m5l/TtD\nGAmxoJps/fVD0i8YmmQOlUihd5MwV1ugh7iLXdbwUOEEYepGSyWTBsEvL6aIolZy\nuAuJYWesjajtTQP4AFz+IPgi70nc3g5dqjJhzQIDAQABAoIBABK1033/LoPl4kh9\nRMXoom8AuFopqaGI5LYdtfBIHYQozWcaWngUwomdP2ryvXUWt8g/u+lPVgQJ22l1\n/SNZyCfas/01p5VePG2tZI8ijsgR6fgzXYL5zLdVJqYD/H1Ksm1VnFAKR0jnlLY3\noNd2qPu5SFN+m8Bj13aOPFZ6Ixay+lPj4fA6y/FbKCUfLkmEJkie/nf+wMV0dq3y\ncoSYM/kLr/eDS7u8Ls8V+dgZKNw1z+NqhJj7OjOdBTf5mP95kHCtXrFu41bvLAHH\nWNkOJ0cFc4CDfiXAgGNRyxRUyYGBUA0siXr+RtjtkHFi4P08sBSCH09oyaYH/E0J\nYgd48D8CgYEA8Iy5kNGvGL+gnYeaAMuMqChMLYdLw2H5nzqasPWWo7TPMAZOvHo8\nPPtI6+inzrpZ1khlhIUmPGxBbHgUSvZoq5ycqO8XP6PWwwEdjV1voXjAcwB6k8L1\nyqH2k9bvv1Ah9xbjwce+SH3Z0IP6DI7nlhJEvq3ddRAa/kfftgFlHZsCgYEAujLX\nFXOMNBv21wY+TasADUkSOsphpgVOVOTd/uJJN64YNHqQFbpPBL58eO/7DuwK12/u\nFtdrcQJ658H9pZemW6suCvpZKx2z9Hh5QypSQJ89XymJGSXcwOw475XOe/ieWsXa\nAJpmIlzv1HEnDnhkebO3kTuK/3GBce+hXaR+KLcCgYEApRXfEG1nPpPctd/nKB6J\nxKoLRb+xlkB6IPYGTeXt4SHogywBA0bcanmGHSkJaU3o86+xxBXhHNyqtbdfLecY\nBJaxyRp1GR7m9+OfFXKHdwi5AvPUK+5D4zHuWJ3M4b4r4TibTFU52OROBNVeWRoG\nA6878KS/9GP+Mn6/IFiqvXsCgYB0pGqmzoazEh2U4B1hjFDxAaiA2c1IMqS6e9Ex\n3dHeJpqVLX5bjiX4I9hX7oYI+AdmpICzIGn3FoWl75mVBaY6YMbsK552axoTePEG\nCVoTj23j0mJHNbfPx2t3cxIyCTIyTSVfIVoABtZa8DN2VicjMlk5iuJtWU6s8F/X\nCLfbiwKBgH78qDoL1o3k3s6CvZk/fv+znf5518Z+63KwzYFB9ffil/7EdH8kSGr/\nCqMjHYXym3h1wKOUGdGRyGA8/IHr2+oL3Qquz0vs6tU9oaZuv/ljZYJNCOBv/UR/\n6XOch7U1SNTVAQuAIl1q4QMpt6YZGQDROPDskBwQYc6Yw4DTBpJW\n-----END RSA PRIVATE KEY-----' + '\r\n').encode(
                'utf-8'))
            print(self.ser.readlines())

    def write_mqtts_certificate(self, n1, n2, n3):
        ''' "mqttr.cer", "mqttc.cer", "mqttc.key"为三个证书名字 调用时如果某个证书不写，则用 None '''
        if self.ser.is_open:
            self.ser.write((fr'AT+MFDELETE="/"' + '\r\n').encode('utf-8'))
            print(self.ser.readlines())
            self.ser.write((fr'AT+MSSLCERTWR="{n1}",0,1273' + '\r\n').encode('utf-8'))
            print(self.ser.readlines())
            self.ser.write((
                    '-----BEGIN CERTIFICATE-----\nMIIDfzCCAmegAwIBAgIUNkQRleM9QOcfEKgg/QHS6kRPqkQwDQYJKoZIhvcNAQEL\nBQAwTzELMAkGA1UEBhMCQ04xEDAOBgNVBAgMB0ppYW5nc3UxDzANBgNVBAcMBlN1\nemhvdTEMMAoGA1UECgwDWFhYMQ8wDQYDVQQDDAZTZWxmQ0EwHhcNMjQwMzI3MDA1\nMDE0WhcNMzQwMzI1MDA1MDE0WjBPMQswCQYDVQQGEwJDTjEQMA4GA1UECAwHSmlh\nbmdzdTEPMA0GA1UEBwwGU3V6aG91MQwwCgYDVQQKDANYWFgxDzANBgNVBAMMBlNl\nbGZDQTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBALLTCcIu6XyUMQhG\nxUqVMhhFQeULqcUV67WEMtqGWCVB/j8Y1Go/VEe2jxb/l3LsLlEceBjfn8vgLwy5\nFhEzdTztqPMAL124/vX45JYvgxQxU4LdHdEde9keiVE0MvddvX0u6Tw7IusvguAK\nEBqhw3cpNHnUQKT3n906B/m70wlRt+RAgBsvmM1Gi3TyKzwN0xnaUV+SHKiT/VRg\n67pngSb1wpl97tzFsZRUpVddpasGkGv4FZTxn6cVk5vNi5fUmb5xvJsS3akKULGW\n6iifqyRo54xBTVTU/56PqYsTNhGKofSLrxvIu3y5wS0ocNpOWV1T75TmAYtaZygA\n2TaaiQUCAwEAAaNTMFEwHQYDVR0OBBYEFFvUBgEisCoRGl7kJ89UpBTOb9CMMB8G\nA1UdIwQYMBaAFFvUBgEisCoRGl7kJ89UpBTOb9CMMA8GA1UdEwEB/wQFMAMBAf8w\nDQYJKoZIhvcNAQELBQADggEBAJnnjOZJxS+bSrQaXn0BTQKoSwseSzQuOsOIX1VA\nYsbhB8ZvspXBo+/hG1XQZhNgBkpK+ebU4XKT4KUPmTsEcFHSk6drsQnw80Zecefz\nsBLR8yedvd5SDyu9C0tyWFMcTPFplU677JEjBHlJU9rxXfkvJgrBF2u6mhfchIWH\ngE3B+Fevk4R1cviclxQ1yYPBBE1op2/vCTlPqM9YbgnmaCVoX9w+ZCqeLdVLpaf1\nd71uTToyEPZ82EvrLvkibIEtKvDzStfyg3loIC/2SmN8H8MN1aAhnuD97Voxxq/x\nQdriB9OSuyoHC55VeOKCzk15Na4D1ULHlUX/FWmwgQGmRK0=\n-----END CERTIFICATE-----' + '\r\n').encode(
                'utf-8'))
            print(self.ser.readlines())

            self.ser.write((fr'AT+MSSLCERTWR="{n2}",0,1151' + '\r\n').encode('utf-8'))
            print(self.ser.readlines())
            self.ser.write((
                        '-----BEGIN CERTIFICATE-----\nMIIDJTCCAg0CFCAduDeRYB6lFOlyOzpJjH0TM9dhMA0GCSqGSIb3DQEBCwUAME8x\nCzAJBgNVBAYTAkNOMRAwDgYDVQQIDAdKaWFuZ3N1MQ8wDQYDVQQHDAZTdXpob3Ux\nDDAKBgNVBAoMA1hYWDEPMA0GA1UEAwwGU2VsZkNBMB4XDTI0MDMyNzAwNTAxNFoX\nDTM0MDMyNTAwNTAxNFowTzELMAkGA1UEBhMCQ04xEDAOBgNVBAgMB0ppYW5nc3Ux\nDzANBgNVBAcMBlN1emhvdTEMMAoGA1UECgwDWFhYMQ8wDQYDVQQDDAZjbGllbnQw\nggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDAGQVTwPGX5EkU7ozj71IU\nzDIlV0emdlzTfsOQmUqB+Pvjk2XB38NevlKUb3jIei1KJ7vDWQWAiMQbbtgowRlU\n6VhHDdsrYTP4bJz5J8HxBh2nFggiA5kwRdbuQ7USXQR3sjUe2kjeeYW/V1Xx3kC1\nW5rfWPjuAfV0hW5EBlEHHG9OO+jHoXQympjrwO9Vhgcrn6ogxQ82gDbPdIZXqu2i\nIsHVFUPT4TGqS6aFeGZmkLSlgNcgxV7RYKiWobJLcRrrV/Nk9cJOZBNYoVuK+iCe\nmh+PA7HxXlrlAze3GwU0GIMASY9tx1LfibNHZj+6SweKYRAP3aD078R5QDTfpGWl\nAgMBAAEwDQYJKoZIhvcNAQELBQADggEBADjHSwhemmvHLXz6BP7DywftGRseLT6I\nr73bNXwcPJLynp83Rl7BxCd0SQ1ZQNxxkJQT49oaKW6vNCN35/g8ycZ5kA5HcM11\nTFg+TbghrcPVOXAD0LyCGKUpWL3NTGO+XHJM13c4jO+pMGTLi+JYSMP3WcUH6Xan\nDkcyZ2/kZrWztwoUREa29LvYalJWhx/mC9u2K7wkmiH/V9if/9iX9v3aRWn8sLDw\noRA4cEz6rwYfJdLDxF56f1Jc4G08lI23Flk/hQY00bJTlG8UlAl+fdke3FkkIn8P\neqqBZhJur0CB3mmnivR6qt/hmiqnQ5IjWwAflkhS9LcbdHeZFJlq9pw=\n-----END CERTIFICATE-----' + '\r\n').encode(
                'utf-8'))
            print(self.ser.readlines())

            self.ser.write((fr'AT+MSSLKEYWR="{n3}",0,1679' + '\r\n').encode('utf-8'))
            print(self.ser.readlines())
            self.ser.write((
                    '-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEAwBkFU8Dxl+RJFO6M4+9SFMwyJVdHpnZc037DkJlKgfj745Nl\nwd/DXr5SlG94yHotSie7w1kFgIjEG27YKMEZVOlYRw3bK2Ez+Gyc+SfB8QYdpxYI\nIgOZMEXW7kO1El0Ed7I1HtpI3nmFv1dV8d5AtVua31j47gH1dIVuRAZRBxxvTjvo\nx6F0MpqY68DvVYYHK5+qIMUPNoA2z3SGV6rtoiLB1RVD0+ExqkumhXhmZpC0pYDX\nIMVe0WColqGyS3Ea61fzZPXCTmQTWKFbivognpofjwOx8V5a5QM3txsFNBiDAEmP\nbcdS34mzR2Y/uksHimEQD92g9O/EeUA036RlpQIDAQABAoIBAQC67V4WsxElChrn\niH6HKxHHdTByz6zEWjdYAumQ4uny8fNC7+K8Nt8pabB4CsUQ6Hr7xxBaNl05R1z1\niPZFKipZSzwA4IXef5cP7bkOZta9kIL4XWMKnk/J/pv4fOBNf0BirYIthKIWA1DX\n8ceLNgfnsr1RC4YoLLXKbjDvduoQLLOkthUM2o2c13FYJjcciqc882XnE0foHeni\nuQBm47ysjS18JaDyohpSlLW7OwX6DHhRyBGoqGk17XqjK6+eg6B1PirKYU32SSgg\n6PnnmKeRp82UJa15AqKPSmNwSgq7ZigSpRfUdiC0g6GlibmjC5qmsjDi1Wa8yrCE\nkQCP6n5hAoGBAPnf/9uq3/Dgo6oFecCGY066yapsQRlI+FBaUNPN2Wk9KLGaRvA5\nrXZ2iniwf+2jI5yJDx2WHlJuJWaCOVTBAHCD0dUqI/RYupWLqKLDl961Hipqj9eu\ncolZaXnleiSyIVgF2gbqL/NFZ/NmPzUZwUpWb9OI+nJA65inL96rM6S9AoGBAMTO\ndgJ+s23cy/nhTmIi2n9HlDz6AE5GjzGvlESoNKWBuS5eB8tFDk18fQtLLMGgIpvH\n95DTh97N+a7rTfoE3IAPCBIlC8K+19mlazqKcghjA4aGuFZGRtGriLXMuaDxyFT1\nwBnjLrnBWX6ejge0pf4UbmLQih3CIO6UDL5UmzcJAoGAQt0m+SAbdriV8wwuDU+o\nyUuAZWM8dEircc0JLfQ6hkfAWO4gp223tih4W11Xjj6Ga//dFJy0Fni0915Hex9+\nP512i+UP4/XOT/AkOxG91PGAVfdX8G4U5h4P9HdsnN8xvv0p34nRNPbQnzgwF8SB\njaPdnqxb4DDxGlM6owoK8r0CgYAaID5SPnebUgBR/7LkHDRdSSdIoPeBbKR9uA06\nwAmdHwdyPFFUjqpDZw9CfIxId/WgMH+Q3kPfNAC9U8daNWMALP6pSfmxtJv67Ja7\ngr14l4xUQ3YdHd8w3lCbsb3Cu9YYUTdbOGlvh1dWE75PD5AplpTA0WZEZQzyHv1C\nFwEz4QKBgQCdLSXYn7hX2JN4jeQ6yD234745L0mBZlc1svCH16XKV7pUfqexwuWx\niBrM3r3DDrVrYW7T3z43s5ovbN4z8ZpLYkdzSENkJuIWP40ezeSpPPiNIOXlvskc\nSdVVa3cnCXdhXiweZvJniI6UuahgUqcNu8DeoM599zNf5Iva8H8jOA==\n-----END RSA PRIVATE KEY-----' + '\r\n').encode(
                'utf-8'))
            print(self.ser.readlines())
    def get_all_data(self):
        if self.is_open:
            # 等待数据到达
            time.sleep(0.1)
            in_waiting = self.ser.in_waiting
            if in_waiting > 0:
                data = self.ser.read(in_waiting)
                decoded_data = data.decode('utf-8', errors='ignore')

                # 打印接收数据时的时间和内容
                timestamp_recv = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                print(f"[{timestamp_recv}] RECV: {decoded_data.strip()}")

                return decoded_data
        return ""

    def wait_for_regex(self, pattern=[r'OK'], checklist=None, timeout=10):
        """等待符合所有正则表达式的响应"""
        default_checklist = ["ERROR","REBOOTING","+MATREADY"]
        if checklist is None:
            checklist = default_checklist
        else:
            checklist.extend(default_checklist)

        matched_patterns = set()  # 用于记录已匹配的正则表达式
        target_patterns = set(pattern)  # 需要匹配的正则表达式集合

        if self.is_open:
            buffer = b''
            start_time = time.time()

            while (time.time() - start_time) < timeout:
                if self.ser.in_waiting > 0:
                    chunk = self.ser.read_all()
                    if chunk:
                        buffer += chunk
                        lines = buffer.split(b'\r\n')
                        buffer = lines[-1]
                        for line in lines[:-1]:
                            decoded_line = line.decode(errors='ignore').strip()
                            if decoded_line:
                                timestamp_recv = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                                print(f"[{timestamp_recv}] RECV: {decoded_line}")

                                # 检查是否包含checklist中的任意项
                                for check_item in checklist:
                                    if check_item in decoded_line:
                                        return False  # 遇到checklist中的项返回False

                                # 检查是否匹配目标正则表达式列表中的任意一个
                                for regex_pattern in pattern:
                                    print(f'当前匹配正则表达式：{regex_pattern}')
                                    if regex_pattern not in matched_patterns and re.search(regex_pattern, decoded_line):
                                        print(f'匹配成功：{regex_pattern}')
                                        matched_patterns.add(regex_pattern)

                                # 检查是否所有正则表达式都已匹配
                                if matched_patterns == target_patterns:
                                    return True  # 所有正则表达式都匹配成功返回True
                time.sleep(0.1)
            print(f"超时未找到所有关键词，当前匹配到的正则表达式为:{matched_patterns}，期望匹配到的正则表达式为:{target_patterns}")
            return False  # 超时未匹配所有正则表达式返回False
        return False
    def wait_for_regex_return(self, pattern, checklist=None, timeout=10):
        """
        等待符合正则表达式的响应，如果在等待过程中遇到checklist中的任意项，则返回False。
        找到匹配内容时返回接收到的所有内容，超时时也返回接收到的所有内容。

        Args:
            pattern (str): 需要匹配的正则表达式模式
            checklist (list): 需要避免的错误关键字列表，默认为空列表
            timeout (int): 超时时间(秒)

        Returns:
            str or bool: 找到匹配pattern的行返回接收到的所有内容，找到checklist中的项返回False，超时返回接收到的内容
        """
        default_checklist = ["ERROR", "REBOOTING", "+MATREADY"]
        if checklist is None:
            checklist = default_checklist
        else:
            checklist.extend(default_checklist)

        if self.is_open:
            buffer = b''
            start_time = time.time()
            response_lines = []

            while (time.time() - start_time) < timeout:
                if self.ser.in_waiting > 0:
                    chunk = self.ser.read_all()
                    if chunk:
                        buffer += chunk
                        lines = buffer.split(b'\r\n')
                        buffer = lines[-1]
                        for line in lines[:-1]:
                            decoded_line = line.decode(errors='ignore').strip()
                            if decoded_line:
                                timestamp_recv = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                                print(f"[{timestamp_recv}] RECV: {decoded_line}")

                                # 检查是否包含checklist中的任意项
                                for check_item in checklist:
                                    if check_item in decoded_line:
                                        return False  # 遇到checklist中的项返回False

                                # 检查是否匹配正则表达式
                                if re.search(pattern, decoded_line):
                                    # 找到匹配时，将当前行也加入结果并返回所有内容
                                    response_lines.append(decoded_line)
                                    return '\r\n'.join(response_lines)  # 找到匹配返回接收到的所有内容

                                response_lines.append(decoded_line)
                time.sleep(0.1)

            # 超时返回接收到的所有内容
            if buffer:
                final_line = buffer.decode(errors='ignore').strip()
                if final_line:
                    response_lines.append(final_line)
            return '\r\n'.join(response_lines)  # 超时返回接收到的内容

        return False  # 串口未打开返回False

    def wait_for_keywords(self, keywords=["OK"], checklist=None, timeout=10):
        """
        等待串口响应，当接收到的数据包含指定关键字列表中的所有关键字时返回True，
        如果在等待过程中遇到checklist中的任意项，则返回False。

        Args:
            keywords (list): 需要查找的关键字列表，默认为["OK"]
            checklist (list): 需要避免的错误关键字列表，默认为空列表
            timeout (int): 超时时间(秒)

        Returns:
            bool: 找到keywords中的所有关键字返回True，找到checklist中的项或超时返回False
        """
        default_checklist = ["ERROR", "REBOOTING", "+MATREADY"]
        if checklist is None:
            checklist = default_checklist
        else:
            checklist.extend(default_checklist)


        found_keywords = set()  # 用于记录已找到的关键字
        target_keywords = set(keywords)  # 需要查找的关键字集合

        if self.is_open:
            buffer = b''
            start_time = time.time()
            while (time.time() - start_time) < timeout:
                if self.ser.in_waiting > 0:
                    chunk = self.ser.read_all()
                    if chunk:
                        buffer += chunk
                        lines = buffer.split(b'\r\n')
                        buffer = lines[-1]
                        for line in lines[:-1]:
                            decoded_line = line.decode(errors='ignore').strip()
                            if decoded_line:
                                timestamp_recv = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                                print(f"[{timestamp_recv}] RECV: {decoded_line}")

                                # 检查是否包含checklist中的任意项
                                for check_item in checklist:
                                    if check_item in decoded_line:
                                        return False  # 遇到checklist中的项返回False

                                # 检查是否包含目标关键字列表中的任意一个
                                for keyword in keywords:
                                    if keyword in decoded_line and keyword not in found_keywords:
                                        found_keywords.add(keyword)

                                # 检查是否所有关键字都已找到
                                if found_keywords == target_keywords:
                                    return True  # 找到所有关键词返回True
                time.sleep(0.1)
            print(f"超时未找到所有关键词，当前找到的关键词为:{found_keywords}，期望找到的关键词为:{target_keywords}")
            return False  # 超时未找到所有关键词返回False
        return False  # 串口未打开返回False

    def wait_for_keywords_return(self, keywords='OK', checklist=None, timeout=10):
        """
        等待串口响应，当接收到的数据包含指定关键字时返回True，
        如果在等待过程中遇到checklist中的任意项，则返回False。
        超时时返回接收到的所有内容。

        Args:
            keywords (str): 需要查找的关键字，默认为'OK'
            checklist (list): 需要避免的错误关键字列表，默认为空列表
            timeout (int): 超时时间(秒)

        Returns:
            bool or str: 找到keywords返回True，找到checklist中的项返回False，超时返回接收到的内容
        """
        default_checklist = ["ERROR", "REBOOTING", "+MATREADY"]
        if checklist is None:
            checklist = default_checklist
        else:
            checklist.extend(default_checklist)

        if self.is_open:
            buffer = b''
            start_time = time.time()
            response_lines = []

            while (time.time() - start_time) < timeout:
                if self.ser.in_waiting > 0:
                    chunk = self.ser.read_all()
                    if chunk:
                        buffer += chunk
                        lines = buffer.split(b'\r\n')
                        buffer = lines[-1]
                        for line in lines[:-1]:
                            decoded_line = line.decode(errors='ignore').strip()
                            if decoded_line:
                                timestamp_recv = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                                print(f"[{timestamp_recv}] RECV: {decoded_line}")

                                # 检查是否包含checklist中的任意项
                                for check_item in checklist:
                                    if check_item in decoded_line:
                                        return False  # 遇到checklist中的项返回False

                                # 检查是否包含目标关键字
                                if keywords in decoded_line:
                                    # 找到关键字时，将当前行也加入结果并返回所有内容
                                    print("找到关键词",keywords)
                                    response_lines.append(f"[{timestamp_recv}] RECV: {decoded_line}")
                                    return '\r\n'.join(response_lines)  # 找到关键词返回接收到的所有内容

                                response_lines.append(f"[{timestamp_recv}] RECV: {decoded_line}")
                time.sleep(0.1)

            # 超时返回接收到的所有内容
            if buffer:
                final_line = buffer.decode(errors='ignore').strip()
                if final_line:
                    response_lines.append(final_line)
            return '\r\n'.join(response_lines)  # 超时返回接收到的内容

        return False  # 串口未打开返回False

    def wait_for_or_keywords(self, keywords1='OK', keywords2='ERROR', timeout=10):
        """
        等待串口响应，当接收到的数据包含任一关键字时返回True

        Args:
            keywords1 (str): 第一个关键字，默认为'OK'
            keywords2 (str): 第二个关键字，默认为'ERROR'
            timeout (int): 超时时间(秒)

        Returns:
            bool: 找到任一关键字返回True，超时未找到返回False
        """
        if self.is_open:
            buffer = b''
            start_time = time.time()

            while (time.time() - start_time) < timeout:
                if self.ser.in_waiting > 0:
                    chunk = self.ser.read_all()
                    if chunk:
                        buffer += chunk
                        lines = buffer.split(b'\r\n')
                        buffer = lines[-1]
                        for line in lines[:-1]:
                            decoded_line = line.decode(errors='ignore').strip()
                            if decoded_line:
                                timestamp_recv = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                                print(f"[{timestamp_recv}] RECV: {decoded_line}")
                                # 检查是否包含任一关键字
                                if keywords1 in decoded_line or keywords2 in decoded_line:
                                    return True  # 找到任一关键字返回True
                time.sleep(0.1)
            return False  # 超时未找到返回False
        return False  # 串口未打开返回False

    def wait_for_or_keywords_return(self, keywords1='OK', keywords2='ERROR', timeout=10):
        """
        等待串口响应，当接收到的数据包含任一关键字时返回所有接收到的内容，
        如果在超时时间内未找到任一关键字则抛出异常。

        Args:
            keywords1 (str): 第一个关键字，默认为'OK'
            keywords2 (str): 第二个关键字，默认为'ERROR'
            timeout (int): 超时时间(秒)

        Returns:
            str: 返回接收到的所有内容（找到任一关键字时）

        Raises:
            Exception: 超时未找到任一关键字时抛出异常
        """
        if self.is_open:
            buffer = b''
            start_time = time.time()
            response_lines = []

            while (time.time() - start_time) < timeout:
                if self.ser.in_waiting > 0:
                    chunk = self.ser.read_all()
                    if chunk:
                        buffer += chunk
                        lines = buffer.split(b'\r\n')
                        buffer = lines[-1]
                        for line in lines[:-1]:
                            decoded_line = line.decode(errors='ignore').strip()
                            if decoded_line:
                                timestamp_recv = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                                print(f"[{timestamp_recv}] RECV: {decoded_line}")

                                # 检查是否包含任一关键字
                                if keywords1 in decoded_line or keywords2 in decoded_line:
                                    # 找到任一关键字时，将当前行也加入结果并返回所有内容
                                    response_lines.append(decoded_line)
                                    return '\r\n'.join(response_lines)  # 找到任一关键字返回接收到的所有内容

                                response_lines.append(decoded_line)
                time.sleep(0.1)

            # 处理缓冲区中可能存在的最后一行完整数据
            if buffer:
                final_line = buffer.decode(errors='ignore').strip()
                if final_line:
                    timestamp_recv = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                    print(f"[{timestamp_recv}] RECV: {final_line}")
                    response_lines.append(final_line)

            # 超时未找到任一关键字，抛出异常
            newline = '\r\n'
            raise Exception(
                f"超时({timeout}秒)未找到关键字 '{keywords1}' 或 '{keywords2}'，接收到的内容: {newline.join(response_lines)}"
            )

        raise Exception("串口未打开")

    def wait_for_response_cx(self, timeout=1, no_data_threshold=0.5):
        """优化版本：确保在超时时仍处理完缓冲区数据"""
        if self.is_open:
            response_lines = []
            buffer = b''
            start_time = time.time()
            last_data_time = start_time
            # no_data_threshold = 0.5  # 500ms无数据则返回
            read_once = 0

            while True:
                # 检查是否超过了总超时时间，但如果之前接收过数据，则继续等待直到no_data_threshold时间无数据
                elapsed_time = time.time() - start_time

                # 如果从未接收过数据且已超过timeout，则退出
                if read_once == 0 and elapsed_time >= timeout:
                    break

                # 如果接收过数据，只有在超过no_data_threshold时间没有新数据时才退出
                if read_once == 1 and (time.time() - last_data_time) > no_data_threshold:
                    break

                # 检查是否有数据可读
                if self.ser.in_waiting > 0:
                    chunk = self.ser.read_all()
                    if chunk:
                        buffer += chunk
                        lines = buffer.split(b'\r\n')
                        buffer = lines[-1]

                        for line in lines[:-1]:
                            decoded_line = line.decode(errors='ignore').strip()
                            if decoded_line:
                                timestamp_recv = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                                print(f"[{timestamp_recv}] RECV: {decoded_line}")

                                response_lines.append(timestamp_recv + decoded_line)
                                last_data_time = time.time()  # 收到数据时更新时间
                                read_once = 1
                # 如果还没有接收过数据，但已达到超时时间，则退出
                elif read_once == 0 and elapsed_time >= timeout:
                    break

                time.sleep(0.05)  # 减少睡眠时间提高响应速度

            # 关键修改：即使超时也要处理缓冲区中剩余的完整行
            if buffer:
                # 处理缓冲区中可能存在的最后一行完整数据
                final_line = buffer.decode(errors='ignore').strip()
                if final_line:
                    timestamp_recv = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                    print(f"[{timestamp_recv}] RECV: {decoded_line}")

                    response_lines.append(timestamp_recv + final_line)

            return '\r\n'.join(response_lines)
        return ""

    def wait_for_response(self, timeout=1,no_data_threshold=0.5):
        """优化版本：确保在超时时仍处理完缓冲区数据"""
        if self.is_open:
            response_lines = []
            buffer = b''
            start_time = time.time()
            last_data_time = start_time
            # no_data_threshold = 0.5  # 500ms无数据则返回
            read_once = 0

            while (time.time() - start_time) < timeout:
                if self.ser.in_waiting > 0:
                    chunk = self.ser.read_all()
                    if chunk:
                        buffer += chunk
                        lines = buffer.split(b'\r\n')
                        buffer = lines[-1]

                        for line in lines[:-1]:
                            decoded_line = line.decode(errors='ignore').strip()
                            if decoded_line:
                                timestamp_recv = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                                print(f"[{timestamp_recv}] RECV: {decoded_line}")

                                # if 'ERROR' in decoded_line:
                                #     self.logger.error(f"[{timestamp_recv}] RECV: {decoded_line}")
                                # else:
                                #     self.logger.info(f"[{timestamp_recv}] RECV: {decoded_line}")

                                response_lines.append(timestamp_recv + decoded_line)
                                last_data_time = time.time()  # 收到数据时更新时间
                                read_once = 1
                if(read_once == 1) and (time.time() - last_data_time) > no_data_threshold:
                    break

                time.sleep(0.05)  # 减少睡眠时间提高响应速度

            # 关键修改：即使超时也要处理缓冲区中剩余的完整行
            if buffer:
                # 处理缓冲区中可能存在的最后一行完整数据
                final_line = buffer.decode(errors='ignore').strip()
                if final_line:
                    timestamp_recv = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                    print(f"[{timestamp_recv}] RECV: {final_line}")

                    # if 'ERROR' in final_line:
                    #     self.logger.error(f"[{timestamp_recv}] RECV: {final_line}")
                    # else:
                    #     self.logger.info(f"[{timestamp_recv}] RECV: {final_line}")

                    response_lines.append(timestamp_recv + final_line)

            return '\r\n'.join(response_lines)
        return ""

    def wait_for_error(self,keywords=['ERROR'], timeout=10):
        """
        等待串口响应，当接收到的数据包含ERROR关键字时返回True，
        如果在等待过程中遇到"OK","REBOOTING","+MATREADY"等正常或重启关键字，或者超时未找到ERROR，则返回False。

        Args:
            timeout (int): 超时时间(秒)

        Returns:
            bool: 找到ERROR返回True，找到正常/重启关键字或超时返回False
        """
        # 定义需要避免的正常或重启关键字列表
        forbidden_keywords = ["OK", "REBOOTING", "+MATREADY"]
        found_keywords = set()  # 用于记录已找到的关键字
        target_keywords = set(keywords)  # 需要查找的关键字集合
        if self.is_open:
            buffer = b''
            start_time = time.time()
            response_lines = []

            while (time.time() - start_time) < timeout:
                if self.ser.in_waiting > 0:
                    chunk = self.ser.read_all()
                    if chunk:
                        buffer += chunk
                        lines = buffer.split(b'\r\n')
                        buffer = lines[-1]
                        for line in lines[:-1]:
                            decoded_line = line.decode(errors='ignore').strip()
                            if decoded_line:
                                timestamp_recv = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                                print(f"[{timestamp_recv}] RECV: {decoded_line}")

                                # 检查是否包含需要避免的正常或重启关键字
                                for forbidden_item in forbidden_keywords:
                                    if forbidden_item in decoded_line:
                                        return False  # 觐到正常/重启关键字返回False

                                # # 检查是否包含目标错误关键字
                                # if "ERROR" in decoded_line:
                                #     return True  # 找到ERROR返回True
                                # 检查是否包含目标关键字列表中的任意一个
                                for keyword in keywords:
                                    if keyword in decoded_line and keyword not in found_keywords:
                                        found_keywords.add(keyword)

                                # 检查是否所有关键字都已找到
                                if found_keywords == target_keywords:
                                    return True  # 找到所有关键词返回True

                                response_lines.append(decoded_line)
                time.sleep(0.1)

            # 超时返回False
            return False  # 超时未找到ERROR返回False

        return False  # 串口未打开返回False

    def wait_for_keywords_withpartcheck(self, keywords='OK', checklist=None, timeout=10):
        """
        等待串口响应，当接收到的数据包含指定关键字时返回所有接收到的内容，
        如果在等待过程中遇到"ERROR","REBOOTING","+MATREADY"或checklist中的任意项，则抛出异常。

        Args:
            keywords (str): 需要查找的关键字，默认为'OK'
            checklist (list): 需要避免的错误关键字列表，默认为空列表
            timeout (int): 超时时间(秒)

        Returns:
            str: 返回接收到的所有内容（找到keywords或超时都会返回）

        Raises:
            Exception: 遇到"ERROR","REBOOTING","+MATREADY"或checklist中的项时抛出异常
        """
        if checklist is None:
            checklist = []

        # 固定的检查列表
        fixed_checklist = ["ERROR", "REBOOTING", "+MATREADY"]
        # 合并检查列表
        combined_checklist = fixed_checklist + checklist

        if self.is_open:
            buffer = b''
            start_time = time.time()
            response_lines = []

            while (time.time() - start_time) < timeout:
                if self.ser.in_waiting > 0:
                    chunk = self.ser.read_all()
                    if chunk:
                        buffer += chunk
                        lines = buffer.split(b'\r\n')
                        buffer = lines[-1]
                        for line in lines[:-1]:
                            decoded_line = line.decode(errors='ignore').strip()
                            if decoded_line:
                                timestamp_recv = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                                print(f"[{timestamp_recv}] RECV: {decoded_line}")

                                # 检查是否包含固定检查列表或自定义检查列表中的任意项
                                for check_item in combined_checklist:
                                    if check_item in decoded_line:
                                        raise Exception(f"检测到禁止内容 '{check_item}' 在响应中: {decoded_line}")

                                # 检查是否包含目标关键字
                                if keywords in decoded_line:
                                    # 找到关键字时，将当前行也加入结果并返回所有内容
                                    response_lines.append(decoded_line)
                                    return '\r\n'.join(response_lines)  # 找到关键词返回接收到的所有内容

                                response_lines.append(decoded_line)
                time.sleep(0.1)

            # 超时返回接收到的所有内容
            if buffer:
                final_line = buffer.decode(errors='ignore').strip()
                if final_line:
                    response_lines.append(final_line)
            return '\r\n'.join(response_lines)  # 超时返回接收到的内容

        return "串口未打开"  # 串口未打开返回空字符串

    def wait_for_error_withpartcheck(self, keywords='ERROR', timeout=10):
        """
        等待串口响应，当接收到的数据包含指定错误关键字时返回所有接收到的内容，
        如果在等待过程中遇到"OK","REBOOTING","+MATREADY"等正常或重启关键字，则抛出异常。

        Args:
            keywords (str): 需要查找的错误关键字，默认为'ERROR'
            timeout (int): 超时时间(秒)

        Returns:
            str: 返回接收到的所有内容（找到keywords或超时都会返回）

        Raises:
            Exception: 遇到"OK","REBOOTING","+MATREADY"等正常或重启响应时抛出异常
        """
        # 定义需要避免的正常或重启关键字列表
        forbidden_keywords = ["OK", "REBOOTING", "+MATREADY"]

        if self.is_open:
            buffer = b''
            start_time = time.time()
            response_lines = []

            while (time.time() - start_time) < timeout:
                if self.ser.in_waiting > 0:
                    chunk = self.ser.read_all()
                    if chunk:
                        buffer += chunk
                        lines = buffer.split(b'\r\n')
                        buffer = lines[-1]
                        for line in lines[:-1]:
                            decoded_line = line.decode(errors='ignore').strip()
                            if decoded_line:
                                timestamp_recv = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                                print(f"[{timestamp_recv}] RECV: {decoded_line}")

                                # 检查是否包含需要避免的正常或重启关键字
                                for forbidden_item in forbidden_keywords:
                                    if forbidden_item in decoded_line:
                                        raise Exception(f"检测到禁止内容 '{forbidden_item}' 在响应中: {decoded_line}")

                                # 检查是否包含目标错误关键字
                                if keywords in decoded_line:
                                    # 找到错误关键字时，将当前行也加入结果并返回所有内容
                                    response_lines.append(decoded_line)
                                    return '\r\n'.join(response_lines)  # 找到错误关键词返回接收到的所有内容

                                response_lines.append(decoded_line)
                time.sleep(0.1)

            # 超时返回接收到的所有内容
            if buffer:
                final_line = buffer.decode(errors='ignore').strip()
                if final_line:
                    response_lines.append(final_line)
            return '\r\n'.join(response_lines)  # 超时返回接收到的内容

        return "串口未打开"  # 串口未打开返回提示信息

    def wait_for_reboot(self, keywords='REBOOTING', timeout=10):
        """
        等待串口响应，当接收到的数据包含指定重启关键字时返回所有接收到的内容，
        如果在等待过程中遇到"ERROR"关键字，则抛出异常。

        Args:
            keywords (str): 需要查找的重启关键字，默认为'REBOOTING'
            timeout (int): 超时时间(秒)

        Returns:
            str: 返回接收到的所有内容（找到keywords或超时都会返回）

        Raises:
            Exception: 遇到"ERROR"时抛出异常
        """
        # 定义需要避免的错误关键字
        error_keyword = "ERROR"

        if self.is_open:
            buffer = b''
            start_time = time.time()
            response_lines = []

            while (time.time() - start_time) < timeout:
                if self.ser.in_waiting > 0:
                    chunk = self.ser.read_all()
                    if chunk:
                        buffer += chunk
                        lines = buffer.split(b'\r\n')
                        buffer = lines[-1]
                        for line in lines[:-1]:
                            decoded_line = line.decode(errors='ignore').strip()
                            if decoded_line:
                                timestamp_recv = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                                print(f"[{timestamp_recv}] RECV: {decoded_line}")

                                # 检查是否包含错误关键字
                                if error_keyword in decoded_line:
                                    raise Exception(f"检测到错误内容 '{error_keyword}' 在响应中: {decoded_line}")

                                # 检查是否包含目标重启关键字
                                if keywords in decoded_line:
                                    # 找到重启关键字时，将当前行也加入结果并返回所有内容
                                    response_lines.append(decoded_line)
                                    return '\r\n'.join(response_lines)  # 找到重启关键词返回接收到的所有内容

                                response_lines.append(decoded_line)
                time.sleep(0.1)

            # 超时返回接收到的所有内容
            if buffer:
                final_line = buffer.decode(errors='ignore').strip()
                if final_line:
                    response_lines.append(final_line)
            return '\r\n'.join(response_lines)  # 超时返回接收到的内容

        return "串口未打开"  # 串口未打开返回提示信息
        
    def check_right_content(self, response_content, expected_patterns=None, forbidden_patterns=None):
        """
        陈翔——检查响应内容是否符合预期,属于校验函数

        Args:
            response_content (str): 要检查的响应内容
            expected_patterns (list): 应该出现的正则模式列表
            forbidden_patterns (list): 不应该出现的模式列表

        Returns:
            bool: 检查结果，True表示符合预期，False表示不符合
        """
        if expected_patterns is None:
            expected_patterns = []
        if forbidden_patterns is None:
            forbidden_patterns = []

        # 设置默认的禁止列表
        default_checklist = ["ERROR", "REBOOTING", "+MATREADY"]
        # 将传入的禁止模式追加到默认列表
        all_forbidden_patterns = default_checklist + forbidden_patterns

        # 检查是否包含禁止的模式
        for forbidden_pattern in all_forbidden_patterns:
            if forbidden_pattern in response_content:
                return False
        # 检查是否包含所有期望的正则模式
        for expected_pattern in expected_patterns:
            if not re.search(expected_pattern, response_content):
                return False
        return True
        
    def wait_keywords_content(self, keywords='OK', forbidden_patterns=None, timeout=5):
        """
        陈翔——等待包含指定关键字的响应内容，同时检查禁止出现的模式，属于接收函数，接收过程中带判断
        快速失败模式，但不抛出异常，而是返回状态标识

        Args:
            keywords (str or list): 需要查找的关键字，可以是单个字符串或字符串列表
            forbidden_patterns (list): 不应该出现的模式列表
            timeout (int): 超时时间(秒)

        Returns:
            str: 找到所有关键字且不包含禁止模式时返回接收到的所有内容
            False: 如果包含禁止模式时返回False
            None: 超时未找到所有指定关键字时返回None
        """
        print('keywords is', keywords)
        if forbidden_patterns is None:
            forbidden_patterns = []

        # 处理keywords参数，支持单个字符串或列表
        if isinstance(keywords, str):
            keywords_list = [keywords]
        elif isinstance(keywords, list):
            keywords_list = keywords
        else:
            keywords_list = [str(keywords)]

        # 预处理关键字列表，处理可能包含变量的正则表达式模式
        processed_keywords = []
        for keyword in keywords_list:
            # 去除可能的转义字符，确保正则表达式能够正确匹配
            processed_keyword = keyword.replace('\\+', '+').replace('\\.', '.').replace('\\*', '*')
            processed_keywords.append(processed_keyword)

        # 设置默认的禁止列表
        default_forbidden = ["ERROR", "REBOOTING", "+MATREADY"]
        # 将传入的禁止模式追加到默认列表
        all_forbidden_patterns = default_forbidden + forbidden_patterns

        if not self.is_open:
            return False  # 串口未打开返回False

        buffer = b''
        start_time = time.time()
        response_lines = []

        # 使用集合跟踪已找到的关键字（存储原始关键字索引）
        found_keywords_set = set()

        while (time.time() - start_time) < timeout:
            if self.ser.in_waiting > 0:
                chunk = self.ser.read_all()
                if chunk:
                    buffer += chunk
                    lines = buffer.split(b'\r\n')
                    buffer = lines[-1]
                    for line in lines[:-1]:
                        decoded_line = line.decode(errors='ignore').strip()
                        if decoded_line:
                            timestamp_recv = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                            print(f"[{timestamp_recv}] RECV: {decoded_line}")

                            # 检查是否包含禁止的模式 - 快速失败
                            for forbidden_pattern in all_forbidden_patterns:
                                if forbidden_pattern in decoded_line:
                                    response_lines.append(decoded_line)
                                    print(f"检测到禁止内容 '{forbidden_pattern}' 在响应中")
                                    return False  # 快速失败，返回False

                            # 检查是否包含目标关键字列表中的任意一个
                            for idx, (original_keyword, processed_keyword) in enumerate(
                                    zip(keywords_list, processed_keywords)):
                                # 使用正则表达式匹配处理过的关键字
                                if re.search(processed_keyword, decoded_line) and idx not in found_keywords_set:
                                    found_keywords_set.add(idx)

                            # 检查是否所有关键字都已找到
                            if len(found_keywords_set) == len(keywords_list):
                                response_lines.append(decoded_line)
                                return '\r\n'.join(response_lines)

                            response_lines.append(decoded_line)
            time.sleep(0.1)

        # 超时处理：返回None表示超时未找到所有关键字，并打印详细信息
        missing_indices = [idx for idx in range(len(keywords_list)) if idx not in found_keywords_set]
        missing_keywords = [keywords_list[idx] for idx in missing_indices]
        print(f"超时未找到所有关键字 '{keywords_list}' 中的某些关键字，缺失的关键字: {missing_keywords}")
        return None
