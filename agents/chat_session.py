#!/usr/bin/env python3
"""对话主界面 - CLI Chat 模式"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm.llm_client import LLMClient
from llm.prompts import SYSTEM_PROMPT
from agents.defect_agent import DefectAgent
from agents.knowledge_agent import KnowledgeAgent
from agents.intent_router import IntentRouter
from agents.test_agent import TestAgent
from engines.serial_engine import SerialEngine
from engines.excel_loader import ExcelTestLoader


class ChatSession:
    """
    对话会话

    管理对话历史、上下文状态、Agent 调用
    """

    def __init__(self):
        self.llm = LLMClient()
        self.router = IntentRouter(llm=self.llm)
        self.loader = ExcelTestLoader()
        self.serial = SerialEngine()
        self.test_agent = TestAgent(llm=self.llm)
        self.defect_agent = DefectAgent(llm=self.llm)
        self.knowledge_agent = KnowledgeAgent(llm=self.llm)

        self.messages = []
        self.context = {
            "port": "",
            "baudrate": 115200,
            "model": "",
            "current_plan": None,
            "current_result": None,
            "awaiting_execution": False,
        }

    def build_system_prompt(self) -> str:
        """构建系统提示词"""
        modules = self.loader.list_modules()
        mod_lines = []
        for m in modules:
            cases = self.loader.load_cases(m['key'])
            mod_lines.append(f"  - {m['key']}: {m['description']} ({len(cases)}条用例)")
        modules_text = "\n".join(mod_lines)

        # 串口状态
        port_status = f"{self.serial.port} @ {self.serial.baudrate}" if self.serial.is_connected() else "未连接"

        return SYSTEM_PROMPT.format(
            modules_list=modules_text,
            port_status=port_status,
        )

    def handle(self, user_input: str) -> list[dict]:
        """
        处理用户输入，返回回复消息列表
        """
        user_input = user_input.strip()
        if not user_input:
            return []

        responses = []

        # 1. 判断意图
        intent = self.router.classify(user_input)
        params = self.router.extract_params(user_input, intent)

        # 2. 根据意图处理
        if intent == "greeting":
            responses.append(self._handle_greeting(user_input))

        elif intent == "help":
            responses.append(self._handle_help())

        elif intent == "serial":
            result = self._handle_serial(user_input, params)
            responses.extend(result)

        elif intent == "test":
            result = self._handle_test(user_input, params)
            responses.extend(result)

        elif intent == "knowledge":
            responses.append(self._handle_knowledge(user_input, params))

        elif intent == "defect":
            responses.append(self._handle_defect(user_input))

        else:
            # 交给 LLM 自由对话
            responses.append(self._handle_fallback(user_input))

        return responses

    def _handle_greeting(self, text: str) -> str:
        return ("你好！我是 AI Native UART Tool 助手 🛠️\n\n"
                "我可以帮你:\n"
                "  • 扫描/打开串口: `扫描端口` `打开COM3`\n"
                "  • 执行测试: `测MQTT的P0` `跑一下TCP`\n"
                "  • 分析结果: `为什么FAIL了`\n"
                "  • 缺陷管理: `创建缺陷`\n\n"
                "输入 `help` 查看更多帮助")

    def _handle_help(self) -> str:
        return (
            "**可用命令:**\n\n"
            "**串口操作:**\n"
            "  `扫描端口` - 列出所有串口\n"
            "  `打开COM3` - 打开指定串口\n"
            "  `打开COM3 115200` - 指定波特率打开\n"
            "  `关闭串口` - 断开串口\n\n"
            "**测试操作:**\n"
            "  `测MQTT` - 查看MQTT测试计划\n"
            "  `测MQTT的P0` - 只看冒烟测试\n"
            "  `开始执行` - 执行当前测试计划\n"
            "  `跑一下TCP` - 直接执行TCP测试\n\n"
            "**结果分析:**\n"
            "  `为什么FAIL` - 分析失败原因\n"
            "  `缺陷 1` - 为第1条FAIL生成缺陷\n\n"
            "**知识查询:**\n"
            "  `模块列表` - 列出所有测试模块\n"
            "  `AT+QMTOPEN是什么` - 查询AT指令\n"
        )

    def _handle_serial(self, text: str, params: dict) -> list:
        responses = []
        action = params.get('action', '')

        if action == 'scan' or not action:
            ports = self.serial.list_ports()
            if ports:
                lines = ["可用串口:"]
                for p in ports:
                    desc = p['description'] or 'n/a'
                    lines.append(f"  {p['port']:12s} {desc}")
                responses.append("\n".join(lines))
            else:
                responses.append("未发现可用串口")

        elif action == 'open':
            port = params.get('port', '')
            baudrate = params.get('baudrate', 115200)
            if not port:
                # 尝试自动选择
                ports = self.serial.list_ports()
                if ports:
                    port = ports[0]['port']
                else:
                    responses.append("未找到可用串口，请指定端口号")
                    return responses

            ok = self.serial.open(port, baudrate)
            if ok:
                self.context['port'] = port
                self.context['baudrate'] = baudrate
                responses.append(f"✅ 已打开 {port} @ {baudrate}")
            else:
                responses.append(f"❌ 打开 {port} 失败，请检查串口是否被占用")

        elif action == 'close':
            self.serial.close()
            responses.append("🔒 串口已关闭")

        return responses

    def _handle_test(self, text: str, params: dict) -> list:
        responses = []

        # 检查是否要执行
        if "开始" in text or "执行" in text or "跑" in text:
            if self.context['current_plan']:
                # 执行当前计划
                responses.append("🚀 开始执行测试...")
                result = self.test_agent.execute_plan(
                    self.context['current_plan'],
                    port=self.context.get('port', ''),
                    baudrate=self.context.get('baudrate', 115200),
                )
                self.context['current_result'] = result
                responses.append(self.test_agent.format_result_summary(result))
            else:
                # 直接执行
                module = params.get('module', '')
                level = params.get('level', 'P0')
                if module:
                    plan = self.test_agent.generate_plan(module, level=level)
                    if plan:
                        self.context['current_plan'] = plan
                        responses.append(f"📋 已生成 {module} 测试计划:")
                        responses.append(self.test_agent.describe_plan(plan))
                        responses.append("\n输入 `开始执行` 运行测试")
                    else:
                        responses.append(f"❌ 模块 {module} 没有可用的测试用例")
                else:
                    responses.append("请指定要测试的模块，例如: `测MQTT的P0`")
            return responses

        # 查看测试计划
        module = params.get('module', '')

        # 特殊处理：模块列表
        if "模块" in text and ("列表" in text or "所有" in text or "有哪些" in text):
            modules = self.loader.list_modules()
            lines = ["**可用测试模块:**\n"]
            for m in modules:
                cases = self.loader.load_cases(m['key'])
                lines.append(f"  • {m['key']:15s} - {m['description']:20s} ({len(cases):3d}条用例)")
            responses.append("\n".join(lines))
            return responses

        if not module:
            responses.append("请指定模块名，例如: `测MQTT` `测TCP的P1`")
            responses.append("\n可用模块:\n" + self.router.format_modules_help())
            return responses

        level = params.get('level', 'P0')
        model = params.get('model', self.context.get('model', ''))

        plan = self.test_agent.generate_plan(module, model=model, level=level)
        if plan:
            self.context['current_plan'] = plan
            responses.append(self.test_agent.describe_plan(plan))
        else:
            responses.append(f"❌ 模块 {module} 没有可用的测试用例")
            responses.append("试试:\n" + self.router.format_modules_help())

        return responses

    def _handle_knowledge(self, text: str, params: dict) -> str:
        """知识查询"""
        # 特殊处理：模块列表
        if "模块" in text and ("列表" in text or "所有" in text or "有哪些" in text):
            modules = self.loader.list_modules()
            lines = ["**可用测试模块:**\n"]
            for m in modules:
                cases = self.loader.load_cases(m['key'])
                lines.append(f"  • {m['key']:15s} - {m['description']:20s} ({len(cases):3d}条用例)")
            return "\n".join(lines)

        # 使用知识图谱Agent查询
        return self.knowledge_agent.query(text)

    def _handle_defect(self, text: str) -> str:
        """缺陷管理"""
        text_lower = text.lower()

        # 查看本地缺陷列表
        if "列表" in text or "查看" in text or "所有" in text:
            defects = self.defect_agent.store.list_defects()
            return self.defect_agent.store.format_list(defects)

        # 查看缺陷详情
        import re
        detail_match = re.search(r'详情\s*(\d+)', text)
        if detail_match:
            did = int(detail_match.group(1))
            return self.defect_agent.format_defect_detail(did)

        # 提交到灵畿
        if "提交" in text or "灵畿" in text:
            # 检查登录
            login = self.defect_agent.sync.check_login()
            if not login['ok']:
                return ("❌ 灵畿平台未登录，请先登录\n"
                        "请通过 Chrome 插件获取 token，然后输入:\n"
                        "`登录灵畿 <你的token>`")

            # 提取缺陷ID
            submit_match = re.search(r'提交\s*(\d+)', text)
            if submit_match:
                did = int(submit_match.group(1))
                result = self.defect_agent.submit_to_lingji(did)
                return result['message']
            else:
                # 提交所有本地缺陷
                defects = self.defect_agent.store.list_defects(status='local')
                if not defects:
                    return "没有待提交的本地缺陷"
                results = self.defect_agent.submit_batch([d['id'] for d in defects])
                ok = sum(1 for r in results if r['ok'])
                fail = sum(1 for r in results if not r['ok'])
                return f"提交结果: ✅ {ok} 成功, ❌ {fail} 失败"

        # 登录灵畿
        if "登录" in text and "灵畿" in text:
            token_match = re.search(r'登录灵畿\s+(.+)', text)
            if token_match:
                token = token_match.group(1).strip()
                result = self.defect_agent.sync.login(token)
                return result['message']
            return "请提供 token，格式: `登录灵畿 <你的token>`"

        # 检查同步
        if "同步" in text or "校验" in text:
            issues = self.defect_agent.sync_check()
            if not issues:
                return "✅ 所有缺陷同步正常"
            lines = ["⚠️ 发现同步问题:"]
            for issue in issues:
                lines.append(f"  • {issue['message']}")
            return "\n".join(lines)

        # 为测试结果中的FAIL创建缺陷
        result = self.context.get('current_result')
        if result and result.failures:
            match = re.search(r'缺陷\s*(\d+)', text)
            if match:
                idx = int(match.group(1)) - 1
                if 0 <= idx < len(result.failures):
                    failure = result.failures[idx]
                    # 确保有AI分析
                    if not failure.ai_analysis:
                        failure.ai_analysis = self.test_agent.analyze_failure(failure)
                    # 创建本地缺陷
                    desc = self.defect_agent.generate_description(failure)
                    r = self.defect_agent.create_local(failure, description=desc)
                    if r['ok']:
                        detail = self.defect_agent.format_defect_detail(r['defect_id'])
                        return f"{r['message']}\n\n{detail}"
                    return r['message']

            # 为所有FAIL创建缺陷
            if "全部" in text or "所有" in text:
                results = []
                for i, f in enumerate(result.failures, 1):
                    if not f.ai_analysis:
                        f.ai_analysis = self.test_agent.analyze_failure(f)
                    desc = self.defect_agent.generate_description(f)
                    r = self.defect_agent.create_local(f, description=desc)
                    results.append(r)
                ok = sum(1 for r in results if r['ok'])
                return f"已为 {ok}/{len(result.failures)} 条FAIL创建本地缺陷\n输入`缺陷列表`查看"

            return ("可用的缺陷操作:\n"
                    "  `缺陷 N` - 为第N条FAIL创建本地缺陷\n"
                    "  `全部创建缺陷` - 为所有FAIL创建\n"
                    "  `缺陷列表` - 查看本地缺陷\n"
                    "  `提交 N` - 提交第N个缺陷到灵畿\n"
                    "  `登录灵畿 <token>` - 登录灵畿平台\n"
                    "  `同步校验` - 检查同步状态")

        # 没有测试结果，查看本地缺陷
        defects = self.defect_agent.store.list_defects()
        if defects:
            return self.defect_agent.store.format_list(defects)
        return "当前没有缺陷，请先执行测试产生FAIL结果"

    def _handle_fallback(self, text: str) -> str:
        """交给 LLM 自由对话"""
        # 添加系统提示和上下文
        sys_prompt = self.build_system_prompt()
        messages = [
            {"role": "system", "content": sys_prompt},
            *self.messages[-10:],  # 最近10条历史
            {"role": "user", "content": text},
        ]
        resp = self.llm.chat(messages, temperature=0.5, max_tokens=1024)
        return resp or "抱歉，我没有理解你的意思。"


def main():
    """主交互循环"""
    print("=" * 50)
    print("  AI Native UART Tool - 对话模式")
    print("  输入 `exit` 退出, `help` 查看帮助")
    print("=" * 50)

    session = ChatSession()

    while True:
        try:
            user_input = input("\n👤 > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n再见！")
            break

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit", "退出"):
            if session.serial.is_connected():
                session.serial.close()
            print("再见！")
            break

        # 处理输入
        responses = session.handle(user_input)

        # 输出回复
        for resp in responses:
            print(f"\n🤖 > {resp}")

        # 保存对话历史
        session.messages.append({"role": "user", "content": user_input})
        for resp in responses:
            session.messages.append({"role": "assistant", "content": resp})

        # 最多保留50条历史
        if len(session.messages) > 50:
            session.messages = session.messages[-50:]


if __name__ == "__main__":
    main()
