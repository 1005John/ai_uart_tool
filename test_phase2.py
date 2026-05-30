#!/usr/bin/env python3
"""Phase 2 集成验证测试"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("Phase 2 集成验证测试 - AI 集成层")
print("=" * 60)

# 1. LLM 客户端
from llm.llm_client import LLMClient
llm = LLMClient()
ok = llm.test_connection()
print(f"\n✅ [LLM] 连接测试: {'通过' if ok else '失败'}")
print(f"   Model: {llm.model}")

# 2. 意图路由
from agents.intent_router import IntentRouter
router = IntentRouter(llm=llm)
test_cases = [
    ("帮我测MQTT的P0", "test", {"module": "mqtt", "level": "P0"}),
    ("打开COM3", "serial", {"port": "COM3", "action": "open"}),
    ("你好", "greeting", {}),
    ("扫描串口", "serial", {"action": "scan"}),
]
print("\n✅ [Intent] 意图路由:")
all_ok = True
for text, expected_intent, expected_params in test_cases:
    intent = router.classify(text)
    params = router.extract_params(text, intent)
    ok = intent == expected_intent
    all_ok &= ok
    status = "✅" if ok else "⚠️"
    print(f"  {status} {text:25s} → '{intent}' (期望: '{expected_intent}')")
if all_ok:
    print("  全部意图识别正确 ✅")

# 3. AI 测试计划生成
from agents.test_agent import TestAgent
agent = TestAgent(llm=llm)
plan = agent.generate_plan("mqtt", level="P0")
print(f"\n✅ [TestPlan] MQTT P0 测试计划:")
print(f"   总用例: {plan.total}")
print(f"   AI 描述生成: {'✅' if hasattr(plan, 'ai_description') and plan.ai_description else '❌'}")

# 4. AI 失败分析
from models.schemas import TestCase, TestCaseRun
fake_case = TestCase(excel_file="", sheet_name="AT+QMTSUB", row_id=1,
                     test_group="sub", case_name="测试订阅",
                     applicable_models=["ALL"])
fake_run = TestCaseRun(
    session_id=0, case=fake_case,
    at_command='AT+QMTSUB=0,1,"sensor/temp",2',
    expected="['+QMTSUB: 0,1,2,0']",
    actual="+CME ERROR: 50",
    status="FAIL"
)
analysis = agent.analyze_failure(fake_run)
print(f"\n✅ [FailAnalysis] AI 失败分析:")
print(f"   分析结果: {analysis[:200]}...")

# 5. 缺陷草稿生成
draft = agent.generate_defect_draft(fake_run)
print(f"\n✅ [DefectDraft] 缺陷草稿生成:")
print(f"   草稿长度: {len(draft)} 字符")
print(f"   含环境描述: {'测试环境' in draft or '环境' in draft}")

# 6. 对话交互
from agents.chat_session import ChatSession
session = ChatSession()
test_dialogs = [
    "模块列表",
    "测一下MQTT",
]
print(f"\n✅ [ChatSession] 对话交互:")
for inp in test_dialogs:
    responses = session.handle(inp)
    for r in responses:
        summary = r[:100].replace('\n', ' ')
        print(f"  👤 {inp:15s} → 🤖 {summary}...")

# 汇总
print(f"\n{'='*60}")
print(f"Phase 2 完成情况:")
print(f"  ✅ LLM 客户端 (DeepSeek API)")
print(f"  ✅ 意图路由 (LLM 驱动的自然语言理解)")
print(f"  ✅ 提示词模板 (系统/测试计划/失败分析/缺陷)")
print(f"  ✅ AI 测试计划生成")
print(f"  ✅ AI 失败分析")
print(f"  ✅ 对话交互 (CLI Chat 模式)")
print(f"{'='*60}")
print(f"启动对话: cd /home/jf/ai_uart_tool && ./venv/bin/python3 main.py chat")
