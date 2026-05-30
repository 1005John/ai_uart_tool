#!/usr/bin/env python3
"""灵畿平台缺陷同步 - lc bug create 集成"""
import json
import os
import re
import subprocess
import time
from typing import Optional


# 默认配置
DEFAULT_CONFIG = {
    "workspace": "CMIOTonemoredcap",
    "project": "R2511D9QC0N",
    "handler_id": "1966881909663256588",
}


class LingjiSync:
    """
    灵畿平台缺陷同步

    功能:
    - 登录校验
    - 创建缺陷
    - 按标题搜索缺陷ID
    - 列出灵畿缺陷
    """

    def __init__(self, workspace: str = None, project: str = None,
                 handler_id: str = None):
        self.workspace = workspace or DEFAULT_CONFIG['workspace']
        self.project = project or DEFAULT_CONFIG['project']
        self.handler_id = handler_id or DEFAULT_CONFIG['handler_id']
        self.lc_path = self._find_lc()

    def _find_lc(self) -> str:
        """查找 lc 命令路径"""
        try:
            result = subprocess.run(["which", "lc"], capture_output=True,
                                    text=True, timeout=5)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return "lc"

    # ── 登录校验 ──

    def check_login(self) -> dict:
        """
        校验灵畿登录状态

        Returns:
            {"ok": bool, "message": str}
        """
        result = self._run_lc(["checkin"])
        if result['returncode'] == 0:
            return {"ok": True, "message": "已登录"}
        else:
            return {"ok": False, "message": "登录已失效，请重新登录"}

    def login(self, token: str) -> dict:
        """
        登录灵畿平台

        Args:
            token: lc login token (从浏览器插件获取)

        Returns:
            {"ok": bool, "message": str}
        """
        # 支持多种 token 格式
        token = token.strip()
        if token.startswith("lc login "):
            token = token[9:].strip()
        if token.startswith("-c "):
            token = token[3:].strip().strip("'\"")

        if token.startswith("MOSS_SESSION="):
            result = self._run_lc(["login", "-c", token])
        else:
            result = self._run_lc(["login", token])

        if result['returncode'] == 0:
            return {"ok": True, "message": "登录成功"}
        else:
            return {"ok": False, "message": result['stderr'] or result['stdout']}

    def is_logged_in(self) -> bool:
        """快速检查是否已登录"""
        r = self.check_login()
        return r['ok']

    # ── 只读模式 ──

    def readonly_off(self, duration: int = 10) -> dict:
        """关闭只读模式"""
        result = self._run_lc(["readonly", "off", "--duration", f"{duration}m"])
        return {
            "ok": result['returncode'] == 0,
            "message": result['stdout'] or result['stderr'],
        }

    # ── 项目操作 ──

    def list_projects(self, workspace: str = None) -> list[dict]:
        """列出研发空间下关联的项目

        Returns:
            [{"code": str, "name": str, ...}]
        """
        ws = workspace or self.workspace
        result = self._run_lc([
            "space", "project", "linked",
            "--workspace-key", ws,
            "--size", "50",
            "--pretty",
        ])
        if result['returncode'] != 0:
            return []
        try:
            data = json.loads(result['stdout'])
            items = data.get('data', {}).get('items', [])
            return [{
                "code": i.get('projectCode', ''),
                "name": i.get('projectName', ''),
                "id": i.get('id', ''),
            } for i in items if i.get('projectCode')]
        except (json.JSONDecodeError, KeyError):
            return []

    # ── 用户操作 ──

    def list_handlers(self, workspace: str = None) -> list[dict]:
        """从已有缺陷中提取处理人列表（ID + 名称）

        Returns:
            [{"id": str, "name": str, "email": str}]
        """
        ws = workspace or self.workspace
        result = self._run_lc([
            "bug", "list", "-w", ws, "-l", "100", "--pretty",
        ])
        if result['returncode'] != 0:
            return []
        try:
            data = json.loads(result['stdout'])
            items = data.get('data', {}).get('items', [])
            seen = {}
            for i in items:
                hid = i.get('handlerId', '')
                hname = i.get('handlerName', '')
                if hid and hname and hid not in seen:
                    # handlerName format: "傅强(fuqiang@cmiot.cmcc)"
                    import re
                    m = re.match(r'(.+?)\((.+?)\)', hname)
                    name = m.group(1) if m else hname
                    email = m.group(2) if m else ''
                    seen[hid] = {"id": hid, "name": name, "email": email}
            return list(seen.values())
        except (json.JSONDecodeError, KeyError):
            return []

    # ── 缺陷操作 ──

    def create_bug(self, title: str, description: str,
                   severity: int = 2, priority: int = 1,
                   bug_type: int = 1,
                   project: str = None, handler_id: str = None) -> dict:
        """
        创建灵畿缺陷

        Args:
            title: 标题（会用于后续搜索，需唯一可追踪）
            description: 描述（含环境/步骤/分析）
            severity: 严重程度 1-4
            priority: 优先级 1-3
            bug_type: 类型 1-5
            project: 项目代码（默认使用 self.project）
            handler_id: 责任人ID（默认使用 self.handler_id）

        Returns:
            {"ok": bool, "bug_id": str or None, "message": str}
        """
        p = project or self.project
        h = handler_id or self.handler_id

        # 1. 关闭只读模式
        self.readonly_off(duration=5)

        # 2. 创建缺陷
        cmd = [
            "bug", "create",
            "-t", title,
            "-D", description,
            "-p", p,
            "-w", self.workspace,
            "--handler-id", h,
            "--template-simple",
            "-l", str(severity),
            "--priority", str(priority),
            "--type", str(bug_type),
        ]
        result = self._run_lc(cmd)

        if result['returncode'] != 0:
            return {
                "ok": False, "bug_id": None,
                "message": result['stderr'] or result['stdout'],
            }

        # 3. ⚠️ bug create 不返回 ID，通过标题搜索
        time.sleep(1.5)  # 等索引
        bug_id = self._search_bug_by_title(title)

        if bug_id:
            return {
                "ok": True, "bug_id": bug_id,
                "message": f"创建成功，灵畿ID: #{bug_id}",
            }
        else:
            return {
                "ok": True, "bug_id": None,
                "message": "创建成功，但未获取到灵畿ID（可通过'灵畿列表'查找）",
            }

    def list_bugs(self, limit: int = 50) -> list[dict]:
        """列出灵畿缺陷（直接解析JSON输出）"""
        result = self._run_lc([
            "bug", "list",
            "-w", self.workspace,
            "-l", str(limit),
        ])
        if result['returncode'] != 0:
            return []

        try:
            data = json.loads(result['stdout'])
            items = data.get('data', {}).get('items', [])
            bugs = []
            for i in items:
                bugs.append({
                    'id': i.get('id', ''),
                    'title': i.get('defectName', ''),
                    'status': i.get('status', ''),
                    'handler': i.get('handlerName', ''),
                    'project': i.get('project', ''),
                    'defectCode': i.get('defectCode', ''),
                })
            return bugs
        except (json.JSONDecodeError, KeyError, TypeError):
            return []

    def get_bug(self, bug_id: str) -> Optional[dict]:
        """获取灵畿缺陷详情"""
        result = self._run_lc([
            "bug", "view", bug_id,
            "-w", self.workspace,
        ])
        if result['returncode'] != 0:
            return None
        return {"raw": result['stdout'], "id": bug_id}

    def delete_bug(self, bug_id: str) -> dict:
        """删除灵畿缺陷"""
        self.readonly_off(duration=5)
        result = self._run_lc([
            "bug", "delete", bug_id,
            "-w", self.workspace, "--yes",
        ])
        return {
            "ok": result['returncode'] == 0,
            "message": result['stdout'] or result['stderr'],
        }

    # ── 内部方法 ──

    def _run_lc(self, args: list) -> dict:
        """执行 lc 命令"""
        cmd = [self.lc_path] + args
        env = os.environ.copy()
        env['NODE_EXTRA_CA_CERTS'] = '/tmp/cmca-combined.crt'
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30, env=env
            )
            return {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        except subprocess.TimeoutExpired:
            return {"returncode": -1, "stdout": "", "stderr": "命令超时"}
        except FileNotFoundError:
            return {"returncode": -1, "stdout": "", "stderr": "lc 命令未找到"}

    def _search_bug_by_title(self, title: str) -> Optional[str]:
        """按标题搜索缺陷ID"""
        bugs = self.list_bugs(limit=100)
        # 反向搜索（用标题关键字匹配）
        keywords = title.replace("【", "").replace("】", " ").split()
        for bug in bugs:
            bug_title = bug.get('title', '')
            # 匹配关键字
            match_count = sum(1 for kw in keywords if kw in bug_title and len(kw) > 2)
            if match_count >= 2:
                return bug.get('id')
            # 完全匹配
            if title[:20] in bug_title or bug_title[:20] in title:
                return bug.get('id')
        return None

    def _parse_bug_list(self, text: str) -> list[dict]:
        """解析 lc bug list --pretty 输出"""
        bugs = []
        lines = text.strip().split('\n')

        current = {}
        for line in lines:
            line = line.strip()
            if not line:
                if current:
                    bugs.append(current)
                    current = {}
                continue

            # 尝试解析 key: value 格式
            if ':' in line:
                key, _, value = line.partition(':')
                key = key.strip().lower()
                value = value.strip()
                if key in ('id', 'objectid', 'key', 'title', 'status',
                           'severity', 'priority', 'project', 'handler'):
                    current[key] = value

        if current:
            bugs.append(current)

        return bugs


if __name__ == "__main__":
    sync = LingjiSync()
    print(f"lc path: {sync.lc_path}")
    print(f"登录状态: {sync.check_login()}")
