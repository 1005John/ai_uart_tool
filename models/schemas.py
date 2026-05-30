#!/usr/bin/env python3
"""数据模型 - 数据类定义"""
from dataclasses import dataclass, field
from typing import Optional, Any
from datetime import datetime


@dataclass
class TestCase:
    """来自Excel的一行测试用例"""
    excel_file: str
    sheet_name: str
    row_id: int
    test_group: str
    case_name: str
    case_level: str = 'P0'
    applicable_models: list = field(default_factory=lambda: ["ALL"])
    params: dict = field(default_factory=dict)
    expected_results: list = field(default_factory=list)
    selected: bool = True
    timeout: int = 10
    delay_after: int = 0

    @property
    def display_name(self) -> str:
        return f"[{self.case_level}] {self.case_name}"


@dataclass
class ExecutableCase:
    """可执行的测试用例（已转换AT指令）"""
    original_case: TestCase
    at_command: str
    expected_patterns: list
    timeout: int = 10
    delay_after: int = 0


@dataclass
class TestPlan:
    """测试计划"""
    module: str
    cases: list[TestCase]
    model: str = ""
    port: str = ""
    baudrate: int = 115200
    custom_params: dict = field(default_factory=dict)

    @property
    def total(self) -> int:
        return len([c for c in self.cases if c.selected])

    @property
    def p0_count(self) -> int:
        return len([c for c in self.cases if c.selected and c.case_level == 'P0'])

    @property
    def estimated_time(self) -> str:
        avg_per_case = 3  # seconds
        total = self.total * avg_per_case
        if total < 60:
            return f"{total}秒"
        return f"{total // 60}分{total % 60}秒"


@dataclass
class TestCaseRun:
    """单条用例执行结果"""
    session_id: int
    case: TestCase
    at_command: str = ""
    expected: str = ""
    actual: str = ""
    status: str = 'PENDING'
    fail_reason: str = ""
    ai_analysis: str = ""
    duration_ms: int = 0


@dataclass
class TestResult:
    """测试结果汇总"""
    session_id: int
    session_name: str
    module: str
    case_runs: list[TestCaseRun]
    summary: str = ""

    @property
    def total(self) -> int:
        return len(self.case_runs)

    @property
    def passed(self) -> int:
        return len([c for c in self.case_runs if c.status == 'PASS'])

    @property
    def failed(self) -> int:
        return len([c for c in self.case_runs if c.status == 'FAIL'])

    @property
    def pass_rate(self) -> float:
        if self.total == 0:
            return 0.0
        return self.passed / self.total * 100

    @property
    def failures(self) -> list[TestCaseRun]:
        return [c for c in self.case_runs if c.status == 'FAIL']

    def format_summary(self) -> str:
        lines = [
            f"====== 测试结果: {self.session_name} ======",
            f"模组: {self.case_runs[0].case.applicable_models if self.case_runs else 'N/A'}",
            f"总计: {self.total}  |  ✅ PASS: {self.passed}  |  ❌ FAIL: {self.failed}  |  通过率: {self.pass_rate:.1f}%",
        ]
        if self.failures:
            lines.append("")
            lines.append("--- FAIL 明细 ---")
            for f in self.failures:
                lines.append(f"  ❌ [{f.case.case_level}] {f.case.case_name}")
                lines.append(f"     AT: {f.at_command}")
                lines.append(f"     预期: {f.expected}")
                lines.append(f"     实际: {f.actual}")
                if f.ai_analysis:
                    lines.append(f"     AI分析: {f.ai_analysis}")
        return "\n".join(lines)
