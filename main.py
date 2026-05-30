#!/usr/bin/env python3
"""
AI Native UART Tool - 主入口

Usage:
    python main.py scan                  # 扫描串口
    python main.py modules               # 列出所有测试模块
    python main.py plan <module>         # 预览测试计划
    python main.py quick <module> [port] # 快速测试（需要串口）
    python main.py chat                  # AI 对话模式（推荐）
    
AI 对话模式支持:
    • 串口操作:  扫描端口 / 打开COM3 / 关闭串口
    • 测试执行:  测MQTT的P0 / 跑一下TCP / 开始执行
    • 结果分析:  为什么FAIL了 / 缺陷 1 / 全部创建缺陷
    • 缺陷管理:  缺陷列表 / 提交 1 / 登录灵畿 <token>
    • 知识查询:  模块列表 / AT+QMTOPEN是什么
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import init_db, get_db_path
from engines.serial_engine import SerialEngine
from engines.excel_loader import ExcelTestLoader
from engines.test_executor import TestExecutor
from models.schemas import TestPlan


def cmd_scan():
    """扫描可用串口"""
    print(SerialEngine.list_ports_text())


def cmd_modules():
    """列出所有测试模块"""
    loader = ExcelTestLoader()
    modules = loader.list_modules()
    total = 0

    print(f"{'模块名':<20} {'说明':<30} {'用例数':<8}")
    print("-" * 60)
    for m in modules:
        cases = loader.load_cases(m['key'])
        count = len(cases)
        total += count
        print(f"{m['key']:<20} {m['description']:<30} {count:<8}")
    print("-" * 60)
    print(f"{'总计':<20} {'':<30} {total:<8}")


def cmd_plan(module: str, model: str = "", level: str = "P0"):
    """预览指定模块的测试计划"""
    loader = ExcelTestLoader()
    sheets = loader.load_sheets(module)
    print(f"\n📋 模块: {module}")
    print(f"   Sheet: {sheets}")

    for level_filter in ["P0", "P1", "P2"]:
        cases = loader.load_cases(module, case_level=[level_filter], model=model)
        if cases:
            print(f"\n   [{level_filter}] {len(cases)} 条用例:")
            for c in cases:
                print(f"     ☐ {c.case_name}")
                for k, v in list(c.params.items())[:3]:
                    if v is not None and str(v).strip():
                        print(f"         {k}={str(v)[:50]}")

    # 显示筛选后的总览
    selected = loader.load_cases(module, case_level=[level], model=model)
    plan = TestPlan(module=module, cases=selected, model=model)
    print(f"\n   📊 当前选择: [{level}] {plan.total} 条, 预计 {plan.estimated_time}")


def cmd_quick(module: str, port: str = "", model: str = ""):
    """快速测试（需要物理串口连接模组）"""
    executor = TestExecutor()
    loader = executor.loader

    try:
        result = executor.quick_test(module, port=port, model=model)
        if result:
            print(result.format_summary())
    except RuntimeError as e:
        print(f"❌ 错误: {e}")
        print("请先连接串口或用 python main.py scan 查看可用端口")


def main():
    init_db()
    print(f"🔧 AI Native UART Tool | 数据库: {get_db_path()}\n")

    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]

    if cmd == "scan":
        cmd_scan()
    elif cmd == "modules":
        cmd_modules()
    elif cmd == "plan" and len(sys.argv) >= 3:
        module = sys.argv[2]
        model = sys.argv[3] if len(sys.argv) > 3 else ""
        level = sys.argv[4] if len(sys.argv) > 4 else "P0"
        cmd_plan(module, model, level)
    elif cmd == "quick" and len(sys.argv) >= 3:
        module = sys.argv[2]
        port = sys.argv[3] if len(sys.argv) > 3 else ""
        model = sys.argv[4] if len(sys.argv) > 4 else ""
        cmd_quick(module, port, model)
    elif cmd == "chat":
        from agents.chat_session import main as chat_main
        chat_main()
    else:
        print(f"未知命令: {cmd}")
        print(__doc__)


if __name__ == "__main__":
    main()
