#!/usr/bin/env python3
"""AI 测试 Agent - 测试计划生成 + 失败分析"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from knowledge.knowledge_store import KnowledgeStore
from llm.llm_client import LLMClient
from llm.prompts import TEST_PLAN_PROMPT, FAIL_ANALYSIS_PROMPT, DEFECT_DESCRIPTION_PROMPT
from engines.excel_loader import ExcelTestLoader
from engines.test_executor import TestExecutor
from models.schemas import TestPlan, TestCaseRun


class TestAgent:
    """
    AI 测试 Agent

    功能:
    - 理解用户测试需求 → 加载 Excel 用例 → 生成测试计划
    - 执行测试 → 实时反馈
    - AI 分析 FAIL → 生成缺陷草稿
    """

    def __init__(self, llm: LLMClient = None):
        self.llm = llm or LLMClient()
        self.loader = ExcelTestLoader()
        self.executor = TestExecutor(excel_loader=self.loader)
        self.knowledge = KnowledgeStore()
        self._last_result = None

    def generate_plan(self, module: str, model: str = "",
                      level: str = "P0") -> TestPlan:
        """
        生成测试计划（包含 AI 描述）

        1. 加载对应模块的用例
        2. 按级别/模组过滤
        3. 用 AI 生成计划描述
        """
        cases = self.loader.load_cases(
            module,
            case_level=[level],
            model=model,
        )

        if not cases:
            # 尝试加载全部级别
            cases = self.loader.load_cases(module, model=model)
            if not cases:
                return None

        plan = TestPlan(
            module=module,
            cases=cases,
            model=model or "未指定",
        )

        # 用 AI 生成计划描述
        cases_text = self._cases_to_plan_text(cases)
        ai_desc = self.llm.chat([{
            "role": "user",
            "content": TEST_PLAN_PROMPT.format(
                module=module,
                model=plan.model,
                case_level=level,
                cases_list=cases_text,
            )
        }], temperature=0.3, max_tokens=512)
        plan.ai_description = ai_desc

        return plan

    def _cases_to_plan_text(self, cases, max_show: int = 30) -> str:
        """用例列表转文本"""
        lines = []
        for c in cases[:max_show]:
            selected = "☑" if c.selected else "☐"
            lines.append(f"  {selected} [{c.case_level}] {c.case_name}  →  {c.sheet_name}")
        if len(cases) > max_show:
            lines.append(f"  ... 还有 {len(cases) - max_show} 条")
        return "\n".join(lines)

    def describe_plan(self, plan: TestPlan) -> str:
        """返回用户可读的测试计划"""
        if not plan:
            return "❌ 没有找到匹配的测试用例"

        # 按级别统计
        from collections import Counter
        level_counts = Counter(c.case_level for c in plan.cases if c.selected)

        lines = [
            f"📋 **{plan.module.upper()} 测试计划**",
            f"",
            f"模组: {plan.model}",
            f"总计: {plan.total} 条用例",
        ]
        for level in ["P0", "P1", "P2"]:
            if level in level_counts:
                lines.append(f"  {level}: {level_counts[level]} 条")

        lines.append(f"预计: {plan.estimated_time}")
        lines.append("")

        if hasattr(plan, 'ai_description') and plan.ai_description:
            lines.append(plan.ai_description)

        lines.append("")
        lines.append("输入 `开始执行` 运行测试")
        lines.append("输入 `调参` 调整参数")

        return "\n".join(lines)

    def execute_plan(self, plan: TestPlan, port: str = "",
                     baudrate: int = 115200, progress_callback=None) -> dict:
        """
        执行测试计划，返回结构化结果
        """
        def default_callback(run: TestCaseRun):
            icon = "✅" if run.status == "PASS" else "❌"
            print(f"  {icon} {run.case.case_name} ({run.duration_ms}ms)")

        cb = progress_callback or default_callback
        self.executor.set_progress_callback(cb)

        # 设置串口
        plan.port = port
        plan.baudrate = baudrate

        result = self.executor.execute_plan(plan)
        self._last_result = result

        # 自动吸收测试结果到知识图谱
        try:
            ingested = self.knowledge.extract_from_batch(result.case_runs, result.session_id)
            count = self.knowledge.save_triples(ingested)
            print(f"[Knowledge] 已吸收 {count} 条知识三元组")
        except Exception as e:
            print(f"[Knowledge] 吸收失败: {e}")

        return result

    def analyze_failure(self, case_run: TestCaseRun) -> str:
        """
        AI 分析失败原因
        """
        prompt = FAIL_ANALYSIS_PROMPT.format(
            case_name=case_run.case.case_name,
            at_command=case_run.at_command or case_run.case.sheet_name,
            expected=case_run.expected or str(case_run.case.expected_results),
            actual=case_run.actual or "无返回(超时)",
            model=case_run.case.case_level,
        )
        analysis = self.llm.chat([{"role": "user", "content": prompt}],
                                temperature=0.2, max_tokens=512)

        # 保存分析结果
        case_run.ai_analysis = analysis

        return analysis

    def generate_defect_draft(self, case_run: TestCaseRun) -> str:
        """
        生成缺陷草稿
        """
        prompt = DEFECT_DESCRIPTION_PROMPT.format(
            module=case_run.case.sheet_name,
            case_name=case_run.case.case_name,
            at_command=case_run.at_command,
            expected=case_run.expected or str(case_run.case.expected_results),
            actual=case_run.actual or "无返回(超时)",
            model="ML307C-DC",
            ai_analysis=case_run.ai_analysis or "待分析",
        )
        defect = self.llm.chat([{"role": "user", "content": prompt}],
                              temperature=0.2, max_tokens=1024)
        return defect

    def format_result_summary(self, result) -> str:
        """格式化测试结果"""
        if not result:
            return "无测试结果"

        lines = [
            f"📊 **测试完成: {result.session_name}**",
            f"",
            f"总计: {result.total} 条  |  ✅ PASS: {result.passed}  |  ❌ FAIL: {result.failed}  |  通过率: {result.pass_rate:.1f}%",
            f"",
        ]

        if result.failures:
            lines.append("--- ❌ FAIL 详情 ---")
            for i, f in enumerate(result.failures, 1):
                lines.append(f"")
                lines.append(f"**{i}. [{f.case.case_level}] {f.case.case_name}**")
                lines.append(f"   AT: `{f.at_command}`")
                lines.append(f"   预期: {f.expected}")
                lines.append(f"   实际: {f.actual[:100]}")
                # AI 分析
                if not f.ai_analysis:
                    f.ai_analysis = self.analyze_failure(f)
                lines.append(f"   🤖 AI 分析: {f.ai_analysis[:200]}")
                lines.append(f"   输入 `缺陷 {i}` 生成缺陷草稿")

        return "\n".join(lines)


if __name__ == "__main__":
    agent = TestAgent()
    plan = agent.generate_plan("mqtt", level="P0")
    print(agent.describe_plan(plan))
