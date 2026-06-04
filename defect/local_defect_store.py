#!/usr/bin/env python3
"""本地缺陷存储 - SQLite + JSON 导出"""
import json
import os
from datetime import datetime
from typing import Optional

from models.database import get_connection


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFECT_DIR = os.path.join(PROJECT_ROOT, "defects")


class LocalDefectStore:
    """
    本地缺陷存储

    功能:
    - 创建缺陷（写入 SQLite + 导出 JSON 文件）
    - 查询缺陷列表
    - 更新缺陷状态
    - 导出 JSON
    """

    def __init__(self):
        os.makedirs(DEFECT_DIR, exist_ok=True)

    # ── 创建 ──

    def create_defect(self, title: str, description: str, test_session_id: int = None,
                      test_case_run_id: int = None, severity: int = 2,
                      priority: int = 1) -> int:
        """
        创建新缺陷

        Args:
            title: 缺陷标题
            description: 缺陷描述（含环境/步骤/分析）
            test_session_id: 关联的测试会话ID
            test_case_run_id: 关联的测试用例执行ID
            severity: 严重程度 1-4
            priority: 优先级 1-3

        Returns: 本地缺陷ID
        """
        conn = get_connection()
        cur = conn.execute("""
            INSERT INTO local_defects 
                (title, description, severity, priority, status,
                 test_session_id, test_case_run_id)
            VALUES (?, ?, ?, ?, 'local', ?, ?)
        """, (title, description, severity, priority,
              test_session_id, test_case_run_id))
        defect_id = cur.lastrowid
        conn.commit()

        # 导出 JSON
        self._export_json(defect_id)

        conn.close()
        return defect_id

    def create_from_test_run(self, case_run_id: int, title: str,
                              description: str) -> int:
        """从测试执行记录创建缺陷"""
        conn = get_connection()
        row = conn.execute(
            "SELECT session_id FROM test_case_runs WHERE id=?",
            (case_run_id,)
        ).fetchone()
        session_id = row['session_id'] if row else None

        return self.create_defect(
            title=title,
            description=description,
            test_session_id=session_id,
            test_case_run_id=case_run_id,
        )

    # ── 查询 ──

    def list_defects(self, status: str = None, limit: int = 50,
                     created_after: str = None) -> list[dict]:
        """列出缺陷

        Args:
            status: 按状态筛选
            limit: 最大条数
            created_after: ISO格式时间，只返回 created_at >= 该时间的缺陷
        """
        conn = get_connection()
        sql = "SELECT * FROM local_defects"
        params = []
        filters = []
        if status:
            filters.append("status=?")
            params.append(status)
        if created_after:
            filters.append("created_at >= ?")
            params.append(created_after)
        if filters:
            sql += " WHERE " + " AND ".join(filters)
        sql += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        rows = conn.execute(sql, params).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_defect(self, defect_id: int) -> Optional[dict]:
        """获取单个缺陷"""
        conn = get_connection()
        row = conn.execute(
            "SELECT * FROM local_defects WHERE id=?", (defect_id,)
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    def list_by_status(self) -> dict:
        """按状态分组统计"""
        conn = get_connection()
        rows = conn.execute("""
            SELECT status, COUNT(*) as count FROM local_defects
            GROUP BY status
        """).fetchall()
        conn.close()
        return {r['status']: r['count'] for r in rows}

    # ── 更新 ──

    def update_status(self, defect_id: int, status: str,
                      lingji_id: str = None):
        """更新缺陷状态"""
        conn = get_connection()
        now = datetime.now().isoformat()

        if status == 'submitted' and lingji_id:
            conn.execute("""
                UPDATE local_defects SET status=?, lingji_id=?, submitted_at=?
                WHERE id=?
            """, (status, lingji_id, now, defect_id))
        elif status == 'synced':
            conn.execute("""
                UPDATE local_defects SET status=?, synced_at=? WHERE id=?
            """, (status, now, defect_id))
        else:
            conn.execute(
                "UPDATE local_defects SET status=? WHERE id=?",
                (status, defect_id)
            )
        conn.commit()
        conn.close()

        # 重新导出 JSON
        self._export_json(defect_id)

    def update_description(self, defect_id: int, description: str):
        """更新缺陷描述"""
        conn = get_connection()
        conn.execute(
            "UPDATE local_defects SET description=? WHERE id=?",
            (description, defect_id)
        )
        conn.commit()
        conn.close()
        self._export_json(defect_id)

    # ── 删除 ──

    def delete_defect(self, defect_id: int):
        """删除缺陷（SQLite + JSON 文件）"""
        conn = get_connection()
        conn.execute("DELETE FROM local_defects WHERE id=?", (defect_id,))
        conn.commit()
        conn.close()
        # 删除 JSON 文件
        fpath = os.path.join(DEFECT_DIR, f"defect_{defect_id:04d}.json")
        if os.path.exists(fpath):
            os.remove(fpath)

    # ── JSON 导出 ──

    def _export_json(self, defect_id: int):
        """导出单个缺陷为 JSON 文件"""
        defect = self.get_defect(defect_id)
        if not defect:
            return

        # 移除不需要的字段
        export = {k: v for k, v in defect.items()
                  if k not in ('id',) and v is not None}
        export['local_id'] = defect['id']

        # 格式化时间
        for key in ('created_at', 'submitted_at', 'synced_at'):
            if key in export and export[key]:
                export[key] = str(export[key])

        # 写入文件
        filename = f"defect_{defect_id:04d}.json"
        filepath = os.path.join(DEFECT_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export, f, ensure_ascii=False, indent=2)

        # 更新 local_file 字段（相对路径）
        rel_path = os.path.relpath(filepath, PROJECT_ROOT)
        conn = get_connection()
        conn.execute(
            "UPDATE local_defects SET local_file=? WHERE id=?",
            (rel_path, defect_id)
        )
        conn.commit()
        conn.close()

    def export_all(self) -> str:
        """导出所有缺陷到 JSON 文件"""
        defects = self.list_defects()
        summary_path = os.path.join(DEFECT_DIR, "defects_summary.json")
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump({
                "export_time": datetime.now().isoformat(),
                "total": len(defects),
                "defects": defects,
            }, f, ensure_ascii=False, indent=2)
        return summary_path

    # ── 格式化输出 ──

    def format_list(self, defects: list[dict] = None) -> str:
        """缺陷列表 → 可读文本"""
        if defects is None:
            defects = self.list_defects()

        if not defects:
            return "暂无本地缺陷"

        lines = [f"📋 本地缺陷共 {len(defects)} 条:"]
        for d in defects:
            status_icon = {
                'local': '📝', 'submitted': '📤', 'synced': '✅'
            }.get(d['status'], '📋')
            lingji = f" → 灵畿#{d['lingji_id']}" if d.get('lingji_id') else ""
            lines.append(
                f"  {status_icon} #{d['id']:04d} [{d['status']}]{lingji}"
            )
            lines.append(f"     {d['title'][:80]}")
        return "\n".join(lines)


if __name__ == "__main__":
    store = LocalDefectStore()
    print("缺陷目录:", DEFECT_DIR)
    print("当前缺陷:", store.list_by_status())
