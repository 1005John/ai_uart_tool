#!/usr/bin/env python3
"""预期结果匹配器 - 支持正则/多模式/错误码匹配"""
import re
from typing import Optional


class ResultMatcher:
    """
    AT指令返回结果匹配器

    支持:
    - 正则匹配（默认）
    - 多模式匹配（任意一个匹配即成功）
    - ERROR/CME ERROR 自动检测
    - 超时处理
    """

    # 常见错误模式
    ERROR_PATTERNS = [
        r"\+CME ERROR:?\s*\d*",
        r"\+CMS ERROR:?\s*\d*",
        r"\bERROR\b",
    ]

    @staticmethod
    def match(actual: str, expected_patterns: list) -> dict:
        """
        匹配实际返回与预期模式

        Args:
            actual: 串口实际返回文本
            expected_patterns: 预期模式列表，空列表默认匹配 "OK"

        Returns:
            {"matched": True/False, "matched_pattern": "", "reason": ""}
        """
        if not actual:
            return {"matched": False, "matched_pattern": "", "reason": "无返回数据"}

        patterns = expected_patterns or [r"OK"]

        for pattern in patterns:
            try:
                if re.search(pattern, actual, re.MULTILINE | re.DOTALL):
                    return {"matched": True, "matched_pattern": pattern, "reason": ""}
            except re.error as e:
                # 正则无效时，尝试精确字符串匹配
                if pattern in actual:
                    return {"matched": True, "matched_pattern": pattern, "reason": ""}

        return {"matched": False, "matched_pattern": "", "reason": f"未匹配到预期模式"}

    @staticmethod
    def has_error(actual: str) -> Optional[str]:
        """检查返回中是否包含错误"""
        for pattern in ResultMatcher.ERROR_PATTERNS:
            m = re.search(pattern, actual, re.MULTILINE)
            if m:
                return m.group(0)
        return None

    @staticmethod
    def extract_value(actual: str, pattern: str) -> Optional[str]:
        """从返回中提取特定值"""
        m = re.search(pattern, actual, re.MULTILINE)
        if m:
            return m.group(1) if m.lastindex else m.group(0)
        return None
