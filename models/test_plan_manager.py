#!/usr/bin/env python3
"""测试方案管理器 - 方案/测试集/自定义指令 的三层管理体系"""
import json, os, re, shutil
from datetime import datetime
from typing import Optional

BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
PLAN_DIR = os.path.join(BASE_DIR, "test_plans")
SET_DIR = os.path.join(BASE_DIR, "test_sets")
CUSTOM_DIR = os.path.join(BASE_DIR, "custom_cmds")


# ── 工具函数 ──

def _ensure_dirs():
    for d in [PLAN_DIR, SET_DIR, CUSTOM_DIR]:
        os.makedirs(d, exist_ok=True)


def _slug(name: str) -> str:
    """中文名称转文件名，去除尾部下划线"""
    s = re.sub(r'[^\w\u4e00-\u9fff\- ]', '', name).strip()
    s = s.rstrip('_')
    return s or "unnamed"


def _plan_path(name: str) -> str:
    return os.path.join(PLAN_DIR, f"{_slug(name)}_plan.json")


def _set_path(name: str) -> str:
    return os.path.join(SET_DIR, f"{_slug(name)}_set.json")


# ── 方案操作 ──

def list_plans() -> list[str]:
    _ensure_dirs()
    return sorted([f[:-10] for f in os.listdir(PLAN_DIR) if f.endswith('_plan.json')])


def save_plan(name: str, test_set_names: list[str],
              loop_count: int = 1, global_delay: int = None) -> str:
    """保存方案"""
    _ensure_dirs()
    data = {
        "name": name,
        "created": datetime.now().isoformat()[:19],
        "loop_count": loop_count,
        "global_delay": global_delay,
        "test_set_names": test_set_names,
    }
    path = _plan_path(name)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path


def load_plan(name: str) -> Optional[dict]:
    """加载方案"""
    path = _plan_path(name)
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def delete_plan(name: str):
    path = _plan_path(name)
    if os.path.exists(path):
        os.remove(path)


# ── 测试集操作 ──

def list_test_sets() -> list[str]:
    """列出所有历史测试集"""
    _ensure_dirs()
    return sorted([f[:-9] for f in os.listdir(SET_DIR) if f.endswith('_set.json')])


def save_test_set(name: str, cases: list[dict]) -> str:
    """保存测试集

    cases: [{"source":"library"/"custom", "module":"", "case_name":"",
             "at_cmd":"", "expected":"", "timeout":10, "delay":null}, ...]
    """
    _ensure_dirs()
    data = {
        "name": name,
        "created": datetime.now().isoformat()[:19],
        "case_count": len(cases),
        "cases": cases,
    }
    path = _set_path(name)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path


def load_test_set(name: str) -> Optional[dict]:
    """加载测试集"""
    path = _set_path(name)
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def delete_test_set(name: str):
    path = _set_path(name)
    if os.path.exists(path):
        os.remove(path)


# ── 自定义指令操作 ──

def list_custom_cmds() -> list[dict]:
    """列出所有保存的自定义指令"""
    _ensure_dirs()
    path = os.path.join(CUSTOM_DIR, "custom_cmds.json")
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_custom_cmds(cmds: list[dict]):
    """保存自定义指令列表"""
    _ensure_dirs()
    path = os.path.join(CUSTOM_DIR, "custom_cmds.json")
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(cmds, f, ensure_ascii=False, indent=2)


def add_custom_cmd(at_cmd: str, case_name: str, expected: str = "OK",
                   timeout: int = 10, delay: int = None) -> list[dict]:
    """添加一条自定义指令，返回新列表"""
    cmds = list_custom_cmds()
    found = False
    for c in cmds:
        if c['at_cmd'] == at_cmd and c['case_name'] == case_name:
            c['expected'] = expected
            c['timeout'] = timeout
            c['delay'] = delay
            found = True
            break
    if not found:
        cmds.append({
            "source": "custom",
            "at_cmd": at_cmd,
            "case_name": case_name,
            "expected": expected,
            "timeout": timeout,
            "delay": delay,
        })
    save_custom_cmds(cmds)
    return cmds


def delete_custom_cmd(idx: int) -> list[dict]:
    """删除一条自定义指令"""
    cmds = list_custom_cmds()
    if 0 <= idx < len(cmds):
        cmds.pop(idx)
        save_custom_cmds(cmds)
    return cmds


# ── 方案合并为执行列表 ──

def merge_plan_to_exec_list(plan_name: str) -> tuple[Optional[list[dict]], str]:
    """将方案中的所有测试集合并为最终执行列表

    Returns:
        (cases_list, error_msg)
        cases_list: [{"index":1, "set_name":"", "source":"", "case_name":"",
                       "at_cmd":"", "expected":"", "timeout":10, "delay":null,
                       "selected":True}, ...]
    """
    plan = load_plan(plan_name)
    if not plan:
        return None, f"方案「{plan_name}」不存在"

    all_cases = []
    for set_name in plan.get('test_set_names', []):
        ts = load_test_set(set_name)
        if not ts:
            return None, f"测试集「{set_name}」不存在（方案已损坏）"
        for c in ts.get('cases', []):
            entry = {
                "set_name": set_name,
                "source": c.get('source', 'library'),
                "module": c.get('module', ''),
                "case_name": c.get('case_name', ''),
                "at_cmd": c.get('at_cmd', ''),
                "expected": c.get('expected', 'OK'),
                "timeout": c.get('timeout', c.get('timeout', 10)),
                "delay": c.get('delay', plan.get('global_delay')),
                "selected": True,
            }
            all_cases.append(entry)

    if not all_cases:
        return None, f"方案「{plan_name}」中没有用例"

    # 标序号
    for i, c in enumerate(all_cases, 1):
        c['index'] = i

    return all_cases, ""


def reorder_case(cases: list[dict], idx: int, direction: str) -> list[dict]:
    """上移/下移一条用例"""
    if not cases:
        return cases
    if direction == 'up' and idx > 0:
        cases[idx], cases[idx-1] = cases[idx-1], cases[idx]
    elif direction == 'down' and idx < len(cases) - 1:
        cases[idx], cases[idx+1] = cases[idx+1], cases[idx]
    # 重编号
    for i, c in enumerate(cases, 1):
        c['index'] = i
    return cases
