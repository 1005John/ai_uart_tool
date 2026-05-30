#!/usr/bin/env python3
"""知识图谱存储 - 三元组提取与管理"""
import re
import json
from datetime import datetime
from typing import Optional

from models.database import get_connection
from models.schemas import TestCaseRun


class KnowledgeStore:
    """
    知识图谱存储

    从测试结果中自动提取三元组知识:
    (模组, 执行指令, AT指令)
    (AT指令, 预期返回, 正则)
    (模组, 返回错误码, +CME ERROR: N)
    (错误码, 根因, AI分析)
    """

    def __init__(self):
        pass

    # ── 三元组提取 ──

    def extract_from_test_run(self, case_run: TestCaseRun, session_id: int = None):
        """
        从单条测试执行结果中提取知识三元组
        """
        triples = []
        model = "ML307C-DC"  # 可从会话中获取

        # 1. 提取AT指令前缀
        cmd_prefix = self._extract_cmd_prefix(case_run.at_command)

        # 2. (模组 → 执行 → AT指令)
        triples.append({
            "subject": model,
            "predicate": "执行指令",
            "object": cmd_prefix,
            "context": json.dumps({
                "full_command": case_run.at_command,
                "status": case_run.status,
                "sheet": case_run.case.sheet_name if case_run.case else "",
            }, ensure_ascii=False),
            "confidence": 1.0,
            "source": "test_run",
            "session_id": session_id,
        })

        # 3. (AT指令 → 预期返回 → 期望结果)
        if case_run.expected:
            triples.append({
                "subject": cmd_prefix,
                "predicate": "预期返回",
                "object": str(case_run.expected)[:100],
                "context": json.dumps({
                    "full_expected": case_run.expected,
                    "case_name": case_run.case.case_name if case_run.case else "",
                }, ensure_ascii=False),
                "confidence": 0.9,
                "source": "test_run",
                "session_id": session_id,
            })

        # 4. 如果 FAIL → 提取错误信息
        if case_run.status == "FAIL" and case_run.actual:
            # 提取错误码
            error_codes = self._extract_errors(case_run.actual)
            for err in error_codes:
                # (模组 → 返回 → 错误码)
                triples.append({
                    "subject": model,
                    "predicate": "返回错误",
                    "object": err,
                    "context": json.dumps({
                        "at_command": case_run.at_command,
                        "case_name": case_run.case.case_name if case_run.case else "",
                    }, ensure_ascii=False),
                    "confidence": 1.0,
                    "source": "test_run",
                    "session_id": session_id,
                })

                # (AT指令 → 返回错误 → 错误码)
                triples.append({
                    "subject": cmd_prefix,
                    "predicate": "返回错误",
                    "object": err,
                    "context": json.dumps({
                        "actual": case_run.actual[:200],
                    }, ensure_ascii=False),
                    "confidence": 1.0,
                    "source": "test_run",
                    "session_id": session_id,
                })

                # (错误码 → 根因 → AI分析)
                if case_run.ai_analysis:
                    triples.append({
                        "subject": err,
                        "predicate": "根因",
                        "object": case_run.ai_analysis[:200],
                        "context": json.dumps({
                            "full_analysis": case_run.ai_analysis,
                            "at_command": case_run.at_command,
                        }, ensure_ascii=False),
                        "confidence": 0.7,
                        "source": case_run.ai_analysis[:20] if case_run.ai_analysis else "ai",
                        "session_id": session_id,
                    })

        # 5. PASS → (AT指令 → 测试通过 → 次数)
        if case_run.status == "PASS":
            triples.append({
                "subject": cmd_prefix,
                "predicate": "测试通过",
                "object": "1次",
                "context": json.dumps({
                    "at_command": case_run.at_command,
                }, ensure_ascii=False),
                "confidence": 0.9,
                "source": "test_run",
                "session_id": session_id,
            })

        return triples

    def extract_from_batch(self, case_runs: list[TestCaseRun],
                           session_id: int = None) -> list[dict]:
        """批量提取三元素"""
        all_triples = []
        for run in case_runs:
            all_triples.extend(self.extract_from_test_run(run, session_id))
        return all_triples

    def save_triples(self, triples: list[dict]):
        """保存三元素到数据库"""
        if not triples:
            return 0

        conn = get_connection()
        count = 0
        for t in triples:
            conn.execute("""
                INSERT INTO knowledge_triples
                    (subject, predicate, object, context, confidence, source, session_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                t['subject'], t['predicate'], t['object'],
                t.get('context'), t.get('confidence', 1.0),
                t.get('source', 'test_run'), t.get('session_id'),
            ))
            count += 1
        conn.commit()
        conn.close()
        return count

    # ── 辅助方法 ──

    def _extract_cmd_prefix(self, command: str) -> str:
        """提取AT指令前缀"""
        if not command:
            return "UNKNOWN"
        # AT+QMTSUB=0,1,... → AT+QMTSUB
        match = re.match(r'(AT\+[\w]+)', command, re.IGNORECASE)
        if match:
            return match.group(1)
        # Sheet名如 "AT+MQTTSUB"
        return command.split("=")[0].strip()

    def _extract_errors(self, text: str) -> list[str]:
        """提取返回中的错误码"""
        errors = []
        patterns = [
            r'\+CME ERROR:\s*(\d+)',
            r'\+CMS ERROR:\s*(\d+)',
            r'\bERROR\b',
        ]
        for pat in patterns:
            matches = re.findall(pat, text)
            for m in matches:
                err = f"+CME ERROR: {m}" if m.isdigit() else "ERROR"
                if err not in errors:
                    errors.append(err)
        return errors or ["ERROR"]


if __name__ == "__main__":
    ks = KnowledgeStore()

    # 测试提取
    from models.schemas import TestCase
    fake_case = TestCase(excel_file="", sheet_name="AT+QMTSUB", row_id=1,
                         test_group="sub", case_name="测试", applicable_models=["ALL"])
    fake_run = TestCaseRun(
        session_id=0, case=fake_case, status="FAIL",
        at_command='AT+QMTSUB=0,1,"sensor/temp",0',
        expected="['+QMTSUB: 0,1,0,0']",
        actual="+CME ERROR: 50",
        ai_analysis="connect_id未建立连接，需先执行AT+QMTOPEN"
    )

    triples = ks.extract_from_test_run(fake_run, session_id=1)
    print("提取的三元组:")
    for t in triples:
        print(f"  ({t['subject']}) --[{t['predicate']}]--> ({t['object']})")
        if t.get('context'):
            ctx = json.loads(t['context'])
            print(f"    context: {dict(list(ctx.items())[:3])}")

    # 保存
    n = ks.save_triples(triples)
    print(f"\n已保存 {n} 条三元组到数据库")
