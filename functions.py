def gen_plan_fn(module, level, model):
    """加载仓库模块用例到 source_table"""
    if not module:
        return None, "请选择模块"
    cases = session.loader.load_cases(module, case_level=[level], model=model)
    if not cases:
        return None, f"❌ 模块 {module} 无 {level} 级用例"
    global _source_cases
    _source_cases = cases
    rows = [_gen_case_row(c)[:4] for c in cases]
    return rows, f"📋 已加载 {module} {level} 级 {len(cases)} 条，勾选后点「导入」"


def import_fn(source_table):
    """从 source_table 导入勾选的用例到 suite_table"""
    global _source_cases, _suite_cases
    if not _source_cases or source_table is None:
        return None, "❌ 请先加载仓库"

    import pandas as pd
    if isinstance(source_table, pd.DataFrame):
        rows = source_table.values.tolist()
    else:
        rows = list(source_table)

    for i, row in enumerate(rows):
        if i >= len(_source_cases):
            break
        cell0 = row[0]
        checked = isinstance(cell0, bool) and cell0 or (isinstance(cell0, str) and cell0.strip() in ("True", "1", "☑"))
        if checked:
            _suite_cases.append(_source_cases[i])

    display = [_gen_case_row(c)[:4] for c in _suite_cases]
    return display, f"✅ 已导入，测试集共 {len(_suite_cases)} 条"


def clear_suite_fn():
    """清空测试集"""
    global _suite_cases
    _suite_cases = []
    return [], "🗑️ 测试集已清空"


def remove_unchecked_fn(suite_table):
    """移除测试集中未勾选的用例"""
    global _suite_cases
    if not _suite_cases or suite_table is None:
        return None, "❌ 测试集为空"
    import pandas as pd
    if isinstance(suite_table, pd.DataFrame):
        rows = suite_table.values.tolist()
    else:
        rows = list(suite_table)

    keep = []
    for i, row in enumerate(rows):
        if i >= len(_suite_cases):
            break
        cell0 = row[0]
        checked = isinstance(cell0, bool) and cell0 or (isinstance(cell0, str) and cell0.strip() in ("True", "1", "☑"))
        if checked:
            keep.append(_suite_cases[i])
    _suite_cases = keep
    display = [_gen_case_row(c)[:4] for c in _suite_cases]
    return display, f"✅ 已移除未勾选项，测试集共 {len(_suite_cases)} 条"


def add_custom_fn(at_cmd, case_name, expected):
    """添加自定义用例到测试集"""
    global _suite_cases
    if not at_cmd.strip() or not case_name.strip():
        return None, "❌ AT指令和用例名不能为空"
    from models.schemas import TestCase
    c = TestCase(
        excel_file='', sheet_name=at_cmd.strip().split('=')[0].split('?')[0],
        row_id=0, test_group='custom', case_name=case_name.strip(),
        params={'send_data': at_cmd.strip()},
        expected_results=[expected.strip()] if expected.strip() else [r"OK"],
    )
    _suite_cases.append(c)
    display = [_gen_case_row(c)[:4] for c in _suite_cases]
    return display, f"✅ 已添加「{case_name}」，测试集共 {len(_suite_cases)} 条"


def save_suite_fn(suite_name):
    """保存测试集为方案"""
    global _suite_cases
    if not _suite_cases or not suite_name.strip():
        return gr.Dropdown(), "❌ 请输入方案名称且测试集不为空"
    _save_test_set(suite_name.strip(), suite_name.strip())  # store name as marker
    # Save actual case data to a separate file
    import json, os
    path = os.path.join(TEST_SET_DIR, f"{suite_name.strip()}_cases.json")
    data = []
    for c in _suite_cases:
        data.append({
            'sheet': c.sheet_name, 'name': c.case_name,
            'params': {k: str(v) for k, v in c.params.items()} if hasattr(c, 'params') else {},
            'expected': c.expected_results if hasattr(c, 'expected_results') else [],
            'timeout': c.timeout if hasattr(c, 'timeout') else 10,
            'delay': c.delay_after if hasattr(c, 'delay_after') else 0,
        })
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    sets = _list_test_sets()
    choices = [s[0] for s in sets]
    return gr.Dropdown(choices=choices, value=suite_name.strip(), label="加载已有方案"), f"✅ 方案「{suite_name}」已保存（{len(_suite_cases)} 条）"


def load_suite_fn(suite_name):
    """加载方案到测试集"""
    global _suite_cases
    if not suite_name.strip():
        return None, "❌ 请选择方案"
    path = os.path.join(TEST_SET_DIR, f"{suite_name.strip()}_cases.json")
    if not os.path.exists(path):
        # Legacy: try index-based load
        return None, f"❌ 方案文件不存在，请重新保存"
    import json
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    from models.schemas import TestCase
    _suite_cases = []
    for d in data:
        c = TestCase(
            excel_file='', sheet_name=d.get('sheet', ''),
            row_id=0, test_group='suite',
            case_name=d.get('name', ''),
            params=d.get('params', {}),
            expected_results=d.get('expected', []),
            timeout=d.get('timeout', 10),
            delay_after=d.get('delay', 0),
        )
        _suite_cases.append(c)
    display = [_gen_case_row(c)[:4] for c in _suite_cases]
    return display, f"✅ 已加载方案「{suite_name}」（{len(_suite_cases)} 条）"


def list_suites_fn():
    """返回所有方案列表"""
    sets = _list_test_sets()
    choices = [s[0] for s in sets]
    return gr.Dropdown(choices=choices, value=None, label="加载已有方案")


def exec_plan_fn(suite_name):
    """执行测试集中的勾选用例"""
    global _suite_cases
    if not _suite_cases:
        yield "❌ 测试集为空，请先导入用例"
        return

    selected = [c for c in _suite_cases if c.selected]
    if not selected:
        yield "❌ 测试集中没有勾选的用例"
        return
    if not session.serial.is_connected():
        yield "❌ 串口未连接"
        return

    total = len(selected)
    yield f"🚀 执行测试集（{suite_name or '未命名'}），{total} 条\n\n"

    # ... execution loop (same as before but using `selected` list) ...
    from models.database import create_session as db_create_session, end_session, update_session_stats
    from models.schemas import TestResult
    from datetime import datetime
    module = "mixed"
    port = session.serial.port
    baudrate = session.serial.baudrate
    sname = suite_name.strip() or "混合测试"
    session_name = f"{sname}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    db_session_id = db_create_session(
        name=session_name, module=module, port=port, baudrate=baudrate,
        model=session.context.get('model', ''), case_level='P0',
    )
    executor = session.test_agent.executor
    executor.serial = session.serial

    passed, failed = 0, 0
    case_runs = []
    progress_lines = []

    for i, case in enumerate(selected, 1):
        yield f"🔄 **[{i}/{total}]** {case.case_name} ..."
        run = executor.execute_case(case, db_session_id, port=port, baudrate=baudrate)
        case_runs.append(run)
        if run.status == 'PASS':
            passed += 1; icon = "✅"
        elif run.status == 'FAIL':
            failed += 1; icon = "❌"
        else:
            icon = "⚠️"
        at_cmd = (run.at_command or case.sheet_name)[:60]
        actual = (run.actual or '').strip()[:150]
        actual_d = f"\n```\n{actual}\n```" if actual else "\n*(无响应)*"
        line = f"  {icon} **{case.case_name}** ({run.duration_ms}ms)\n    `>>> {at_cmd}`{actual_d}"
        progress_lines.append(line)
        display = [f"**进度:** ✅{passed}  ❌{failed}  /  {total}", "---"]
        display.extend(progress_lines[-12:])
        yield "\n".join(display)

    update_session_stats(db_session_id)
    summary = f"✅ {passed} 通过 | ❌ {failed} 失败 | 共 {total} 条"
    end_session(db_session_id, summary=summary)
    result = TestResult(session_id=db_session_id, session_name=session_name, module=module, case_runs=case_runs)
    session.context['current_result'] = result
    session.context['exec_result'] = result
    _save_exec_result(case_runs, summary, sname)

    defect_hint = "\n\n📌 点「生成缺陷」为失败用例创建缺陷" if failed > 0 else ""
    yield f"## 📊 测试集: {sname}\n\n**{summary}**{defect_hint}"
