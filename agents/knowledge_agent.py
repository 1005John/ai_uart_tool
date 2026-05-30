#!/usr/bin/env python3
"""AI 知识查询 Agent"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from knowledge.knowledge_store import KnowledgeStore
from knowledge.knowledge_querier import KnowledgeQuerier
from llm.llm_client import LLMClient


class KnowledgeAgent:
    """
    知识查询 Agent

    功能:
    - 从测试结果自动提取知识
    - 查询历史相似失败
    - 查询模组能力
    - 自然语言知识问答
    """

    def __init__(self, llm: LLMClient = None):
        self.llm = llm or LLMClient()
        self.store = KnowledgeStore()
        self.querier = KnowledgeQuerier()

    def ingest_test_result(self, case_run, session_id: int = None):
        """吸收测试结果到知识图谱"""
        triples = self.store.extract_from_test_run(case_run, session_id)
        count = self.store.save_triples(triples)
        return count

    def ingest_batch(self, case_runs: list, session_id: int = None):
        """批量吸收"""
        triples = self.store.extract_from_batch(case_runs, session_id)
        count = self.store.save_triples(triples)
        return count

    def query(self, text: str) -> str:
        """
        自然语言知识查询

        自动判断查询类型并返回格式化结果
        """
        text_lower = text.lower()

        # 1. 统计概览
        if "统计" in text or "概览" in text or "知识图谱" in text:
            stats = self.querier.get_statistics()
            return self._format_stats(stats)

        # 2. 模组能力
        if "能力" in text or "支持" in text or "模组" in text:
            model = "ML307C-DC"
            caps = self.querier.get_model_capabilities(model)
            if caps.get('supported_commands'):
                return self.querier.format_capabilities(caps)

        # 3. 错误码查询
        import re
        err_match = re.search(r'(CME ERROR[:\s]*(\d+)|ERROR\s*(\d+))', text, re.IGNORECASE)
        if err_match:
            error_code = err_match.group(0).strip()
            results = self.querier.find_similar_failures(error=error_code)
            if results:
                base = self.querier.format_similar_failures(results)
                # 用 LLM 补充解释
                llm_explain = self.llm.chat([{
                    "role": "user",
                    "content": f"请解释物联网模组AT指令中的{error_code}是什么含义，以及常见原因。简短专业，100字以内。"
                }], temperature=0.3, max_tokens=200)
                return f"{llm_explain}\n\n{base}"
            else:
                return self.llm.chat([{
                    "role": "user",
                    "content": f"请解释物联网模组AT指令中的{error_code}是什么含义。简短专业，100字以内。"
                }], temperature=0.3, max_tokens=200)

        # 4. AT指令查询
        at_match = re.search(r'(AT\+[\w]+)', text, re.IGNORECASE)
        if at_match:
            at_cmd = at_match.group(1)
            errors = self.querier.find_errors_for_command(at_cmd)
            similar = self.querier.find_similar_failures(at_command=at_cmd)

            lines = [f"🔍 **{at_cmd} 相关知识:**"]
            if errors:
                lines.append(f"\n出现过以下错误:")
                for e in errors[:5]:
                    lines.append(f"  • {e['error_code']} ({e['occurances']}次)")
            if similar:
                lines.append(f"\n历史分析:")
                for s in similar[:3]:
                    lines.append(f"  • {s['analysis'][:100]}")
            if not errors and not similar:
                lines.append("\n暂无该指令的历史测试数据")
            return "\n".join(lines)

        # 5. 自由搜索
        results = self.querier.search(text, limit=10)
        if results:
            return self.querier.format_search(results)

        # 6. 兜底：LLM 回答
        return self.llm.chat([{
            "role": "system",
            "content": "你是物联网模组AT指令测试专家。基于专业知识回答，简洁专业。"
        }, {
            "role": "user",
            "content": f"问题: {text}"
        }], temperature=0.3, max_tokens=512)

    def _format_stats(self, stats: dict) -> str:
        lines = [
            "📊 **知识图谱统计**",
            f"",
            f"三元组总数: {stats.get('total_triples', 0)}",
            f"独立实体数: {stats.get('unique_subjects', 0)}",
            f"关系类型: {', '.join(stats.get('unique_predicates', []))}",
        ]
        if stats.get('top_errors'):
            lines.append(f"\n**常见错误:**")
            for e in stats['top_errors'][:5]:
                lines.append(f"  • {e['error']} ({e['count']}次)")
        if stats.get('models_tested'):
            lines.append(f"\n**已测试模组:**")
            for m in stats['models_tested']:
                lines.append(f"  • {m['model']} ({m['tests']}条)")
        return "\n".join(lines)


if __name__ == "__main__":
    agent = KnowledgeAgent()
    print("知识图谱Agent启动...")
    stats = agent.querier.get_statistics()
    print(f"当前: {stats['total_triples']} 条三元组")
