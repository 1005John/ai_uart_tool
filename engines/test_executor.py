#!/usr/bin/env python3
"""测试执行引擎 - 整合串口引擎 + Excel加载器 + 结果匹配器"""
import time
from typing import Optional, Callable
from datetime import datetime

from models.schemas import TestCase, TestPlan, TestCaseRun, TestResult, ExecutableCase
from models.database import (
    init_db, create_session, end_session, update_session_stats, add_case_run
)
from engines.serial_engine import SerialEngine
from engines.excel_loader import ExcelTestLoader, evaluate_param
from engines.result_matcher import ResultMatcher


class TestExecutor:
    """
    测试执行引擎

    功能:
    - 执行单个测试用例（单条AT指令）
    - 执行测试计划（批量）
    - 回调通知进度
    - 自动记录到数据库
    """

    def __init__(self, serial_engine: SerialEngine = None, excel_loader: ExcelTestLoader = None):
        self.serial = serial_engine or SerialEngine()
        self.loader = excel_loader or ExcelTestLoader()
        self._progress_callback: Optional[Callable[[TestCaseRun], None]] = None
        init_db()

    def set_progress_callback(self, callback: Callable[[TestCaseRun], None]):
        """设置进度回调（UI更新用）"""
        self._progress_callback = callback

    # ── 单用例执行 ──

    def execute_case(self, case: TestCase, session_id: int,
                     port: str = "", baudrate: int = 115200) -> TestCaseRun:
        """
        执行单个测试用例

        流程:
        1. 调用 ExcelLoader 将 TestCase 转为实际 AT 指令
        2. 发送到串口
        3. 等待响应
        4. 匹配预期结果
        5. 记录到数据库
        """
        run = TestCaseRun(
            session_id=session_id,
            case=case,
        )

        try:
            # 1. 生成 AT 指令
            exec_case = self._generate_command(case)
            run.at_command = exec_case.at_command

            # 2. 发送前预处理
            start = time.time()

            # 3. 发送指令
            self.serial.send_at(exec_case.at_command)

            # 4. 等待响应
            result = self.serial.wait_for(
                exec_case.expected_patterns,
                timeout=exec_case.timeout
            )

            run.duration_ms = result['duration_ms']
            run.actual = result['response']
            run.expected = str(exec_case.expected_patterns)

            # 5. 判定结果
            if not result['success']:
                # 超时
                run.status = 'FAIL'
                run.fail_reason = f"超时({exec_case.timeout}s)无响应"
                # 检查是否有错误返回
                err = ResultMatcher.has_error(result['response'])
                if err:
                    run.fail_reason += f"，检测到错误: {err}"
            else:
                # 匹配成功
                match_result = ResultMatcher.match(
                    result['response'],
                    exec_case.expected_patterns
                )
                if match_result['matched']:
                    run.status = 'PASS'
                else:
                    run.status = 'FAIL'
                    run.fail_reason = f"返回内容不匹配: {result['response'][:100]}... 预期: {exec_case.expected_patterns}"

            # 6. 延迟（用于连续指令间隔）
            if exec_case.delay_after > 0:
                time.sleep(exec_case.delay_after / 1000.0)

        except Exception as e:
            run.status = 'ERROR'
            run.fail_reason = f"执行异常: {e}"

        # 7. 记录到数据库
        add_case_run(
            session_id=session_id,
            sheet_name=case.sheet_name,
            excel_row_id=case.row_id,
            test_group=case.test_group,
            case_name=case.case_name,
            case_level=case.case_level,
            applicable_models=str(case.applicable_models),
            at_command=run.at_command,
            send_data=run.at_command,
            expected_result=run.expected,
            actual_result=run.actual,
            duration_ms=run.duration_ms,
            status=run.status,
            fail_reason=run.fail_reason,
            ai_analysis=run.ai_analysis,
        )

        # 8. 回调通知
        if self._progress_callback:
            self._progress_callback(run)

        return run

    # ── 批量执行 ──

    def execute_plan(self, plan: TestPlan) -> TestResult:
        """
        执行完整测试计划

        Args:
            plan: 测试计划

        Returns: 测试结果
        """
        # 1. 打开串口（如未打开）
        if not self.serial.is_connected():
            if plan.port:
                ok = self.serial.open(plan.port, plan.baudrate)
                if not ok:
                    raise RuntimeError(f"无法打开串口 {plan.port}")

        # 2. 创建数据库会话
        session_name = f"{plan.module}测试_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        model_str = plan.model or "未知"
        session_id = create_session(
            name=session_name,
            module=plan.module,
            port=plan.port,
            baudrate=plan.baudrate,
            model=model_str,
            case_level=",".join(sorted(set(c.case_level for c in plan.cases if c.selected))),
        )

        case_runs = []
        selected = [c for c in plan.cases if c.selected]
        total = len(selected)

        print(f"\n{'='*60}")
        print(f"开始测试: {session_name}")
        print(f"模块: {plan.module} | 用例数: {total} | 模组: {model_str}")
        print(f"{'='*60}\n")

        # 3. 逐条执行
        for i, case in enumerate(selected, 1):
            case_info = f"[{i}/{total}] [{case.case_level}] {case.case_name}"
            print(f"\n>>> {case_info}")

            run = self.execute_case(case, session_id,
                                    port=plan.port, baudrate=plan.baudrate)

            # 状态图标
            icon = "✅" if run.status == 'PASS' else "❌" if run.status == 'FAIL' else "⚠️"
            print(f"{icon} {run.status} ({run.duration_ms}ms)")
            if run.fail_reason:
                print(f"   原因: {run.fail_reason}")

            case_runs.append(run)

            # 简易进度
            passed = len([r for r in case_runs if r.status == 'PASS'])
            failed = len([r for r in case_runs if r.status == 'FAIL'])
            print(f"   进度: {passed}✅ {failed}❌ / {i}")

        # 4. 更新会话统计
        update_session_stats(session_id)

        # 5. 汇总
        result = TestResult(
            session_id=session_id,
            session_name=session_name,
            module=plan.module,
            case_runs=case_runs,
        )

        summary = result.format_summary()
        print(f"\n{summary}")

        end_session(session_id, summary=summary)

        return result

    # ── 指令生成 ──

    def _generate_command(self, case: TestCase) -> ExecutableCase:
        """
        将 TestCase 转为可执行 AT 指令

        依据 sheet_name(AT指令名) 和 params 生成完整 AT 指令
        """
        # 从 sheet_name 提取指令前缀（如 "AT+MQTTSUB"）
        cmd_prefix = case.sheet_name  # 如 "AT+MQTTSUB"

        # 建立参数映射表
        param_mapping = self._build_param_mapping(cmd_prefix, case.params)

        return ExecutableCase(
            original_case=case,
            at_command=param_mapping.get('send_data', cmd_prefix),
            expected_patterns=case.expected_results or [r"OK"],
            timeout=case.timeout,
            delay_after=case.delay_after,
        )

    def _build_param_mapping(self, cmd_prefix: str, params: dict) -> dict:
        """
        根据指令前缀和参数字典，生成完整 AT 指令

        优先级:
        1. 如果 params 中有 send_data → 直接使用（Excel已提供）
        2. 调用 test_at_link/common/command_*.py 的 set_* 函数生成
        3. 否则根据参数拼接
        """
        # 如果 Excel 中已有 send_data
        send_data = params.get('send_data')
        if send_data:
            send_str = evaluate_param(str(send_data))
            return {'send_data': send_str}

        # 尝试从 test_at_link 的命令模块获取真实 AT 指令
        real_cmd = self._call_command_module(cmd_prefix, params)
        if real_cmd:
            return {'send_data': real_cmd}

        # 降级：根据参数拼接
        # 把 params 按 key=value 拼接
        param_parts = []
        for k, v in params.items():
            if v is not None and str(v).strip():
                val_str = str(v)
                # 如果是字符串且包含特殊字符，加引号
                if isinstance(v, str) and (',' in v or ' ' in v):
                    val_str = f'"{v}"'
                param_parts.append(f"{k}={val_str}")
        if param_parts:
            return {'send_data': f"{cmd_prefix} {' '.join(param_parts)}"}
        return {'send_data': cmd_prefix}

    def _call_command_module(self, cmd_prefix: str, params: dict) -> str | None:
        """
        调用 test_at_link 的命令模块生成真实 AT 指令

        处理参数名别名（Excel 字段名 vs 函数参数名）
        """
        cmd_name = cmd_prefix.replace("AT+", "").lower().strip()
        if not cmd_name:
            return None

        # 命令模块映射（sheet_prefix → module_name）
        module_map = {
            'mqttcfg': 'command_mqtt',
            'mqtt':    'command_mqtt',
            'mip':     'command_tcp',
            'mhttpcfg': 'command_http',
            'mhttp':   'command_http',
            'mhttps':  'command_http',
            'csms':    'command_sms',
            'cmgf':    'command_sms',
            'csca':    'command_sms',
            'csdh':    'command_sms',
            'cnmi':    'command_sms',
            'mgnsscfg': 'command_gnss',
            'mgnss':   'command_gnss',
            'cgdcont': 'command_packet_domain',
            'cgatt':   'command_packet_domain',
            'cgact':   'command_packet_domain',
            'cgpaddr': 'command_packet_domain',
            'mfwcfg':  'command_fota',
            'mfwdload':'command_fota',
            'mlpmcfg': 'command_pm',
            'madc':    'command_adc',
            'mgpio':   'command_gpio',
            'mled':    'command_mled',
            'mdns':    'command_dns',
            'mntp':    'command_ntp',
            'mping':   'command_mping',
            'mcsearfcn':'command_extended',
            'mlockfreq':'command_extended',
            'clck':    'command_networkservice',
            'mag':     'command_gnss',
            'mdg':     'command_gnss',
        }
        module_name = None
        # 先精确匹配再模糊匹配（避免 mip 匹配到 mipcfg 时先被 mip 吃掉）
        sorted_prefixes = sorted(module_map.keys(), key=len, reverse=True)
        for prefix in sorted_prefixes:
            if cmd_name.startswith(prefix):
                module_name = module_map[prefix]
                break
        if not module_name:
            return None

        # 参数名别名表（Excel 字段名 → 函数参数名）
        param_aliases = {
            'mqtthost': 'host',
            'mqttport': 'port',
            'send_message': 'message',
            'sub_topics': 'topics',
            'unsub_topics': 'topics',
        }

        # 转换参数名，并解析字符串为 Python 对象
        import ast
        mapped_params = {}
        for k, v in params.items():
            target_key = param_aliases.get(k, k)
            # Excel 中的列表/字典存为字符串，需要解析
            if isinstance(v, str):
                try:
                    parsed = ast.literal_eval(v)
                    mapped_params[target_key] = parsed
                except (ValueError, SyntaxError):
                    mapped_params[target_key] = v
            else:
                mapped_params[target_key] = v

        # 函数名：AT+MQTTCFG + cfg_type=cid → set_mqttcfg_cid
        if cmd_name == 'mqttcfg' and 'cfg_type' in mapped_params:
            func_name = f"set_mqttcfg_{mapped_params['cfg_type']}"
        elif cmd_name.startswith('mhttprequest_') or cmd_name.startswith('mhttpsrequest_'):
            func_name = 'set_' + cmd_name.split('_')[0]
        elif cmd_name.startswith('mlpmcfg_'):
            # AT+MLPMCFG_1111 → set_mlpmcfg (后缀作为 cmd 参数)
            suffix = cmd_name[len('mlpmcfg_'):]
            func_name = 'set_mlpmcfg'
            # 添加 cmd 参数，Excel 里没有的话用后缀
            if 'cmd' not in mapped_params:
                mapped_params['cmd'] = suffix
        elif cmd_name == 'mqttpub':
            func_name = f"set_{cmd_name}"
        else:
            func_name = f"set_{cmd_name}"

        try:
            import importlib
            mod_path = f"test_at_link.common.{module_name}"
            mod = importlib.import_module(mod_path)
            func = getattr(mod, func_name, None)
            if not func:
                return None

            # 提取函数能接受的参数
            import inspect
            sig = inspect.signature(func)
            filtered_params = {}
            for pname in sig.parameters:
                if pname in mapped_params:
                    filtered_params[pname] = mapped_params[pname]

            result = func(**filtered_params)
            if isinstance(result, dict) and result.get('send_data'):
                return result['send_data']
        except Exception:
            pass

        return None

    # ── 快捷方法 ──

    def quick_test(self, module: str, port: str = "", baudrate: int = 115200,
                   model: str = "", level: str = "P0") -> TestResult:
        """
        快速测试：按模块+级别执行

        Args:
            module: 模块名
            port: 串口号
            baudrate: 波特率
            model: 模组型号
            level: 用例级别
        """
        cases = self.loader.load_cases(module, case_level=[level], model=model)
        if not cases:
            print(f"❌ 模块 {module} 没有级别 {level} 的测试用例")
            return None

        plan = TestPlan(
            module=module,
            cases=cases,
            model=model,
            port=port,
            baudrate=baudrate,
        )
        return self.execute_plan(plan)


if __name__ == "__main__":
    # 测试: 加载 MQTT 模块 P0 级用例
    loader = ExcelTestLoader()
    executor = TestExecutor(excel_loader=loader)

    print("=== 可用模块 ===")
    for m in loader.list_modules():
        print(f"  {m['key']}: {m['description']}")

    print("\n=== MQTT P0 级用例预览 ===")
    cases = loader.load_cases("mqtt", case_level=["P0"])
    print(loader.cases_to_text(cases))
    print(f"\n共 {len(cases)} 条 P0 用例")
