#!/usr/bin/env python3
"""缺陷管理 Agent - AI 驱动的缺陷创建与同步"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from defect.local_defect_store import LocalDefectStore
from defect.lingji_sync import LingjiSync
from llm.llm_client import LLMClient
from llm.prompts import DEFECT_DESCRIPTION_PROMPT
from models.schemas import TestCaseRun
from models.database import get_connection


class DefectAgent:
    """
    缺陷管理 Agent

    功能:
    - AI 生成缺陷描述
    - 创建本地缺陷 + JSON 导出
    - 提交到灵畿平台
    - 同步校验
    - 列表查看
    """

    def __init__(self, llm: LLMClient = None):
        self.llm = llm or LLMClient()
        self.store = LocalDefectStore()
        self.sync = LingjiSync()

    # ── AI 生成缺陷描述 ──

    def generate_description(self, case_run: TestCaseRun, module: str = "") -> str:
        """AI 生成标准缺陷描述"""
        if not case_run.ai_analysis:
            case_run.ai_analysis = "等待分析"

        prompt = DEFECT_DESCRIPTION_PROMPT.format(
            module=module or (case_run.case.sheet_name if case_run.case else ""),
            case_name=case_run.case.case_name if case_run.case else "",
            at_command=case_run.at_command or "",
            expected=case_run.expected or "",
            actual=case_run.actual or "无返回(超时)",
            model="ML307C-DC",
            ai_analysis=case_run.ai_analysis,
        )
        return self.llm.chat([{"role": "user", "content": prompt}],
                            temperature=0.2, max_tokens=1024)

    def generate_title(self, case_run: TestCaseRun) -> str:
        """AI 生成缺陷标题"""
        title = f"【{case_run.case.sheet_name}】{case_run.case.case_name} 测试失败"
        if len(title) > 100:
            title = title[:97] + "..."
        return title

    # ── 创建本地缺陷 ──

    def create_local(self, case_run: TestCaseRun, description: str = None) -> dict:
        """
        创建本地缺陷

        Returns:
            {"ok": bool, "defect_id": int, "file": str, "message": str}
        """
        title = self.generate_title(case_run)
        if not description:
            description = self.generate_description(case_run)

        # 获取 test_case_run_id
        case_run_id = None
        if hasattr(case_run, 'case') and case_run.case:
            conn = get_connection()
            row = conn.execute(
                "SELECT id FROM test_case_runs WHERE session_id=? AND case_name=?",
                (case_run.session_id, case_run.case.case_name)
            ).fetchone()
            if row:
                case_run_id = row['id']
            conn.close()

        defect_id = self.store.create_defect(
            title=title,
            description=description,
            test_session_id=case_run.session_id,
            test_case_run_id=case_run_id,
        )

        defect = self.store.get_defect(defect_id)
        return {
            "ok": True,
            "defect_id": defect_id,
            "file": defect.get('local_file', '') if defect else '',
            "message": f"✅ 本地缺陷 #{defect_id:04d} 已创建",
        }

    # ── 提交到灵畿 ──

    def submit_to_lingji(self, defect_id: int) -> dict:
        """
        提交单个缺陷到灵畿平台

        Returns:
            {"ok": bool, "lingji_id": str, "message": str}
        """
        defect = self.store.get_defect(defect_id)
        if not defect:
            return {"ok": False, "lingji_id": None, "message": "缺陷不存在"}

        result = self.sync.create_bug(
            title=defect['title'],
            description=defect['description'],
            severity=defect.get('severity', 2),
            priority=defect.get('priority', 1),
        )

        if result['ok'] and result['bug_id']:
            self.store.update_status(defect_id, 'submitted', lingji_id=result['bug_id'])
            return {
                "ok": True,
                "lingji_id": result['bug_id'],
                "message": f"✅ 已提交到灵畿平台，缺陷ID: #{result['bug_id']}",
            }
        elif result['ok']:
            self.store.update_status(defect_id, 'submitted')
            return {
                "ok": True,
                "lingji_id": None,
                "message": "已在灵畿创建成功，但未获取到ID（稍后可通过'灵畿同步'补全）",
            }
        else:
            return {
                "ok": False,
                "lingji_id": None,
                "message": f"❌ 提交失败: {result['message']}",
            }

    def submit_batch(self, defect_ids: list[int]) -> list[dict]:
        """批量提交"""
        results = []
        for did in defect_ids:
            r = self.submit_to_lingji(did)
            results.append(r)
            import time
            time.sleep(0.5)  # 防止限流
        return results

    # ── 同步校验 ──

    def sync_check(self) -> list[dict]:
        """
        校验本地与灵畿的一致性

        Returns: 不一致的缺陷列表
        """
        submitted = self.store.list_defects(status='submitted')
        issues = []

        for defect in submitted:
            if not defect.get('lingji_id'):
                issues.append({
                    "defect_id": defect['id'],
                    "type": "MISSING_ID",
                    "message": f"缺陷 #{defect['id']:04d} 缺少灵畿ID",
                })
                continue

            # 尝试在灵畿查询
            bug = self.sync.get_bug(defect['lingji_id'])
            if bug is None:
                issues.append({
                    "defect_id": defect['id'],
                    "type": "NOT_FOUND",
                    "message": f"灵畿ID #{defect['lingji_id']} 不存在",
                })

        return issues

    # ── 格式化输出 ──

    def format_defect_detail(self, defect_id: int) -> str:
        """格式化缺陷详情"""
        defect = self.store.get_defect(defect_id)
        if not defect:
            return "❌ 缺陷不存在"

        status_map = {
            'local': '📝 本地',
            'submitted': '📤 已提交',
            'synced': '✅ 已同步',
        }
        status_str = status_map.get(defect['status'], defect['status'])
        lingji = f"灵畿ID: #{defect['lingji_id']}" if defect.get('lingji_id') else "未提交"

        lines = [
            f"缺陷 #{defect['id']:04d} [{status_str}]",
            f"{lingji}",
            f"标题: {defect['title']}",
            f"严重程度: {defect.get('severity', 2)}/4  优先级: {defect.get('priority', 1)}/3",
            f"",
            f"描述:",
            f"{defect.get('description', '无')[:500]}",
        ]

        if defect.get('local_file'):
            lines.append(f"\n本地文件: {defect['local_file']}")

        return "\n".join(lines)


if __name__ == "__main__":
    agent = DefectAgent()
    print("缺陷目录:", os.path.join(os.path.dirname(os.path.dirname(__file__)), "defects"))
    print("灵畿登录:", agent.sync.check_login())
