#!/usr/bin/env python3
"""知识查询引擎 - 搜索历史相似失败/模组能力/统计"""
import json
from typing import Optional
from datetime import datetime

from models.database import get_connection


class KnowledgeQuerier:
    """
    知识查询引擎

    功能:
    - 搜索历史相似失败 (find_similar_failures)
    - 查询模组能力 (get_model_capabilities)
    - 全文本搜索 (search)
    - 统计概览 (get_statistics)
    """

    def __init__(self):
        pass

    # ── 相似失败查询 ──

    def find_similar_failures(self, at_command: str = None,
                               error: str = None,
                               model: str = None,
                               limit: int = 5) -> list[dict]:
        """
        查找历史相似失败

        Args:
            at_command: AT指令前缀 (如 "AT+QMTSUB")
            error: 错误码 (如 "+CME ERROR: 50")
            model: 模组型号
            limit: 返回条数

        Returns:
            [{"at_command", "error", "analysis", "model", "time"}]
        """
        conn = get_connection()
        conditions = ["predicate = '根因'"]
        params = []

        # 通过关联的 subject (错误码) 搜索
        if error:
            conditions.append("subject LIKE ?")
            params.append(f"%{error}%")

        # 通过 context 中的 AT 指令搜索
        if at_command:
            conditions.append("context LIKE ?")
            params.append(f"%{at_command}%")

        # 通过 subject 或 object 搜索
        if model:
            # model 可能出现在 subject 或 context 中
            conditions.append("(subject LIKE ? OR context LIKE ?)")
            params.extend([f"%{model}%", f"%{model}%"])

        where = " AND ".join(conditions) if conditions else "1=1"

        rows = conn.execute(f"""
            SELECT subject, predicate, object, context, source, created_at
            FROM knowledge_triples
            WHERE {where}
            ORDER BY created_at DESC
            LIMIT ?
        """, (*params, limit)).fetchall()

        conn.close()

        results = []
        for r in rows:
            ctx = {}
            if r['context']:
                try:
                    ctx = json.loads(r['context'])
                except:
                    ctx = {"raw": r['context']}

            results.append({
                "error_code": r['subject'],
                "predicate": r['predicate'],
                "analysis": r['object'],
                "at_command": ctx.get('at_command', ''),
                "case_name": ctx.get('case_name', ''),
                "full_analysis": ctx.get('full_analysis', r['object']),
                "time": str(r['created_at']),
            })

        return results

    def find_errors_for_command(self, at_command: str) -> list[dict]:
        """查找某个AT指令出现过的所有错误"""
        conn = get_connection()
        rows = conn.execute("""
            SELECT DISTINCT subject as error_code, object as analysis,
                   COUNT(*) as occurances
            FROM knowledge_triples
            WHERE predicate = '根因'
              AND context LIKE ?
            GROUP BY subject
            ORDER BY occurances DESC
        """, (f"%{at_command}%",)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # ── 模组能力 ──

    def get_model_capabilities(self, model: str = "ML307C-DC") -> dict:
        """
        获取模组型号的能力矩阵

        基于历史测试数据自动构建:
        - 支持的AT指令列表
        - 各指令的预期返回
        - 已知的限制/不支持项
        - 常见的错误模式
        """
        conn = get_connection()

        # 1. 执行的AT指令
        cmd_rows = conn.execute("""
            SELECT DISTINCT object as cmd, COUNT(*) as count
            FROM knowledge_triples
            WHERE subject = ? AND predicate = '执行指令'
            GROUP BY object
            ORDER BY count DESC
        """, (model,)).fetchall()

        # 2. 返回过的错误
        err_rows = conn.execute("""
            SELECT DISTINCT object as error, COUNT(*) as count
            FROM knowledge_triples
            WHERE subject = ? AND predicate = '返回错误'
            GROUP BY object
            ORDER BY count DESC
        """, (model,)).fetchall()

        # 3. 通过测试的指令
        pass_rows = conn.execute("""
            SELECT DISTINCT subject as cmd
            FROM knowledge_triples
            WHERE predicate = '测试通过'
        """).fetchall()

        conn.close()

        return {
            "model": model,
            "supported_commands": [r['cmd'] for r in cmd_rows],
            "command_count": len(cmd_rows),
            "known_errors": [{"error": r['error'], "count": r['count']}
                            for r in err_rows],
            "passed_commands": [r['cmd'] for r in pass_rows],
            "last_updated": datetime.now().isoformat(),
        }

    # ── 通用搜索 ──

    def search(self, query: str, limit: int = 20) -> list[dict]:
        """
        全文本搜索三元组

        支持模糊匹配:
        search("AT+QMTSUB") → 所有相关的三元组
        search("ERROR 50") → 错误50的所有记录
        search("ML307C") → 该模组的所有信息
        """
        conn = get_connection()
        like = f"%{query}%"
        rows = conn.execute("""
            SELECT subject, predicate, object, context, confidence, source, created_at
            FROM knowledge_triples
            WHERE subject LIKE ?
               OR predicate LIKE ?
               OR object LIKE ?
               OR context LIKE ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (like, like, like, like, limit)).fetchall()
        conn.close()

        results = []
        for r in rows:
            results.append({
                "subject": r['subject'],
                "predicate": r['predicate'],
                "object": r['object'][:200],
                "confidence": r['confidence'],
                "source": r['source'],
                "time": str(r['created_at']),
            })
        return results

    # ── 统计 ──

    def get_statistics(self) -> dict:
        """知识图谱统计概览"""
        conn = get_connection()

        stats = {}
        stats['total_triples'] = conn.execute(
            "SELECT COUNT(*) as c FROM knowledge_triples"
        ).fetchone()['c']

        stats['unique_subjects'] = conn.execute(
            "SELECT COUNT(DISTINCT subject) as c FROM knowledge_triples"
        ).fetchone()['c']

        stats['unique_predicates'] = conn.execute(
            "SELECT DISTINCT predicate as p FROM knowledge_triples"
        ).fetchall()
        stats['unique_predicates'] = [r['p'] for r in stats['unique_predicates']]

        stats['top_errors'] = [
            dict(r) for r in conn.execute("""
                SELECT object as error, COUNT(*) as count
                FROM knowledge_triples
                WHERE predicate = '返回错误'
                GROUP BY object
                ORDER BY count DESC LIMIT 10
            """).fetchall()
        ]

        stats['models_tested'] = [
            dict(r) for r in conn.execute("""
                SELECT subject as model, COUNT(*) as tests
                FROM knowledge_triples
                WHERE predicate = '执行指令'
                GROUP BY subject
            """).fetchall()
        ]

        conn.close()
        return stats

    # ── 格式化输出 ──

    def format_similar_failures(self, results: list[dict]) -> str:
        """格式化相似失败查询结果"""
        if not results:
            return "📭 未找到历史相似记录"

        lines = ["🔍 **历史相似失败:**"]
        for i, r in enumerate(results[:5], 1):
            at = r.get('at_command', '')
            analysis = r.get('analysis', '')[:150]
            time = r.get('time', '')[:16]
            lines.append(f"  {i}. `{at}`")
            lines.append(f"     🤖 {analysis}")
            if time:
                lines.append(f"     🕐 {time}")
        return "\n".join(lines)

    def format_capabilities(self, caps: dict) -> str:
        """格式化模组能力"""
        if not caps or not caps.get('supported_commands'):
            return "暂无该模组的测试数据"

        lines = [
            f"📊 **{caps['model']} 能力矩阵**",
            f"",
            f"已测试指令: {caps['command_count']} 条",
            f"",
        ]

        if caps['supported_commands']:
            lines.append("**支持的AT指令:**")
            for cmd in caps['supported_commands'][:20]:
                lines.append(f"  • {cmd}")
            if len(caps['supported_commands']) > 20:
                lines.append(f"  ... 还有 {len(caps['supported_commands'])-20} 条")

        if caps['known_errors']:
            lines.append(f"\n**已知错误模式:**")
            for e in caps['known_errors'][:10]:
                lines.append(f"  • {e['error']} (出现 {e['count']} 次)")

        return "\n".join(lines)

    def format_search(self, results: list[dict]) -> str:
        """格式化搜索结果"""
        if not results:
            return "📭 未找到匹配结果"

        lines = [f"🔍 找到 {len(results)} 条结果:"]
        for r in results[:15]:
            lines.append(
                f"  ({r['subject']}) --[{r['predicate']}]--> ({r['object'][:80]})"
            )
        if len(results) > 15:
            lines.append(f"  ... 还有 {len(results)-15} 条")
        return "\n".join(lines)

    # ── 多维度筛选 ──

    def get_filter_options(self) -> dict:
        """获取所有筛选维度的可选值

        Returns:
            {"models": [...], "defect_titles": [...], "versions": [...], "years": [...]}
        """
        conn = get_connection()
        options = {}

        # 模组型号（只从缺陷描述提取，确保有对应缺陷）
        import re
        desc_rows = conn.execute(
            "SELECT DISTINCT description FROM local_defects WHERE description IS NOT NULL"
        ).fetchall()
        models = set()
        for d in desc_rows:
            desc = d['description'] or ''
            # 匹配 **模组型号:** 后的非空格内容
            m = re.search(r'\*\*模组型号:\*\*\s*\*{0,2}\s*(\S+)', desc)
            if m:
                val = m.group(1).strip('* ')
                # 过滤掉空值、横线（属于下一行字段）、路径等非型号内容
                if val and not val.startswith('-') and not val.startswith('/'):
                    models.add(val)
        options['models'] = sorted(models)

        # 固件版本
        versions = set()
        for d in desc_rows:
            desc = d['description'] or ''
            # 从 "固件版本: XXXX" 后开始截取直到下一个字段
            m = re.search(r'\*\*固件版本:\*\*\s*\*{0,2}\s*(.+?)(?:\s*-+\s*\*{2}|$)', desc, re.DOTALL)
            if m:
                v = m.group(1).strip().replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')[:60]
                # 过滤掉以 + 开头的内容（如 +MQTTURC 这种不是版本号）
                if v and not v.startswith('+'):
                    versions.add(v)
        options['versions'] = sorted(versions)

        # 缺陷标题
        rows = conn.execute(
            "SELECT DISTINCT title FROM local_defects ORDER BY title"
        ).fetchall()
        options['defect_titles'] = [r['title'][:60] for r in rows]

        # 年份
        rows = conn.execute("""
            SELECT DISTINCT substr(created_at,1,7) as ym
            FROM local_defects ORDER BY ym DESC
        """).fetchall()
        options['months'] = [r['ym'] for r in rows if r['ym']]

        conn.close()
        return options

    def faceted_query(self, models: list = None, versions: list = None,
                      defect_titles: list = None,
                      months: list = None,
                      date_start: str = None, date_end: str = None) -> dict:
        """多维度筛选查询

        Args:
            models: 模组型号列表
            versions: 固件版本列表
            defect_titles: 缺陷标题列表
            months: 月份列表 (YYYY-MM)
            date_start: 起始日期 (YYYY-MM-DD)
            date_end: 结束日期 (YYYY-MM-DD)

        Returns:
            {
                "matched_defects": [...],  # 匹配的缺陷
                "enriched": [...],          # 带型号/版本/时间的缺陷
                "summary": {...}           # 各维度统计
            }
        """
        conn = get_connection()
        import re

        # 先从 local_defects 筛选
        defect_conditions = []
        defect_params = []

        if defect_titles:
            placeholders = ",".join("?" for _ in defect_titles)
            defect_conditions.append(f"title IN ({placeholders})")
            defect_params.extend(defect_titles)

        if months:
            placeholders = ",".join("?" for _ in months)
            defect_conditions.append(f"substr(created_at,1,7) IN ({placeholders})")
            defect_params.extend(months)

        if date_start:
            defect_conditions.append("created_at >= ?")
            defect_params.append(date_start)
        if date_end:
            defect_conditions.append("created_at <= ?")
            defect_params.append(date_end + " 23:59:59")

        # 版本和模组型号需要从 description 中模糊匹配
        if versions or models:
            desc_conditions = []
            all_descs = conn.execute(
                "SELECT DISTINCT id, title, description, created_at, lingji_id, status "
                "FROM local_defects"
            ).fetchall()
            matched_ids = set()
            for d in all_descs:
                desc = d['description'] or ''
                match = True
                if models:
                    found = False
                    for m in models:
                        if re.search(r'模组型号[：:]\s*\*{0,2}\s*' + re.escape(m), desc):
                            found = True
                            break
                    if not found:
                        match = False
                if versions and match:
                    found = False
                    for v in versions:
                        if v in desc:
                            found = True
                            break
                    if not found:
                        match = False
                if match:
                    matched_ids.add(d['id'])

            if matched_ids:
                placeholders = ",".join("?" for _ in matched_ids)
                defect_conditions.append(f"id IN ({placeholders})")
                defect_params.extend(matched_ids)
            else:
                # 没有匹配任何缺陷
                conn.close()
                return {"matched_defects": [], "summary": {}}

        # 执行筛选
        where = ""
        if defect_conditions:
            where = "WHERE " + " AND ".join(defect_conditions)

        rows = conn.execute(f"""
            SELECT id, title, description, created_at, lingji_id, status
            FROM local_defects {where}
            ORDER BY created_at DESC LIMIT 200
        """, defect_params).fetchall()
        conn.close()

        matched = [dict(r) for r in rows]

        # 从匹配结果中提取各维度的值，并给每条缺陷附上型号/版本
        models_found = set()
        versions_found = set()
        months_found = set()
        titles_found = set()
        enriched = []
        for d in matched:
            desc = d['description'] or ''
            m = re.search(r'\*\*模组型号:\*\*\s*\*{0,2}\s*(\S+)', desc)
            mod = m.group(1).strip('* ') if m else ''
            if mod and not mod.startswith('-') and not mod.startswith('/'):
                models_found.add(mod)
            else:
                mod = ''
            m = re.search(r'\*\*固件版本:\*\*\s*\*{0,2}\s*(.+?)(?:\s*-+\s*\*{2}|$)', desc, re.DOTALL)
            ver = ''
            if m:
                ver = m.group(1).strip().replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')[:60]
                if ver.startswith('+'):
                    ver = ''
                else:
                    versions_found.add(ver)
            ym = str(d['created_at'])[:7] if d['created_at'] else ''
            if ym:
                months_found.add(ym)
            titles_found.add(d['title'][:60])
            enriched.append({
                "id": d['id'],
                "created_at": str(d['created_at'])[:10] if d['created_at'] else '',
                "title": d['title'][:60],
                "model": mod,
                "version": ver,
                "lingji_id": d.get('lingji_id', ''),
                "status": d['status'],
            })

        return {
            "matched_defects": matched,
            "enriched": enriched,
            "summary": {
                "total": len(matched),
                "models": sorted(models_found),
                "versions": sorted(versions_found),
                "months": sorted(months_found, reverse=True),
                "defect_titles": sorted(titles_found),
            }
        }
