#!/usr/bin/env python3
"""AI Native UART Tool - Web UI v2 (用例集 + 即时缺陷)"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gradio as gr
from agents.chat_session import ChatSession
from models.database import init_db, get_db_path
from models.test_plan_manager import (
    list_plans, save_plan, load_plan, delete_plan,
    list_test_sets, save_test_set, load_test_set, delete_test_set,
    list_custom_cmds, save_custom_cmds, add_custom_cmd, delete_custom_cmd,
    merge_plan_to_exec_list, reorder_case,
)
from datetime import datetime
import json

init_db()
session = ChatSession()
serial = session.serial

EXEC_RESULT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "last_exec_result.json")
TEST_SET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "test_sets")
APP_START_TIME = datetime.now().isoformat()  # 本轮启动时间，用作缺陷时间筛选默认值
_DEFECT_CACHE = []  # 缺陷列表缓存，用于行点击映射ID


# ── 持久化工具 ──

_suite_cases = []  # 测试集的 TestCase 列表


def _gen_case_row(c):
    cmd_preview = c.sheet_name
    try:
        real_cmd = session.test_agent.executor._call_command_module(c.sheet_name, c.params)
        if real_cmd:
            cmd_preview = real_cmd[:55]
    except:
        pass
    return [False, c.case_name[:45], c.sheet_name, cmd_preview[:55]]

def _save_exec_result(case_runs, summary, suite_name=""):
    os.makedirs(os.path.dirname(EXEC_RESULT_PATH), exist_ok=True)
    data = {
        "timestamp": datetime.now().isoformat(),
        "suite_name": suite_name,
        "summary": summary,
        "cases": [
            {
                "name": r.case.case_name if hasattr(r, 'case') else '',
                "sheet": r.case.sheet_name if hasattr(r, 'case') else '',
                "at_command": r.at_command,
                "actual": (r.actual or '').strip(),
                "status": r.status,
                "duration_ms": r.duration_ms,
                "fail_reason": r.fail_reason,
            }
            for r in case_runs
        ],
    }
    with open(EXEC_RESULT_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _load_exec_result():
    if not os.path.exists(EXEC_RESULT_PATH):
        return None
    try:
        with open(EXEC_RESULT_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None


def _save_test_set(name, case_indices):
    """保存用例集"""
    os.makedirs(TEST_SET_DIR, exist_ok=True)
    path = os.path.join(TEST_SET_DIR, f"{name}.json")
    with open(path, 'w', encoding='utf-8') as f:
        json.dump({"name": name, "indices": case_indices}, f, ensure_ascii=False)


def _list_test_sets():
    os.makedirs(TEST_SET_DIR, exist_ok=True)
    sets = []
    for f in sorted(os.listdir(TEST_SET_DIR)):
        if f.endswith('.json'):
            name = f[:-5]
            with open(os.path.join(TEST_SET_DIR, f), 'r') as fp:
                data = json.load(fp)
            sets.append((name, data.get("indices", [])))
    return sets


def _load_test_set(name):
    path = os.path.join(TEST_SET_DIR, f"{name}.json")
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return None


# ── UI 函数 ──

def scan_fn():
    ports = serial.list_ports()
    items = []
    for p in ports:
        port_name = p['port'] or ''
        desc = p['description'] or ''
        hwid = p.get('hwid', '') or ''

        # 跨平台 USB 设备标记
        is_hardware = (
            'USB' in desc.upper() or
            'ACM' in port_name or
            'COM' in port_name.upper() or
            'usb' in desc.lower() or
            'usb' in hwid.lower() or
            'VID' in hwid or
            bool(desc and desc != 'n/a')
        )

        label = f"{port_name}  {desc}" if desc and desc != 'n/a' else port_name
        if is_hardware:
            label = f"🔵 {label}"
        items.append(label)
    return gr.Dropdown(choices=items or ["无可用串口"])


def connect_fn(port_str, baud):
    if not port_str or port_str == "无可用串口" or port_str is None:
        return "⚠️ 请先扫描并选择端口"
    # 从下拉标签中提取端口名：格式为 "🔵 COM3  USB Serial Port" 或 "/dev/ttyUSB0  ..."
    port = port_str.replace("🔵", "").replace("🔴", "").strip().split()[0]
    # 跨平台端口名：Windows 是 COM3 格式，Linux/macOS 是 /dev/ttyXXX 格式
    # 不做任何路径改写，pyserial 原生接受所有平台的端口名
    try:
        ok = serial.open(port, int(baud))
        if ok:
            session.test_agent.executor.serial = serial
        return f"✅ 已连接 {port} @ {baud}" if ok else f"❌ 连接失败（串口可能被占用）"
    except Exception as e:
        return f"❌ 连接失败: {str(e)[:60]}"


def disconnect_fn():
    serial.close()
    return "🔒 已断开"


# ── 两表模式：仓库 + 测试集 ──

_source_cases = []   # 仓库模块的 TestCase 列表
_custom_cases = []   # 自定义用例列表
_custom_id_counter = 0


def _all_source():
    """返回仓库所有用例（模块 + 自定义）"""
    return _source_cases + _custom_cases


def gen_plan_fn(module, level, model):
    """加载仓库模块（保留自定义用例）"""
    global _source_cases
    if not module:
        return None, "请选择模块"
    cases = session.loader.load_cases(module, case_level=[level], model=model)
    if not cases:
        return None, f"❌ 模块 {module} 无 {level} 级用例"
    _source_cases = cases
    rows = [_gen_case_row(c)[:4] for c in _all_source()]
    return rows, f"📋 已加载 {module} {level} 级 {len(cases)} 条（含 {len(_custom_cases)} 条自定义）"


def add_custom_to_source_fn(at_cmd, case_name, expected):
    """添加自定义用例到仓库（不是直接到测试集）"""
    global _custom_cases, _custom_id_counter
    if not at_cmd.strip() or not case_name.strip():
        return None, "❌ AT指令和用例名不能为空"
    from models.schemas import TestCase
    _custom_id_counter += 1
    c = TestCase(
        excel_file='', sheet_name=at_cmd.strip().split('=')[0].split('?')[0],
        row_id=_custom_id_counter, test_group='custom', case_name=case_name.strip(),
        params={'send_data': at_cmd.strip()},
        expected_results=[expected.strip()] if expected.strip() else [r"OK"],
    )
    _custom_cases.append(c)
    rows = [_gen_case_row(c)[:4] for c in _all_source()]
    return rows, f"✅ 已添加「{case_name}」到仓库，勾选后点「导入」"


def import_fn(source_table):
    """从仓库导入勾选用例到测试集"""
    global _suite_cases
    all_cases = _all_source()
    if not all_cases or source_table is None:
        return None, "❌ 仓库为空"
    import pandas as pd
    rows = source_table.values.tolist() if isinstance(source_table, pd.DataFrame) else list(source_table)
    added = 0
    for i, row in enumerate(rows):
        if i >= len(all_cases):
            break
        cell0 = row[0]
        if (isinstance(cell0, bool) and cell0) or (isinstance(cell0, str) and cell0.strip() in ("True", "1", "☑")):
            _suite_cases.append(all_cases[i])
            added += 1
    display = [_gen_case_row(c)[:4] for c in _suite_cases]
    return display, f"✅ 已导入 {added} 条，测试集共 {len(_suite_cases)} 条"


def clear_suite_fn():
    global _suite_cases
    _suite_cases = []
    return [], "🗑️ 测试集已清空"


def remove_unchecked_fn(suite_table):
    global _suite_cases
    if not _suite_cases or suite_table is None:
        return None, "❌ 测试集为空"
    import pandas as pd
    rows = suite_table.values.tolist() if isinstance(suite_table, pd.DataFrame) else list(suite_table)
    keep = []
    for i, row in enumerate(rows):
        if i >= len(_suite_cases):
            break
        cell0 = row[0]
        if (isinstance(cell0, bool) and cell0) or (isinstance(cell0, str) and cell0.strip() in ("True", "1", "☑")):
            keep.append(_suite_cases[i])
    _suite_cases = keep
    display = [_gen_case_row(c)[:4] for c in _suite_cases]
    return display, f"✅ 已移除未勾选，测试集共 {len(_suite_cases)} 条"


def remove_checked_fn(suite_table):
    """删除测试集中已勾选的用例"""
    global _suite_cases
    if not _suite_cases or suite_table is None:
        return None, "❌ 测试集为空"
    import pandas as pd
    rows = suite_table.values.tolist() if isinstance(suite_table, pd.DataFrame) else list(suite_table)
    keep = []
    removed = 0
    for i, row in enumerate(rows):
        if i >= len(_suite_cases):
            break
        cell0 = row[0]
        checked = (isinstance(cell0, bool) and cell0) or (isinstance(cell0, str) and cell0.strip() in ("True", "1", "☑"))
        if not checked:
            keep.append(_suite_cases[i])
        else:
            removed += 1
    _suite_cases = keep
    display = [_gen_case_row(c)[:4] for c in _suite_cases]
    return display, f"✅ 已删除 {removed} 条，测试集共 {len(_suite_cases)} 条"


def save_suite_fn(suite_name):
    global _suite_cases
    if not _suite_cases or not suite_name.strip():
        return gr.Dropdown(), "❌ 请填写方案名称且测试集不为空"
    import json
    data = [{
        'sheet': c.sheet_name, 'name': c.case_name,
        'params': dict(c.params) if hasattr(c, 'params') else {},
        'expected': c.expected_results if hasattr(c, 'expected_results') else [],
        'timeout': c.timeout if hasattr(c, 'timeout') else 10,
        'delay': c.delay_after if hasattr(c, 'delay_after') else 0,
    } for c in _suite_cases]
    path = os.path.join(TEST_SET_DIR, f"{suite_name.strip()}_cases.json")
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    choices = [f[:-11] for f in sorted(os.listdir(TEST_SET_DIR)) if f.endswith('_cases.json')]
    return gr.Dropdown(choices=choices, value=suite_name.strip(), label="加载已有方案"), f"✅ 方案「{suite_name}」已保存"


def load_suite_fn(suite_name):
    global _suite_cases
    if not suite_name.strip():
        return None, "❌ 请选择方案"
    path = os.path.join(TEST_SET_DIR, f"{suite_name.strip()}_cases.json")
    if not os.path.exists(path):
        return None, f"❌ 方案文件 {suite_name} 不存在"
    import json
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    from models.schemas import TestCase
    _suite_cases = []
    for d in data:
        c = TestCase(excel_file='', sheet_name=d.get('sheet', ''), row_id=0, test_group='suite',
                     case_name=d.get('name', ''), params=d.get('params', {}),
                     expected_results=d.get('expected', []), timeout=d.get('timeout', 10),
                     delay_after=d.get('delay', 0))
        _suite_cases.append(c)
    display = [_gen_case_row(c)[:4] for c in _suite_cases]
    return display, f"✅ 已加载方案「{suite_name}」（{len(_suite_cases)} 条）"


def list_suites_fn():
    choices = [f[:-11] for f in sorted(os.listdir(TEST_SET_DIR)) if f.endswith('_cases.json')]
    return gr.Dropdown(choices=choices, value=None, label="加载已有方案")


def exec_plan_fn(suite_name):
    """执行测试集"""
    global _suite_cases
    if not _suite_cases:
        yield "❌ 测试集为空"
        return
    selected = [c for c in _suite_cases if getattr(c, 'selected', True)]
    if not selected:
        yield "❌ 没有勾选的用例"
        return
    if not session.serial.is_connected():
        yield "❌ 请先连接串口"
        return

    # ── 读取模组版本信息 ──
    yield "🔍 正在读取模组版本信息..."
    module_info = "未知"
    firmware_ver = "未知"
    try:
        s = session.serial
        s.send("ATI", with_enter=True)
        import time; time.sleep(0.5)
        resp = s.read()
        if resp:
            text = resp.decode(errors='replace')
            lines = text.strip().split('\n')
            module_info = lines[1].strip() if len(lines) > 1 else text.strip()[:60]
            firmware_ver = text.strip()[:80]
    except:
        pass
    session.context['module_info'] = module_info
    session.context['firmware_ver'] = firmware_ver

    total = len(selected)
    sname = suite_name.strip() or "混合测试"
    yield f"🚀 执行测试集: {sname}（{total} 条）\n\n"

    from models.database import create_session as db_create_session, end_session, update_session_stats
    from models.schemas import TestResult
    from datetime import datetime
    session_name = f"{sname}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    db_session_id = db_create_session(name=session_name, module='mixed', port=session.serial.port,
        baudrate=session.serial.baudrate, model='', case_level='P0')
    executor = session.test_agent.executor
    executor.serial = session.serial
    passed, failed = 0, 0; case_runs = []; progress = []

    for i, case in enumerate(selected, 1):
        yield f"🔄 **[{i}/{total}]** {case.case_name} ..."
        run = executor.execute_case(case, db_session_id, port=session.serial.port, baudrate=session.serial.baudrate)
        case_runs.append(run)
        if run.status == 'PASS': passed += 1; icon = "✅"
        elif run.status == 'FAIL': failed += 1; icon = "❌"
        else: icon = "⚠️"
        at_cmd = (run.at_command or case.sheet_name)[:60]
        actual_d = f"\n```\n{(run.actual or '').strip()[:150]}\n```" if run.actual else "\n*(无响应)*"
        progress.append(f"  {icon} **{case.case_name}** ({run.duration_ms}ms)\n    `>>> {at_cmd}`{actual_d}")
        yield f"**进度:** ✅{passed}  ❌{failed}  /  {total}\n---\n" + "\n".join(progress[-12:])

    update_session_stats(db_session_id)
    summary = f"✅ {passed} | ❌ {failed} | 共 {total} 条"
    end_session(db_session_id, summary=summary)
    result = TestResult(session_id=db_session_id, session_name=session_name, module='mixed', case_runs=case_runs)
    session.context['current_result'] = result
    session.context['exec_result'] = result
    _save_exec_result(case_runs, summary, sname)
    defect_hint = "\n\n📌 点「生成缺陷」创建缺陷" if failed > 0 else ""
    yield f"## 📊 {sname}\n\n**{summary}**{defect_hint}"

    # ── 自动生成缺陷 ──
    if failed > 0:
        try:
            from models.schemas import TestCaseRun
            ok = 0
            for f in case_runs:
                if f.status != 'FAIL':
                    continue
                at_cmd = f.at_command or ''
                actual = (f.actual or '').strip()[:200]
                reason = f.fail_reason or '未知'
                desc = (
                    f"## 缺陷报告\n\n"
                    f"### 测试环境\n"
                    f"- **模组型号:** {session.context.get('module_info', 'ML307H')}\n"
                    f"- **固件版本:** {session.context.get('firmware_ver', '未知')}\n"
                    f"- **串口:** {port} @ {baudrate}\n"
                    f"- **测试指令:** `{at_cmd}`\n"
                    f"- **指令耗时:** {f.duration_ms}ms\n\n"
                    f"### 复现步骤\n"
                    f"1. 连接模组串口（{port}）\n"
                    f"2. 发送指令: `{at_cmd}`\n"
                    f"3. 等待响应\n\n"
                    f"### 预期结果\n"
                    f"指令返回 `OK` 或匹配期望响应\n\n"
                    f"### 实际结果\n"
                    f"```\n{actual}\n```\n"
                    f"**失败原因:** {reason}\n\n"
                    f"### 根因分析\n"
                    f"{reason}\n"
                )
                r = session.defect_agent.create_local(f, description=desc)
                if r['ok']:
                    ok += 1
            yield f"\n✅ 已自动为 {ok}/{failed} 条 FAIL 生成缺陷\n💡 切换到 **🐛 缺陷管理** 标签页查看"
        except Exception as e:
            print(f"[AutoDefect] {e}")


def gen_defects_from_result():
    """从上次执行结果生成缺陷"""
    result = session.context.get('current_result')
    if not result:
        data = _load_exec_result()
        if data and data.get('cases'):
            from models.schemas import TestResult, TestCaseRun, TestCase
            runs = []
            for c in data['cases']:
                tc = TestCase(excel_file='', sheet_name=c.get('sheet',''),
                              row_id=0, test_group='', case_name=c.get('name',''))
                tr = TestCaseRun(session_id=0, case=tc,
                    at_command=c.get('at_command',''), actual=c.get('actual',''),
                    status=c.get('status','FAIL'), fail_reason=c.get('fail_reason',''),
                    duration_ms=c.get('duration_ms',0))
                runs.append(tr)
            result = TestResult(session_id=0, session_name='', module='tcp', case_runs=runs)
            session.context['current_result'] = result

    if not result or not result.failures:
        return "✅ 没有失败用例，无需创建缺陷"

    failures = result.failures
    ok = 0
    for i, f in enumerate(failures):
        sheet = f.case.sheet_name
        at_cmd = f.at_command or ''
        actual = (f.actual or '').strip()[:200]
        reason = f.fail_reason or '未知'
        desc = (
            f"## 缺陷报告\n\n"
            f"### 测试环境\n"
            f"- **模组型号:** {session.context.get('module_info', 'ML307H')}\n"
            f"- **固件版本:** {session.context.get('firmware_ver', '未知')}\n"
            f"- **串口:** {session.serial.port} @ {session.serial.baudrate}\n"
            f"- **测试指令:** `{at_cmd}`\n"
            f"- **指令耗时:** {f.duration_ms}ms\n\n"
            f"### 复现步骤\n"
            f"1. 连接模组串口（{session.serial.port}）\n"
            f"2. 发送指令: `{at_cmd}`\n"
            f"3. 等待响应\n\n"
            f"### 预期结果\n"
            f"指令返回 `OK` 或匹配期望响应\n\n"
            f"### 实际结果\n"
            f"```\n{actual}\n```\n"
            f"**失败原因:** {reason}\n\n"
            f"### 根因分析\n"
            f"{reason}\n"
        )
        r = session.defect_agent.create_local(f, description=desc)
        if r['ok']:
            ok += 1

    return f"✅ 已为 {ok}/{len(failures)} 条 FAIL 生成缺陷"


# ── 缺陷管理 ──

def _build_defect_table(since_time=None):
    """生成缺陷列表数据（含勾选框，最多50条）

    Args:
        since_time: ISO时间字符串，只返回该时间之后的缺陷
    """
    global _DEFECT_CACHE
    import re
    # 兼容处理：gr.DateTime返回ISO格式(带T)或datetime对象，SQLite存的是空格格式
    if since_time:
        since_time = str(since_time).replace('T', ' ').split('.')[0][:19]
    defects = session.defect_agent.store.list_defects(limit=50, created_after=since_time)
    _DEFECT_CACHE = defects
    if not defects:
        return []
    data = []
    for d in defects:
        desc = d['description'] or ''
        # 提取型号
        m = re.search(r'\*\*模组型号:\*\*\s*\*{0,2}\s*(\S+)', desc)
        model = m.group(1).strip('* ') if m else ''
        if model.startswith('-') or model.startswith('/'):
            model = ''
        # 提取版本
        m = re.search(r'\*\*固件版本:\*\*\s*\*{0,2}\s*(.+?)(?:\s*-+\s*\*{2}|$)', desc, re.DOTALL)
        version = ''
        if m:
            v = m.group(1).strip().replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')[:30]
            if v and not v.startswith('+'):
                version = v
        # 时间
        date_str = str(d['created_at'])[:16] if d['created_at'] else ''
        # 状态
        if d.get('lingji_id'):
            status = f"📝+灵畿#{d['lingji_id']}"
        elif d['status'] == 'submitted':
            status = "📝 已提交(未同步ID)"
        else:
            status = "📝 本地"
        data.append([False, str(d['id']), f"{d['title'][:40]}", model, version, date_str, status])
    return data


def refresh_defect_list_fn(since_time):
    """刷新缺陷列表（按时间筛选）"""
    global _DEFECT_CACHE
    try:
        table = _build_defect_table(since_time if since_time else None)
        count = len(table)
        hint = f"共 {count} 条，点击行查看详情"
        if since_time:
            # 显示时转回可读格式
            display_time = str(since_time).replace('T', ' ').split('.')[0][:16]
            hint += f"（筛选: {display_time} 之后）"
        else:
            hint += "（全部时间）"
        return table, hint
    except Exception as e:
        print(f"[DefectRefresh] {e}")
        return [], f"❌ 刷新失败: {str(e)[:50]}"


def view_defect_by_row_fn(evt: gr.SelectData):
    """点击行查看缺陷详情"""
    global _DEFECT_CACHE
    if evt.index is None:
        return "### 👆 请点击行"
    row_idx, _ = evt.index if isinstance(evt.index, (list, tuple)) else (evt.index, 0)
    if row_idx < 0 or row_idx >= len(_DEFECT_CACHE):
        return "### ❌ 无效行"
    defect = _DEFECT_CACHE[row_idx]
    return session.defect_agent.format_defect_detail(defect['id'])


def view_defect_by_id_fn(defect_id):
    """按ID查看缺陷详情（保留兼容）"""
    if defect_id is None or defect_id <= 0:
        return "### 👆 请输入有效缺陷ID"
    detail = session.defect_agent.format_defect_detail(int(defect_id))
    _DEFECT_CACHE.clear()
    return detail


def delete_defect_by_id_fn(defect_id):
    """删除指定ID的缺陷（有灵畿ID的禁止删除）"""
    if defect_id is None or defect_id <= 0:
        return _build_defect_table(), "❌ 请输入有效缺陷ID"
    did = int(defect_id)
    d = session.defect_agent.store.get_defect(did)
    if not d:
        return _build_defect_table(), f"❌ 缺陷 #{did} 不存在"
    if d.get('lingji_id'):
        return _build_defect_table(), f"⏭️ 缺陷 #{did} 已提交灵畿（#{d['lingji_id']}），请先在灵畿平台删除"
    session.defect_agent.store.delete_defect(did)
    return _build_defect_table(), f"🗑️ 已删除缺陷 #{did}"


def batch_delete_defect_fn(table_data):
    """批量删除勾选的缺陷（有灵畿ID的自动跳过，保持本地与系统一致）"""
    global _DEFECT_CACHE
    if table_data is None or len(table_data) == 0:
        return _build_defect_table(), "❌ 缺陷列表为空"
    import pandas as pd
    rows = table_data.values.tolist() if isinstance(table_data, pd.DataFrame) else list(table_data)
    deleted = 0
    skipped = 0
    for i, row in enumerate(rows):
        if i >= len(_DEFECT_CACHE):
            break
        cell0 = row[0]
        if (isinstance(cell0, bool) and cell0) or (isinstance(cell0, str) and cell0.strip() in ("True", "1", "☑")):
            did = _DEFECT_CACHE[i]['id']
            # 有灵畿ID的不允许删除，保持本地与系统一致
            if _DEFECT_CACHE[i].get('lingji_id'):
                skipped += 1
                continue
            session.defect_agent.store.delete_defect(did)
            deleted += 1
    _DEFECT_CACHE.clear()
    new_table = _build_defect_table()
    msg = f"🗑️ 已删除 {deleted} 条"
    if skipped:
        msg += f"，⏭️ 跳过 {skipped} 条（已提交灵畿，需在灵畿平台操作）"
    return new_table, msg


# ── 提交到灵畿 ──

_DEFAULT_HANDLER_ID = "1966881909663256588"  # 傅强

def fetch_projects_for_lingji_fn():
    """获取灵畿项目列表和处理人列表"""
    try:
        sync = session.defect_agent.sync
        projects = sync.list_projects()
        handlers = sync.list_handlers()

        # ── 项目下拉 ──
        if not projects:
            proj_dd = gr.Dropdown(choices=[], value=None, interactive=True,
                                  label="📁 目标项目（未获取到）")
            proj_msg = "⚠️ 未获取到项目，请确认已登录灵畿且 workspace 正确"
        else:
            choices = [(f"{p['name']} ({p['code']})", p['code']) for p in projects]
            proj_dd = gr.Dropdown(choices=choices, value=choices[0][1], interactive=True,
                                  label=f"📁 目标项目（共 {len(projects)} 个）")
            proj_msg = f"✅ 已获取 {len(projects)} 个项目"

        # ── 处理人下拉 ──
        if handlers:
            handler_choices = [(f"{h['name']} ({h['email']})", h['id']) for h in handlers]
            # 默认选中傅强
            default_handler = None
            for h in handlers:
                if h['name'] == '傅强':
                    default_handler = h['id']
                    break
            handler_dd = gr.Dropdown(
                choices=handler_choices, value=default_handler or handler_choices[0][1],
                interactive=True, label=f"👤 缺陷责任人（共 {len(handlers)} 人）")
            msg = f"{proj_msg}，{len(handlers)} 位责任人"
        else:
            # 无历史数据时，使用默认handler_id
            handler_dd = gr.Dropdown(
                choices=[("傅强 (默认)", _DEFAULT_HANDLER_ID)],
                value=_DEFAULT_HANDLER_ID,
                interactive=True, label="👤 缺陷责任人（默认）")
            msg = f"{proj_msg}，无历史缺陷数据，使用默认责任人"

        return proj_dd, handler_dd, f"### {msg}，选好项目和责任人后点提交"
    except Exception as e:
        return (gr.Dropdown(choices=[], value=None, interactive=True, label="📁 目标项目"),
                gr.Dropdown(choices=[("傅强 (默认)", _DEFAULT_HANDLER_ID)],
                            value=_DEFAULT_HANDLER_ID, interactive=True, label="👤 缺陷责任人"),
                f"❌ 获取失败: {str(e)[:60]}")


def submit_checked_to_lingji_fn(project_code, handler_id, table_data):
    """提交勾选的缺陷到灵畿平台"""
    global _DEFECT_CACHE

    if not project_code:
        yield "### ❌ 请先选择项目"
        return
    if not handler_id or str(handler_id).strip() == "0":
        yield "### ❌ 请选择缺陷责任人"
        return

    handler = str(handler_id).strip()
    if table_data is None or len(table_data) == 0:
        yield "### ❌ 缺陷列表为空"
        return

    # 解析勾选的缺陷
    import pandas as pd
    rows = table_data.values.tolist() if isinstance(table_data, pd.DataFrame) else list(table_data)
    selected = []
    for i, row in enumerate(rows):
        if i >= len(_DEFECT_CACHE):
            break
        cell0 = row[0]
        if (isinstance(cell0, bool) and cell0) or (isinstance(cell0, str) and cell0.strip() in ("True", "1", "☑")):
            selected.append(_DEFECT_CACHE[i])

    if not selected:
        yield "### ❌ 请在缺陷列表中勾选要提交的缺陷"
        return

    sync = session.defect_agent.sync
    store = session.defect_agent.store

    # 检查登录
    if not sync.is_logged_in():
        yield "### ❌ 灵畿未登录，请先执行 lc login"
        return

    total = len(selected)
    ok_count = 0
    fail_count = 0
    skip_count = 0
    results = []

    yield f"### 🚀 开始提交 {total} 条缺陷到灵畿...\n\n"

    # 统计标题使用次数，用于生成唯一后缀
    title_count = {}
    for d in selected:
        title_count[d['title']] = title_count.get(d['title'], 0) + 1
    title_seq = {}

    # 获取灵畿已有标题，避免重复
    try:
        existing_bugs = sync.list_bugs(limit=200)
        existing_titles = set(b.get('title', '') for b in existing_bugs)
    except:
        existing_titles = set()
    
    for idx, defect in enumerate(selected, 1):
        did = defect['id']
        title = defect['title']
        desc = defect.get('description', '') or '无详细描述'

        # 跳过已有灵畿ID的
        if defect.get('lingji_id'):
            skip_count += 1
            results.append(f"  ⏭️ #{did:04d} 已提交灵畿#{defect['lingji_id']}，跳过")
            continue

        yield f"**[{idx}/{total}]** 提交 #{did:04d}: {title[:40]}...\n"

        try:
            # 同名缺陷加序号后缀（灵畿要求标题唯一）
            seq = title_seq.get(title, 0) + 1
            title_seq[title] = seq
            # 检查是否需要在标题加后缀：本地有同名 或 灵畿已有该标题
            needs_suffix = title_count[title] > 1 or title in existing_titles
            if needs_suffix:
                final_title = f"{title}  #{seq}"
            else:
                final_title = title

            r = sync.create_bug(
                title=final_title,
                description=desc,
                severity=defect.get('severity', 2),
                priority=defect.get('priority', 1),
                project=project_code,
                handler_id=handler,
            )
            if r['ok'] and r['bug_id']:
                bug_id = r['bug_id']
                store.update_status(did, 'submitted', lingji_id=bug_id)
                ok_count += 1
                results.append(f"  ✅ #{did:04d} → 灵畿#{bug_id}")
            elif r['ok']:
                store.update_status(did, 'submitted')
                ok_count += 1
                results.append(f"  ✅ #{did:04d} → 已提交(未获取ID)")
            else:
                fail_count += 1
                err_msg = r['message']
                # 提取简洁错误信息
                import json as _json
                try:
                    err_data = _json.loads(err_msg)
                    err_detail = err_data.get('error', {}).get('message', err_msg[:80])
                except:
                    err_detail = err_msg[:80]
                results.append(f"  ❌ #{did:04d} → {err_detail}")
        except Exception as e:
            fail_count += 1
            results.append(f"  ❌ #{did:04d} → {str(e)[:50]}")

        yield f"### 🚀 进度: ✅{ok_count} ❌{fail_count} / {total}\n\n" + "\n".join(results[-12:])

    # ── 导入知识图谱 ──
    if ok_count > 0:
        yield f"\n### 📊 正在将已提交缺陷导入知识图谱...\n"
        k_store = session.knowledge_agent.store
        triple_count = 0
        for d in selected:
            did = d['id']
            updated = store.get_defect(did)
            if updated and updated.get('lingji_id'):
                # 创建知识三元组: (本地缺陷 → 提交到 → 灵畿缺陷)
                triples = [{
                    "subject": f"本地缺陷#{did:04d}",
                    "predicate": "提交到",
                    "object": f"灵畿缺陷#{updated['lingji_id']}",
                    "context": '{"title": "' + (d['title'][:50] or '') + '", "project": "' + project_code + '"}',
                    "confidence": 1.0,
                    "source": "defect_submit",
                    "session_id": None,
                }, {
                    "subject": f"灵畿缺陷#{updated['lingji_id']}",
                    "predicate": "属于项目",
                    "object": project_code,
                    "context": '{"title": "' + (d['title'][:50] or '') + '"}',
                    "confidence": 1.0,
                    "source": "defect_submit",
                    "session_id": None,
                }]
                triple_count += k_store.save_triples(triples)
        yield f"\n### ✅ 提交完成！\n" \
              f"- ✅ 成功: {ok_count}\n" \
              f"- ⏭️ 跳过(已提交): {skip_count}\n" \
              f"- ❌ 失败: {fail_count}\n" \
              f"- 📊 已导入 {triple_count} 条知识三元组\n" \
              f"\n💡 切换到缺陷列表，刷新后可见已提交状态（📤）和灵畦编号\n" \
              f"💡 可在知识图谱标签页查询「灵畦缺陷」"
    else:
        yield f"\n### ❌ 全部提交失败，请检查灵畦登录状态和项目配置"



# ── 构建 UI ──

with gr.Blocks(title="AI Native UART Tool", fill_height=True, fill_width=True) as ui:
    gr.Markdown(f"### 🔧 AI Native UART Tool")

    # ── 测试方案与执行标签页 ──
    # ── 串口控制（固定在页面顶部）──
    with gr.Row(elem_id="serial-bar"):
        port_dd = gr.Dropdown(label="端口", choices=[], scale=3)
        baud_in = gr.Number(label="波特率", value=115200, precision=0, scale=1)
        status_box = gr.Textbox(label="状态", value="未连接", scale=2)
        gr.Button("🔍 扫描", scale=1).click(scan_fn, None, port_dd)
        gr.Button("✅ 连接", scale=1).click(connect_fn, [port_dd, baud_in], status_box)
        gr.Button("❌ 断开", scale=1).click(disconnect_fn, None, status_box)

    # ── 测试方案与执行标签页 ──
    with gr.Tab("📋 测试方案与执行") as plan_tab:

        # ══════════════════════════════════
        # 子标签：用例集库 | 方案管理
        # ══════════════════════════════════
        with gr.Tabs():
            # ── 用例集库 ──────────────────
            with gr.Tab("📦 用例集库"):
                with gr.Row():
                    with gr.Column(scale=1, min_width=200):
                        gr.Markdown("### 用例集列表")
                        with gr.Row():
                            new_set_btn = gr.Button("➕ 新建", scale=1)
                            copy_set_btn = gr.Button("📋 复制", scale=1)
                            del_set_btn = gr.Button("🗑️ 删除", scale=1)
                        with gr.Row():
                            new_set_name = gr.Textbox(label="新建名称", placeholder="输入名称", scale=1)
                            copy_set_name = gr.Textbox(label="复制为", placeholder="新用例集名称", scale=1)
                        set_radio = gr.Radio(label="选择用例集", choices=[], interactive=True)
                        set_lib_status = gr.Markdown("")

                    with gr.Column(scale=2, min_width=350):
                        gr.Markdown("### 用例列表")
                        with gr.Row():
                            save_set_btn = gr.Button("💾 保存", variant="primary", scale=1)
                            del_set_case_btn = gr.Button("🗑️ 删除此行", scale=1)
                            case_up_btn = gr.Button("⬆ 上移此行", scale=1)
                            case_down_btn = gr.Button("⬇ 下移此行", scale=1)
                        set_case_table = gr.Dataframe(
                            headers=["", "用例名称", "AT指令", "超时(s)", "延迟(ms)"],
                            datatype=["str", "str", "str", "str", "str"],
                            column_count=5, interactive=True, row_count=20,
                            label="点击行选中→按钮操作",
                        )
                        selected_row = gr.State(value=None)
                        set_case_status = gr.Markdown("")

                # ── 用例集库事件 ──
                PAD_ROWS = 20

                def _clean_set_names():
                    return sorted([s.rstrip('_') for s in list_test_sets()])

                def refresh_set_radio():
                    sets = _clean_set_names()
                    return gr.Radio(choices=[(s, s) for s in sets])
                def load_cases_to_table(set_name):
                    if not set_name:
                        return [], "### 请选择用例集", None
                    ts = load_test_set(set_name)
                    cases = ts.get('cases', []) if ts else []
                    rows = []
                    for i, c in enumerate(cases):
                        marker = "●" if i == 0 else "○"
                        rows.append([f"{marker} #{i+1}",
                                     c.get('case_name', '')[:40],
                                     (c.get('at_cmd', '') or c.get('module', ''))[:45],
                                     str(c.get('timeout', 10)),
                                     str(c.get('delay', '') if c.get('delay') is not None else '')])
                    while len(rows) < PAD_ROWS:
                        rows.append(["", "", "", "", ""])
                    return rows, f"### 用例集「{set_name}」共 {len(cases)} 条 · 点击行选中", None

                set_radio.change(load_cases_to_table, [set_radio], [set_case_table, set_case_status, selected_row])

                def on_row_select(evt: gr.SelectData):
                    if evt.index is None:
                        return None
                    if isinstance(evt.index, (list, tuple)):
                        return evt.index[0]
                    return evt.index

                set_case_table.select(on_row_select, None, [selected_row])

                def create_set(name):
                    if not name or not name.strip():
                        return refresh_set_radio(), "", "### ❌ 请输入名称"
                    name = name.strip()
                    if name not in _clean_set_names():
                        save_test_set(name, [])
                        return refresh_set_radio(), "", f"### ✅ 已创建「{name}」"
                    return refresh_set_radio(), "", f"### ⏭️ 「{name}」已存在"

                new_set_btn.click(create_set, [new_set_name], [set_radio, new_set_name, set_lib_status])

                def delete_set(set_name):
                    if not set_name:
                        return refresh_set_radio(), [], "### ❌ 请先选择用例集", None
                    delete_test_set(set_name)
                    return refresh_set_radio(), [], f"### ✅ 已删除「{set_name}」", None

                del_set_btn.click(delete_set, [set_radio], [set_radio, set_case_table, set_lib_status, selected_row])

                def copy_set(old_name, new_name):
                    if not old_name:
                        return refresh_set_radio(), "", "### ❌ 请先选择用例集"
                    if not new_name or not new_name.strip():
                        return refresh_set_radio(), "", "### ❌ 请输入新名称"
                    new_name = new_name.strip()
                    if new_name in _clean_set_names():
                        return refresh_set_radio(), "", f"### ⏭️ 「{new_name}」已存在"
                    ts = load_test_set(old_name)
                    save_test_set(new_name, ts.get('cases', []) if ts else [])
                    return refresh_set_radio(), "", f"### ✅ 已复制「{old_name}」→「{new_name}」"

                copy_set_btn.click(copy_set, [set_radio, copy_set_name],
                                   [set_radio, copy_set_name, set_lib_status])

                def save_cases_from_table(set_name, table_data):
                    if not set_name:
                        return table_data, "### ❌ 请先选择用例集", None
                    import pandas as pd
                    if isinstance(table_data, pd.DataFrame):
                        rows = table_data.values.tolist()
                    elif table_data and hasattr(table_data, '__iter__'):
                        rows = [list(r) for r in table_data]
                    else:
                        rows = []
                    cases = []
                    for r in rows:
                        # 跳过空行和标记列
                        name = str(r[1]).strip() if len(r) > 1 else ""
                        cmd = str(r[2]).strip() if len(r) > 2 else ""
                        if not name or not cmd:
                            continue
                        # 去掉名称中可能的标记前缀
                        to = int(r[3]) if len(r) > 3 and str(r[3]).strip() else 10
                        dl = int(r[4]) if len(r) > 4 and str(r[4]).strip() else None
                        cases.append({
                            "source": "custom", "at_cmd": cmd, "case_name": name[:40],
                            "module": cmd, "expected": "OK", "timeout": to,
                            "delay": dl if dl else None,
                        })
                    save_test_set(set_name, cases)
                    new_rows, msg, _ = load_cases_to_table(set_name)
                    return new_rows, f"### ✅ 已保存 {len(cases)} 条", None

                save_set_btn.click(save_cases_from_table, [set_radio, set_case_table],
                                   [set_case_table, set_case_status, selected_row])

                def del_selected_case(set_name, sel_row):
                    if not set_name:
                        return [], "", None
                    if sel_row is None:
                        return load_cases_to_table(set_name)
                    ts = load_test_set(set_name)
                    cases = ts.get('cases', []) if ts else []
                    if sel_row >= len(cases):
                        return load_cases_to_table(set_name)
                    removed = cases.pop(sel_row)
                    save_test_set(set_name, cases)
                    new_rows, msg, _ = load_cases_to_table(set_name)
                    return new_rows, f"### ✅ 已删除「{removed.get('case_name','')}」", None

                del_set_case_btn.click(del_selected_case, [set_radio, selected_row],
                                       [set_case_table, set_case_status, selected_row])

                def move_selected_case(set_name, sel_row, direction):
                    if not set_name or sel_row is None:
                        return [], "", None
                    ts = load_test_set(set_name)
                    cases = ts.get('cases', []) if ts else []
                    if sel_row >= len(cases):
                        return load_cases_to_table(set_name)
                    if direction == 'up' and sel_row > 0:
                        cases[sel_row], cases[sel_row-1] = cases[sel_row-1], cases[sel_row]
                    elif direction == 'down' and sel_row < len(cases) - 1:
                        cases[sel_row], cases[sel_row+1] = cases[sel_row+1], cases[sel_row]
                    else:
                        return load_cases_to_table(set_name)
                    save_test_set(set_name, cases)
                    new_rows, msg, _ = load_cases_to_table(set_name)
                    return new_rows, f"### ✅ 已移动", sel_row + (1 if direction == 'down' else -1 if direction == 'up' else 0)

                case_up_btn.click(lambda s, r: move_selected_case(s, r, 'up'),
                                  [set_radio, selected_row], [set_case_table, set_case_status, selected_row])
                case_down_btn.click(lambda s, r: move_selected_case(s, r, 'down'),
                                    [set_radio, selected_row], [set_case_table, set_case_status, selected_row])

                # 初始加载
                _init_sets = sorted(s.rstrip('_') for s in list_test_sets())
                set_radio.choices = [(s, s) for s in _init_sets]
                # 初始加载
                _init_sets = sorted(s.rstrip('_') for s in list_test_sets())
                set_radio.choices = [(s, s) for s in _init_sets]

            # ── 方案管理 ──────────────────
            with gr.Tab("📋 方案管理"):
                with gr.Row():
                    # 左：方案管理
                    with gr.Column(scale=1, min_width=200):
                        with gr.Row():
                            new_plan_btn = gr.Button("➕ 新建", scale=1)
                            del_plan_btn = gr.Button("🗑️ 删除", scale=1)
                            refresh_plan_btn = gr.Button("🔄 刷新", scale=1)
                            exec_plan_btn = gr.Button("🚀 执行", variant="primary", scale=1)
                        new_plan_name = gr.Textbox(label="新方案名称", placeholder="输入名称")
                        plan_radio = gr.Radio(label="选择方案", choices=[], interactive=True)
                        plan_status = gr.Markdown("")
                        with gr.Row():
                            loop_count = gr.Number(label="执行轮次", value=1, precision=0, minimum=1, scale=1)
                            loop_delay = gr.Number(label="轮次间隔(s)", value=0, precision=0, minimum=0, scale=1)
                        gr.Markdown("---")
                        gr.Markdown("### 可选用例集（勾选即保存）")
                        set_checkboxes = gr.CheckboxGroup(label="勾选即加入方案", choices=[], interactive=True)
                        plan_set_status = gr.Markdown("")

                    # 中：用例表格 + 执行
                    with gr.Column(scale=2, min_width=350):
                        gr.Markdown("### 方案用例")
                        plan_case_table = gr.Dataframe(
                            headers=["☑", "用例集", "用例名称", "AT指令", "超时", "延迟"],
                            datatype=["bool", "str", "str", "str", "str", "str"],
                            column_count=6, interactive=True, row_count=15,
                            label="勾选→执行",
                        )
                        plan_exec_status = gr.Markdown("")

                    # 右：执行日志
                    with gr.Column(scale=2, min_width=300):
                        gr.Markdown("### 执行日志")
                        plan_exec_log = gr.Textbox(lines=18, max_lines=30, interactive=False, placeholder="执行后将实时显示AT指令收发...", show_label=False)

                # ── 方案管理事件 ──
                def refresh_plan_radio():
                    plans = sorted(list_plans())
                    return gr.Radio(choices=[(p, p) for p in plans])

                def load_plan_cases(plan_name):
                    """加载方案用例到表格"""
                    if not plan_name:
                        return [], ""
                    plan = load_plan(plan_name)
                    if not plan:
                        return [], f"### ❌ 方案「{plan_name}」不存在"
                    set_names = plan.get('test_set_names', [])
                    rows = []
                    for sn in set_names:
                        ts = load_test_set(sn)
                        if not ts:
                            continue
                        for c in ts.get('cases', []):
                            rows.append([False, sn,
                                         c.get('case_name', '')[:35],
                                         (c.get('at_cmd', '') or c.get('module', ''))[:40],
                                         str(c.get('timeout', 10)),
                                         str(c.get('delay', '') if c.get('delay') is not None else '')])
                    while len(rows) < 20:
                        rows.append([False, "", "", "", "", ""])
                    return rows, f"### 方案「{plan_name}」共 {len([r for r in rows if r[1]])} 条（{len(set_names)} 个用例集）"

                def on_plan_select(plan_name):
                    if not plan_name:
                        return refresh_plan_radio(), "", gr.CheckboxGroup(choices=[]), [], "", 1, 0
                    plan = load_plan(plan_name)
                    all_sets = sorted(s.rstrip('_') for s in list_test_sets())
                    selected_sets = plan.get('test_set_names', [])
                    case_rows, msg = load_plan_cases(plan_name)
                    lc = plan.get('loop_count', 1) if plan else 1
                    ld = plan.get('global_delay', 0) if plan else 0
                    return (refresh_plan_radio(),
                            f"### ✅ 方案「{plan_name}」",
                            gr.CheckboxGroup(choices=[(s, s) for s in all_sets], value=selected_sets),
                            case_rows, msg, lc, ld)

                plan_radio.change(on_plan_select, [plan_radio],
                                  [plan_radio, plan_status, set_checkboxes, plan_case_table, plan_exec_status, loop_count, loop_delay])

                refresh_plan_btn.click(on_plan_select, [plan_radio],
                                       [plan_radio, plan_status, set_checkboxes, plan_case_table, plan_exec_status, loop_count, loop_delay])

                def create_plan(name):
                    if not name or not name.strip():
                        return refresh_plan_radio(), "", "### ❌ 请输入名称"
                    name = name.strip()
                    if name not in list_plans():
                        save_plan(name, [], loop_count=1, global_delay=None)
                        return refresh_plan_radio(), "", f"### ✅ 已创建「{name}」"
                    return refresh_plan_radio(), "", f"### ⏭️ 「{name}」已存在"

                new_plan_btn.click(create_plan, [new_plan_name], [plan_radio, new_plan_name, plan_status])

                def do_delete_plan(plan_name):
                    if not plan_name:
                        return refresh_plan_radio(), gr.CheckboxGroup(choices=[]), [], "", "### ❌ 请选择方案", 1, 0
                    delete_plan(plan_name)
                    return refresh_plan_radio(), gr.CheckboxGroup(choices=[]), [], "", f"### ✅ 已删除「{plan_name}」", 1, 0

                del_plan_btn.click(do_delete_plan, [plan_radio],
                                   [plan_radio, set_checkboxes, plan_case_table, plan_status, plan_exec_status, loop_count, loop_delay])

                def on_set_check(plan_name, checked_sets):
                    if not plan_name:
                        return [], "", "### ❌ 请先选择方案"
                    plan = load_plan(plan_name)
                    checked = list(checked_sets) if checked_sets else []
                    save_plan(plan_name, checked, loop_count=plan.get('loop_count', 1) if plan else 1,
                              global_delay=plan.get('global_delay') if plan else None)
                    case_rows, msg = load_plan_cases(plan_name)
                    return case_rows, msg, f"### ✅ {len(checked)} 个用例集"

                set_checkboxes.change(on_set_check, [plan_radio, set_checkboxes],
                                      [plan_case_table, plan_exec_status, plan_set_status])

                def auto_save_loop(plan_name, lc, ld):
                    if not plan_name: return ""
                    plan = load_plan(plan_name)
                    if not plan: return ""
                    save_plan(plan_name, plan.get('test_set_names', []), loop_count=int(lc) if lc else 1,
                              global_delay=int(ld) if ld is not None else 0)
                    return f"### ✅ 轮次={int(lc or 1)}, 间隔={int(ld or 0)}s"

                loop_count.change(auto_save_loop, [plan_radio, loop_count, loop_delay], [plan_status])
                loop_delay.change(auto_save_loop, [plan_radio, loop_count, loop_delay], [plan_status])

                def exec_plan(plan_name, table_data, lc, ld):
                    """执行方案：支持多轮循环"""
                    if not plan_name:
                        yield ("### ❌ 请先选择方案", ""); return
                    if not serial.is_connected():
                        yield ("### ❌ 请先连接串口", "⚠️ 未连接串口，请先在顶部连接"); return
                    raw_cases, err = merge_plan_to_exec_list(plan_name)
                    if err:
                        yield (f"### ❌ {err}", f"错误: {err}"); return
                    if not raw_cases:
                        yield ("### ❌ 方案无用例", "方案中没有用例，请先在左侧勾选用例集"); return

                    from models.schemas import TestCase as TC
                    import pandas as pd, time
                    if isinstance(table_data, pd.DataFrame):
                        rows = table_data.values.tolist()
                    elif table_data and hasattr(table_data, '__iter__'):
                        rows = [list(r) for r in table_data]
                    else:
                        rows = []

                    all_cases, checked_indices = [], set()
                    idx = 0
                    for r in rows:
                        if str(r[1]).strip():
                            tc = TC(excel_file='', sheet_name=str(r[3])[:45] if len(r) > 3 else '',
                                    row_id=0, test_group=str(r[1]), case_name=str(r[2]) if len(r) > 2 else '',
                                    params={'send_data': str(r[3]) if len(r) > 3 else ''},
                                    expected_results=['OK'], timeout=int(r[4]) if len(r) > 4 and str(r[4]).strip() else 10,
                                    delay_after=int(r[5]) if len(r) > 5 and str(r[5]).strip() else 0)
                            all_cases.append((str(r[1]), tc))
                            if r[0]: checked_indices.add(idx)
                            idx += 1

                    cases = [(sn, tc) for i, (sn, tc) in enumerate(all_cases) if i in checked_indices] if checked_indices else all_cases
                    if not cases: yield ("### ❌ 未选中任何用例", "请在用例表格中勾选要执行的用例"); return

                    loops = int(lc) if lc else 1
                    loop_delay_s = int(ld) if ld else 0

                    log_lines = [f"═══ 执行方案: {plan_name} ═══", f"串口: {serial.port} @ {serial.baudrate}",
                                 f"用例: {len(cases)}/{len(all_cases)} | 轮次: {loops} | 间隔: {loop_delay_s}s\n"]
                    yield (f"### 🚀 {plan_name} {len(cases)}条 × {loops}轮\n", "\n".join(log_lines))

                    executor = session.test_agent.executor
                    executor.serial = serial
                    from models.database import create_session as db_create_session, end_session, update_session_stats
                    from datetime import datetime
                    sname = f"{plan_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    db_sid = db_create_session(name=sname, module='plan', port=serial.port,
                        baudrate=serial.baudrate, model='', case_level='P0')
                    total_pass, total_fail = 0, 0
                    all_results = []
                    for loop in range(loops):
                        if loops > 1:
                            log_lines.append(f"\n── 第 {loop+1}/{loops} 轮 ──")
                            yield (f"### 🔄 第 {loop+1}/{loops} 轮\n", "\n".join(log_lines))
                        passed, failed = 0, 0
                        for i, (sn, case) in enumerate(cases, 1):
                            at_cmd = case.params.get('send_data', '') if hasattr(case, 'params') else ''
                            log_lines.append(f"[L{loop+1} #{i}] [{sn}] {case.case_name}")
                            log_lines.append(f">>> {at_cmd}")
                            yield (f"🔄 L{loop+1} [{i}/{len(cases)}] [{sn}] {case.case_name} ...", "\n".join(log_lines))
                            run = executor.execute_case(case, db_sid, port=serial.port, baudrate=serial.baudrate)
                            all_results.append(run)
                            actual = (run.actual or '').strip()[:150]
                            log_lines.append(f"<<< {actual}")
                            if run.status == 'PASS':
                                passed += 1; total_pass += 1
                                log_lines.append(f"✅ PASS ({run.duration_ms}ms)")
                            elif run.status == 'FAIL':
                                failed += 1; total_fail += 1
                                log_lines.append(f"❌ FAIL ({run.duration_ms}ms) - {run.fail_reason or '未知'}")
                            yield (f"  {'✅' if run.status=='PASS' else '❌'} {case.case_name} ({run.duration_ms}ms)", "\n".join(log_lines))
                        log_lines.append(f"第 {loop+1} 轮: ✅{passed} ❌{failed}")
                        if loop < loops - 1 and loop_delay_s > 0:
                            log_lines.append(f"等待 {loop_delay_s}s ...")
                            yield (f"### ⏳ 等待 {loop_delay_s}s ...\n", "\n".join(log_lines))
                            time.sleep(loop_delay_s)

                    update_session_stats(db_sid)
                    summary = f"✅ {total_pass} | ❌ {total_fail} | {len(cases)}条 × {loops}轮"
                    end_session(db_sid, summary=summary)
                    _save_exec_result(all_results, summary, plan_name)
                    log_lines.append(f"\n═══ 完成: {summary} ═══")
                    yield (f"\n### 📊 {summary}", "\n".join(log_lines))
                    if total_fail > 0:
                        yield (f"\n💡 切换到「🐛 缺陷管理」", "\n".join(log_lines))
                        try:
                            ok = 0
                            for r in all_results:
                                if r.status != 'FAIL': continue
                                desc = (f"## 缺陷报告\n\n### 测试环境\n- **方案:** {plan_name}\n"
                                    f"- **串口:** {serial.port} @ {serial.baudrate}\n"
                                    f"- **测试指令:** `{r.at_command or ''}`\n- **指令耗时:** {r.duration_ms}ms\n\n"
                                    f"### 实际结果\n```\n{(r.actual or '').strip()[:200]}\n```\n"
                                    f"**失败原因:** {r.fail_reason or '未知'}\n")
                                res = session.defect_agent.create_local(r, description=desc)
                                if res['ok']: ok += 1
                            if ok > 0:
                                log_lines.append(f"已自动生成 {ok} 条本地缺陷")
                                yield (f"✅ {ok} 条本地缺陷", "\n".join(log_lines))
                        except Exception as e:
                            yield (f"⚠️ 缺陷生成失败: {e}", "\n".join(log_lines))

                exec_plan_btn.click(exec_plan, [plan_radio, plan_case_table, loop_count, loop_delay], [plan_exec_status, plan_exec_log])

                # 初始加载
                _init_plans = sorted(list_plans())
                plan_radio.choices = [(p, p) for p in _init_plans]
                _init_all_sets = sorted(s.rstrip('_') for s in list_test_sets())
                set_checkboxes.choices = [(s, s) for s in _init_all_sets]

                # 初始加载
                _init_plans = sorted(list_plans())
                plan_radio.choices = [(p, p) for p in _init_plans]
                _init_all_sets = sorted(s.rstrip('_') for s in list_test_sets())
                set_checkboxes.choices = [(s, s) for s in _init_all_sets]

    # ── 缺陷管理标签页 ──
    with gr.Tab("🐛 缺陷管理") as defect_tab:
        # 筛选行（Textbox 替代 DateTime，回车触发）
        with gr.Row():
            date_start = gr.Textbox(label="起始日期", placeholder="2026-05-30", value="", scale=1)
            date_end = gr.Textbox(label="截止日期", placeholder="2026-06-01", value="", scale=1)
            model_filter = gr.Dropdown(label="🔧 型号", choices=[], multiselect=True, scale=1)
            ver_filter = gr.Dropdown(label="📀 版本", choices=[], multiselect=True, scale=1)
            clear_filters_btn = gr.Button("🗑️ 清空", scale=1)


        # ── 缺陷列表 + 详情 ──
        with gr.Row():
            with gr.Column(scale=1, min_width=350):
                with gr.Row():
                    batch_delete_btn = gr.Button("🗑️ 批量删除勾选", scale=1)
                    defect_status = gr.Markdown(f"共 {len(_DEFECT_CACHE)} 条")
                defect_table = gr.Dataframe(
                    value=_build_defect_table(),
                    headers=["☑", "ID", "标题", "型号", "版本号", "测试时间", "状态"],
                    datatype=["bool", "str", "str", "str", "str", "str", "str"],
                    column_count=7, interactive=True, row_count=20,
                    label="勾选操作 | 点击行查看详情",
                )
                # 提交灵畿
                with gr.Row():
                    lingji_project_dd = gr.Dropdown(label="📁 项目", choices=[], interactive=True, scale=2)
                    lingji_handler_dd = gr.Dropdown(label="👤 责任人", choices=[], interactive=True, scale=2)
                    fetch_projects_btn = gr.Button("🔄 获取", scale=1)
                    lingji_confirm_btn = gr.Button("⬆️ 提交勾选", variant="primary", scale=1)
                lingji_progress = gr.Markdown("")

            with gr.Column(scale=1, min_width=300):
                defect_detail = gr.Markdown("### 点击缺陷行查看详情")

        # ── 辅助函数 ──
        def filter_defect_table(models, versions, titles, ds, de):
            """多维筛选缺陷表格"""
            date_start = ds.strip() if ds and ds.strip() else None
            date_end = de.strip() if de and de.strip() else None

            if not any([models, versions, titles, date_start, date_end]):
                # 无筛选条件，显示全部
                table = _build_defect_table()
                return table, f"### 💡 共 {len(table)} 条缺陷 | 选择筛选项缩小范围"

            result = session.knowledge_agent.querier.faceted_query(
                models=models if models else None,
                versions=versions if versions else None,
                defect_titles=titles if titles else None,
                date_start=date_start, date_end=date_end,
            )

            summary = result.get('summary', {})
            enriched = result.get('enriched', [])

            if not summary or summary.get('total', 0) == 0:
                return [], "### 📭 无匹配结果"

            # 构建带勾选框和数据缓存的表格
            defect_rows = []
            for d in enriched:
                status = f"📝+灵畿#{d['lingji_id']}" if d.get('lingji_id') else "📝 本地"
                defect_rows.append([False, f"#{d['id']}", d['title'][:60],
                                    d['model'], d['version'][:30], d['created_at'], status])

            # 更新 _DEFECT_CACHE 为筛选后的数据（便于点击查看详情）
            from models.database import get_connection
            conn = get_connection()
            ids = [int(d['id']) for d in enriched]
            if ids:
                placeholders = ",".join("?" for _ in ids)
                cached = conn.execute(
                    f'SELECT * FROM local_defects WHERE id IN ({placeholders}) ORDER BY created_at DESC',
                    ids
                ).fetchall()
                _DEFECT_CACHE.clear()
                _DEFECT_CACHE.extend([dict(r) for r in cached])
            conn.close()

            # 概要文本
            lines = [f"### ✅ 匹配 {summary['total']} 条缺陷"]
            if not models and summary.get('models'):
                lines.append(f"🔧 型号: {'、'.join(summary['models'])}")
            if not versions and summary.get('versions'):
                lines.append(f"📀 版本: {'、'.join(summary['versions'])}")
            if not titles and summary.get('defect_titles'):
                lines.append(f"🎯 标题: {len(summary['defect_titles'])} 种")
            if summary.get('months'):
                lines.append(f"📅 月份: {'、'.join(summary['months'][:4])}")

            return defect_rows, " | ".join(lines)

        # ── 事件绑定 ──
        def refresh_with_filters(ds, de, models, versions):
            return filter_defect_table(models, versions, None, ds, de)

        # 日期输入框回车触发 + 下拉自动刷新
        date_start.submit(refresh_with_filters, [date_start, date_end, model_filter, ver_filter],
                          [defect_table, defect_status])
        date_end.submit(refresh_with_filters, [date_start, date_end, model_filter, ver_filter],
                        [defect_table, defect_status])
        model_filter.change(refresh_with_filters, [date_start, date_end, model_filter, ver_filter],
                            [defect_table, defect_status])
        ver_filter.change(refresh_with_filters, [date_start, date_end, model_filter, ver_filter],
                          [defect_table, defect_status])
        clear_filters_btn.click(
            lambda: ("", "", None, None, _build_defect_table(), f"共 {len(_DEFECT_CACHE)} 条"),
            None, [date_start, date_end, model_filter, ver_filter, defect_table, defect_status])

        # 表格点击查看详情
        defect_table.select(view_defect_by_row_fn, None, defect_detail)
        # 批量删除
        batch_delete_btn.click(batch_delete_defect_fn, [defect_table],
                               [defect_table, defect_status])
        # 提交灵畿
        fetch_projects_btn.click(fetch_projects_for_lingji_fn, None,
                                 [lingji_project_dd, lingji_handler_dd, lingji_progress])
        lingji_confirm_btn.click(submit_checked_to_lingji_fn,
                                 [lingji_project_dd, lingji_handler_dd, defect_table],
                                 lingji_progress)


if __name__ == "__main__":
    import socket
    try:
        host = socket.gethostbyname(socket.gethostname())
    except socket.gaierror:
        host = "127.0.0.1"
    print(f"\n🌐 http://localhost:7860  (本机: http://{host}:7860)\n")
    ui.launch(server_name="0.0.0.0", server_port=7860, head="""<style>
#serial-bar { position: sticky; top: 0; z-index: 100; background: var(--background-fill-primary, #fff); padding: 6px 0; border-bottom: 1px solid var(--border-color-primary, #ddd); margin-bottom: 4px; }
html { scroll-behavior: smooth; overscroll-behavior: auto; }
body { overflow-y: auto !important; }
.gradio-container { overflow: visible; max-width: 100% !important; }
.gradio-container .contain { max-width: 100% !important; padding: 0 8px !important; }
.app, .main, .wrap, .tabitem, .tabs > div { max-width: 100% !important; }
/* Dataframe 不拦截滚轮 */
[data-testid="dataframe"] { overscroll-behavior: contain; }
table { overscroll-behavior: auto; }
</style>""")
