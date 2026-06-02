#!/usr/bin/env python3
"""串口引擎 - pyserial 封装，跨平台"""
import serial
import serial.tools.list_ports
import threading
import time
import re
from typing import Optional, Callable
from datetime import datetime


def _safe_decode(data: bytes, fallback: str = 'latin-1') -> str:
    """安全解码：按 UTF-8 → GBK → fallback 顺序尝试"""
    if not data:
        return ''
    for enc in ['utf-8', 'gbk', 'gb2312', fallback]:
        try:
            return data.decode(enc)
        except (UnicodeDecodeError, UnicodeError):
            continue
    # 最后兜底
    return data.decode('latin-1', errors='replace')


class SerialEngine:
    """
    串口引擎

    功能:
    - 扫描可用COM口
    - 打开/关闭串口
    - 发送数据
    - 接收数据（支持超时/模式匹配/流式回调）
    - 自动重连检测
    - 多编码支持（UTF-8/GBK/ASCII 自动回退）
    """

    def __init__(self):
        self.ser: Optional[serial.Serial] = None
        self.is_open = False
        self.port = ""
        self.baudrate = 115200
        self._recv_buffer = b""
        self._recv_callback: Optional[Callable[[bytes, str], None]] = None
        self._lock = threading.Lock()
        self._recv_thread: Optional[threading.Thread] = None
        self._running = False

    # ── 端口扫描 ──

    @staticmethod
    def list_ports() -> list[dict]:
        """扫描可用串口"""
        ports = []
        for p in serial.tools.list_ports.comports():
            ports.append({
                "port": p.device,
                "description": p.description,
                "hwid": p.hwid,
                "manufacturer": p.manufacturer or "",
                "product": p.product or "",
            })
        return ports

    @staticmethod
    def list_ports_text() -> str:
        ports = SerialEngine.list_ports()
        if not ports:
            return "未发现可用串口"
        lines = ["可用串口:"]
        for p in ports:
            lines.append(f"  {p['port']} - {p['description']}")
        return "\n".join(lines)

    # ── 连接管理 ──

    def open(self, port: str, baudrate: int = 115200, timeout: float = 3,
             bytesize: int = serial.EIGHTBITS, parity: str = serial.PARITY_NONE,
             stopbits: float = serial.STOPBITS_ONE) -> bool:
        """打开串口"""
        try:
            self.ser = serial.Serial(
                port=port,
                baudrate=baudrate,
                bytesize=bytesize,
                parity=parity,
                stopbits=stopbits,
                timeout=timeout
            )
            self.is_open = True
            self.port = port
            self.baudrate = baudrate
            self._recv_buffer = b""
            print(f"[Serial] ✅ 已打开 {port} @ {baudrate}")
            return True
        except serial.SerialException as e:
            print(f"[Serial] ❌ 打开失败: {e}")
            self.is_open = False
            return False

    def close(self):
        """关闭串口"""
        self._running = False
        if self._recv_thread and self._recv_thread.is_alive():
            self._recv_thread.join(timeout=2)
        if self.ser and self.ser.is_open:
            try:
                self.ser.close()
            except:
                pass
        self.is_open = False
        print(f"[Serial] 🔒 已关闭 {self.port}")

    def is_connected(self) -> bool:
        return self.is_open and self.ser and self.ser.is_open

    # ── 数据收发 ──

    def send(self, data: str, hex_mode: bool = False, with_enter: bool = True) -> int:
        """
        发送数据到串口
        Args:
            data: 要发送的数据
            hex_mode: 是否按16进制解析
            with_enter: 是否追加 \\r\\n
        Returns: 发送字节数
        """
        if not self.is_connected():
            raise RuntimeError("串口未打开")

        if hex_mode:
            # 16进制字符串 → 字节
            data = data.replace(" ", "").replace("\n", "").replace("\r", "")
            if len(data) % 2 == 1:
                data += "0"
            payload = bytes.fromhex(data)
        else:
            payload = data.encode('utf-8', errors='replace')
            if with_enter:
                payload += b"\r\n"

        with self._lock:
            written = self.ser.write(payload)
            self.ser.flush()

        direction = "HEX" if hex_mode else "ASCII"
        preview = payload[:80]
        print(f"[Serial] >>> [{direction}] {preview}{'...' if len(payload) > 80 else ''}")
        return written

    def send_at(self, at_command: str) -> int:
        """快捷发送AT指令（自动追加\\r\\n）"""
        return self.send(at_command, hex_mode=False, with_enter=True)

    def read(self, size: int = 4096, timeout: float = None) -> bytes:
        """读取数据"""
        if not self.is_connected():
            raise RuntimeError("串口未打开")
        if self.ser.in_waiting == 0:
            time.sleep(0.05)
        data = self.ser.read(min(size, self.ser.in_waiting or 1))
        if data:
            print(f"[Serial] <<< {_safe_decode(data[:80])}")
        return data

    def read_all(self) -> bytes:
        """读取全部可用数据"""
        if not self.is_connected():
            return b""
        data = self.ser.read(self.ser.in_waiting or 1)
        if data:
            print(f"[Serial] <<< {_safe_decode(data[:120])}")
        return data

    def send_and_wait(self, command: str, expected_patterns: list = None,
                      timeout: float = 5.0, hex_mode: bool = False,
                      with_enter: bool = True) -> dict:
        """
        发送指令并等待响应

        Returns:
            {"success": bool, "response": str, "matched_pattern": str, "duration_ms": int}
        """
        self.send(command, hex_mode=hex_mode, with_enter=with_enter)
        return self.wait_for(expected_patterns or [r"OK"], timeout=timeout)

    def wait_for(self, patterns: list, timeout: float = 5.0) -> dict:
        """
        等待串口返回匹配指定模式

        Args:
            patterns: 正则表达式列表，任一匹配即成功
            timeout: 超时秒数

        Returns:
            {"success": bool, "response": str, "matched_pattern": str, "duration_ms": int}
        """
        if not self.is_connected():
            return {"success": False, "response": "", "matched_pattern": "", "duration_ms": 0}

        buffer = b""
        start = time.time()

        while time.time() - start < timeout:
            if self.ser.in_waiting:
                data = self.ser.read(self.ser.in_waiting)
                buffer += data

            text = _safe_decode(buffer)

            for pattern in patterns:
                if re.search(pattern, text, re.MULTILINE):
                    elapsed = int((time.time() - start) * 1000)
                    print(f"[Serial] ✅ 匹配: /{pattern}/ → {elapsed}ms")
                    return {
                        "success": True,
                        "response": text,
                        "matched_pattern": pattern,
                        "duration_ms": elapsed
                    }

            time.sleep(0.01)

        elapsed = int((time.time() - start) * 1000)
        text = _safe_decode(buffer)
        print(f"[Serial] ⏰ 超时({timeout}s)，已接收: {text[:100]}")
        return {
            "success": False,
            "response": text,
            "matched_pattern": "",
            "duration_ms": elapsed
        }

    # ── 流式接收（后台线程） ──

    def start_stream(self, callback: Callable[[bytes, str], None] = None):
        """启动后台接收线程"""
        if self._recv_thread and self._recv_thread.is_alive():
            return
        self._running = True
        self._recv_callback = callback or self._default_callback
        self._recv_thread = threading.Thread(target=self._recv_loop, daemon=True)
        self._recv_thread.start()
        print("[Serial] 📡 后台接收已启动")

    def stop_stream(self):
        self._running = False

    def _recv_loop(self):
        while self._running and self.is_connected():
            try:
                if self.ser.in_waiting:
                    data = self.ser.read(self.ser.in_waiting)
                    self._recv_buffer += data
                    text = _safe_decode(data)
                    if self._recv_callback:
                        self._recv_callback(data, text)
                else:
                    time.sleep(0.01)
            except Exception as e:
                print(f"[Serial] 接收异常: {e}")
                break

    def _default_callback(self, data: bytes, text: str):
        print(f"[Serial] <<< {text.rstrip()}")

    # ── 便捷工具 ──

    def auto_connect(self, baudrate: int = 115200) -> bool:
        """自动连接第一个可用串口"""
        ports = self.list_ports()
        for p in ports:
            if self.open(p['port'], baudrate):
                return True
        return False


# ── 独立测试 ──
if __name__ == "__main__":
    eng = SerialEngine()
    print(eng.list_ports_text())
