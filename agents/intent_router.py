#!/usr/bin/env python3
"""意图路由 - LLM驱动的自然语言理解"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm.llm_client import LLMClient
from llm.prompts import INTENT_CLASSIFICATION_PROMPT
from engines.excel_loader import ExcelTestLoader


class IntentRouter:
    """
    意图路由器

    使用 LLM 解析用户自然语言输入，
    映射到具体意图和参数。
    """

    INTENT_DESCRIPTIONS = {
        "serial": "串口操作：打开、关闭、扫描、配置波特率等",
        "test": "测试相关：执行测试、查看用例列表、分析结果",
        "defect": "缺陷管理：创建缺陷、提交到灵畿平台",
        "knowledge": "知识查询：AT指令含义、模组参数、历史测试记录",
        "greeting": "问候或闲聊",
        "help": "请求帮助",
    }

    def __init__(self, llm: LLMClient = None):
        self.llm = llm or LLMClient()
        self.loader = ExcelTestLoader()

    def classify(self, user_input: str) -> str:
        """判断意图"""
        prompt = INTENT_CLASSIFICATION_PROMPT.format(user_input=user_input)
        resp = self.llm.chat([{"role": "user", "content": prompt}],
                            temperature=0.1, max_tokens=50)
        intent = resp.strip().lower()

        # 映射到标准意图
        known = list(self.INTENT_DESCRIPTIONS.keys())
        for k in known:
            if k in intent:
                return k
        return "unknown"

    def extract_params(self, user_input: str, intent: str) -> dict:
        """
        从用户输入中提取参数

        示例:
        "帮我测MQTT的P0" → {"module": "mqtt", "level": "P0"}
        "打开COM3,115200" → {"port": "COM3", "baudrate": "115200"}
        """
        params = {}

        if intent == "test":
            params = self._extract_test_params(user_input)
        elif intent == "serial":
            params = self._extract_serial_params(user_input)
        elif intent == "knowledge":
            params = self._extract_query_params(user_input)

        return params

    def _extract_test_params(self, text: str) -> dict:
        """提取测试相关参数"""
        text_lower = text.lower()

        # 提取模块名
        modules = [m['key'] for m in self.loader.list_modules()]
        found_module = None
        for mod in modules:
            if mod.lower() in text_lower:
                found_module = mod
                break
        # 也匹配中文名
        cn_map = {
            "mqtt": ["mqtt", "消息队列"],
            "tcp": ["tcp", "tcp协议"],
            "http": ["http", "网页"],
            "sms": ["短信"],
            "gnss": ["定位", "gps", "gnss"],
            "fota": ["升级", "fota"],
        }
        if not found_module:
            for mod, keywords in cn_map.items():
                if any(kw in text_lower for kw in keywords):
                    found_module = mod
                    break

        # 提取级别
        level = "P0"
        if "p1" in text_lower or "详细" in text_lower:
            level = "P1"
        elif "全部" in text_lower or "所有" in text_lower:
            level = "P0"  # 全部级别

        # 提取模组
        model = ""
        for m in ["ml307c", "ml307", "mn316", "mn319"]:
            if m in text_lower:
                model = m.upper()
                break

        result = {"module": found_module, "level": level, "model": model}
        return {k: v for k, v in result.items() if v}

    def _extract_serial_params(self, text: str) -> dict:
        """提取串口参数"""
        import re
        text_lower = text.lower()

        params = {}

        # 提取端口号
        port_match = re.search(r'(COM\d+|tty\w+)', text, re.IGNORECASE)
        if port_match:
            params['port'] = port_match.group(1)

        # 提取波特率
        baud_match = re.search(r'(\d+)\s*波特|波特率\s*(\d+)', text)
        if not baud_match:
            baud_match = re.search(r'\b(9600|115200|57600|38400|19200)\b', text)
        if baud_match:
            for g in baud_match.groups():
                if g:
                    params['baudrate'] = int(g)
                    break

        # 提取操作
        if any(kw in text_lower for kw in ["打开", "连接", "open", "开串"]):
            params['action'] = 'open'
        elif any(kw in text_lower for kw in ["关闭", "断开", "close", "关串"]):
            params['action'] = 'close'
        elif any(kw in text_lower for kw in ["扫描", "scan", "列出串", "看看"]):
            params['action'] = 'scan'
        # "列表" 单独出现时可能有歧义，默认不映射

        return params

    def _extract_query_params(self, text: str) -> dict:
        """提取知识查询参数"""
        import re
        text_lower = text.lower()
        params = {"query": text}

        # AT指令
        at_match = re.search(r'(AT\+[\w=?,]*)', text, re.IGNORECASE)
        if at_match:
            params['at_command'] = at_match.group(1)

        return params

    def format_modules_help(self) -> str:
        """生成模块帮助文本"""
        modules = self.loader.list_modules()
        lines = ["可用测试模块:"]
        for m in modules:
            cases = self.loader.load_cases(m['key'])
            lines.append(f"  {m['key']:15s} {m['description']:20s} {len(cases):4d}条用例")
        return "\n".join(lines)


if __name__ == "__main__":
    router = IntentRouter()
    test_inputs = [
        "帮我测一下MQTT订阅功能",
        "打开串口COM3",
        "为什么AT+QMTSUB会返回ERROR",
        "你好",
        "扫描可用串口",
    ]
    for inp in test_inputs:
        intent = router.classify(inp)
        params = router.extract_params(inp, intent)
        print(f"  {inp:30s} → {intent:10s} {params}")
